from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .cart import Cart
from home.models import Product
from accounts.models import Address
from .forms import CardAddForm, CouponApplyForm, OrderAddressForm
from .models import Order, OrderItem, Coupon
from django.conf import settings
import requests
import json
import datetime
from django.contrib import messages

class CartView(View):
    def get(self, request):
        cart = Cart(request)
        return render(request, template_name='orders/cart.html', context={'cart': cart})

class CartAddView(PermissionRequiredMixin, View):
    permission_required = 'orders.add_order'  # برای دسترسی یا محدود کردن کاربر برای یک سری کارها

    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CardAddForm(request.POST)
        if form.is_valid():
            cart.add(product, form.cleaned_data['quantity'])
        return redirect('orders:cart')


class CartRemoveView(View):
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        return redirect('orders:cart')


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user, phone_number=request.user.phone_number)
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
        cart.clear()
        return redirect('orders:order_detail', order.id)

class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        coupon_form = CouponApplyForm()
        address_form = OrderAddressForm(user=request.user)
        addresses = request.user.addresses.all()

        return render(request, "orders/order.html", {
            "order": order,
            "form": coupon_form,
            "address_form": address_form,
            "addresses": addresses,
        })

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # اگر فرم کوپن ارسال شد
        if "code" in request.POST:
            coupon_form = CouponApplyForm(request.POST)
            if coupon_form.is_valid():
                code = coupon_form.cleaned_data['code']
                messages.success(request, f"Coupon {code} applied.")
            return redirect("orders:order_detail", order.id)

        # اگر فرم انتخاب/اضافه کردن آدرس ارسال شد
        address_form = OrderAddressForm(user=request.user, data=request.POST)
        if address_form.is_valid():
            cd = address_form.cleaned_data
            edit_id = cd.get("edit_id")

            if edit_id:  # آدرس موجود
                addr = get_object_or_404(Address, id=edit_id, user=request.user)
            else:  # آدرس جدید
                # اگر کاربر بخواهد آدرس جدید اضافه کند، ریدایرکت به صفحه مدیریت آدرس‌ها
                return redirect("accounts:manage_addresses")

            order.address = addr
            order.save()
            messages.success(request, "آدرس انتخاب شد. اکنون می‌توانید پرداخت را انجام دهید.")
            return redirect("orders:order_detail", order.id)

        # اگر فرم آدرس معتبر نبود دوباره صفحه را نمایش بده
        coupon_form = CouponApplyForm()
        addresses = request.user.addresses.all()
        return render(request, "orders/order.html", {
            "order": order,
            "form": coupon_form,
            "address_form": address_form,
            "addresses": addresses,
        })

class OrderPayView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        request.session['order_pay'] = {
            'order_id': order.id,
        }
        amount = order.get_total_price()
        description = "توضیح پرداخت"
        email = request.user.email
        mobile = request.user.phone_number
        merchant_id = settings.MERCHANT
        callback_url = settings.CALLBACKURL
        sandbox = settings.SANDBOX

        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        data = {
            "merchant_id": merchant_id,
            "amount": amount,
            "description": description,
            "callback_url": callback_url,
            "metadata": {"mobile": mobile, "email": email}
        }

        url = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json' if sandbox else 'https://api.zarinpal.com/pg/v4/payment/request.json'

        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('data') and res_data['data'].get('code') == 100:
                authority = res_data['data']['authority']
                gateway_url = f"https://sandbox.zarinpal.com/pg/StartPay/{authority}" if sandbox else f"https://www.zarinpal.com/pg/StartPay/{authority}"
                return redirect(gateway_url)
            else:
                return render(request, 'orders/payment_result.html', {'status': 'failed',
                                                                      'error_code': res_data.get('errors')})
        else:
            return render(request, 'orders/payment_result.html', {'status': 'failed',
                                                                  'error_code': 'خطا در ارتباط با زرین پال'})

class OrderVerifyView(LoginRequiredMixin, View):
    def get(self, request):
        order_id = request.session['order_pay']['order_id']
        order = Order.objects.get(id=int(order_id))
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        if status == 'OK':
            merchant_id = settings.MERCHANT
            amount = order.get_total_price()
            sandbox = settings.SANDBOX

            headers = {'accept': 'application/json', 'content-type': 'application/json'}
            data = {
                "merchant_id": merchant_id,
                "amount": amount,
                "authority": authority
            }

            url = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json' if sandbox else 'https://api.zarinpal.com/pg/v4/payment/verify.json'

            response = requests.post(url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('data') and res_data['data'].get('code') == 100:
                    order.paid = True
                    order.save()
                    ref_id = res_data['data']['ref_id']
                    return render(request, 'orders/payment_result.html', {'status': 'success',
                                                                          'ref_id': ref_id})
                else:
                    return render(request, 'orders/payment_result.html', {'status': 'failed',
                                                                          'error_code': res_data.get('errors')})
            else:
                return render(request, 'orders/payment_result.html', {'status': 'failed',
                                                                      'error_code': 'خطا در ارتباط با زرین پال'})
        else:
            return render(request, 'orders/payment_result.html', {'status': 'canceled'})


class CouponApplyView(LoginRequiredMixin, View):
    form_class = CouponApplyForm

    def post(self, request, order_id):
        now = datetime.datetime.now()
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                coupon = Coupon.objects.get(code__exact=code, valid_from__lte=now, valid_to__gte=now, active=True)
            except Coupon.DoesNotExist:
                messages.error(request, message='this coupon does not exist', extra_tags='danger')
                return redirect('orders:order_detail', order_id)
            order = Order.objects.get(id=order_id)
            order.discount = coupon.discount
            order.save()
        return redirect('orders:order_detail', order_id)
