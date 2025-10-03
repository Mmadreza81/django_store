from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.views import View
from .forms import UserRegisterationForm, VerifyCodeForm, UserLoginForm, EditUserForm, AddressForm
from .models import User, OtpCode, Profile, Address
import random
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from types import SimpleNamespace
from django.contrib.auth import views as auth_view
from django.urls import reverse_lazy
from accounts.tasks import remove_expired_otp_codes

class UserRegisterView(View):
    form_class = UserRegisterationForm
    templates_name = 'accounts/register.html'

    def get(self, request):
        form = self.form_class
        return render(request, template_name=self.templates_name, context={'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000, 9999)
            OtpCode.objects.update_or_create(email=form.cleaned_data['email'], defaults={'code': random_code})
            request.session['user_registeration_info'] = {
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['email'],
                'username': form.cleaned_data['username'],
                'password': form.cleaned_data['password2'],
            }
            send_mail(subject='کد فعال سازی حساب', message=f"کد فعال سازی شما: {random_code}",
                      from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[form.cleaned_data['email']], fail_silently=False)
            messages.success(request, message='کد به ایمیل شما فرستاده شد', extra_tags='success')
            return redirect('accounts:verify_code')
        return render(request, template_name=self.templates_name, context={'form': form})


class UserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class
        return render(request, template_name='accounts/verify.html', context={'form': form})

    def post(self, request):
        user_session = request.session['user_registeration_info']
        try:
            code_instance = OtpCode.objects.get(email=user_session['email'])
        except OtpCode.DoesNotExist:
            # یعنی کد یا منقضی شده یا هیچ‌وقت وجود نداشته
            messages.error(request, 'کد منقضی شده است. لطفا روی ارسال مجدد کد بزنید', extra_tags='danger')
            return redirect('accounts:verify_code')

        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['code'] == code_instance.code:
                # ایجاد کاربر
                User.objects.create_user(
                    phone_number=user_session['phone_number'],
                    email=user_session['email'],
                    username=user_session['username'],
                    password=user_session['password']
                )

                # لاگین کردن کاربر
                user = authenticate(request, username=user_session['email'], password=user_session['password'])
                if user is not None:
                    login(request, user)
                    code_instance.delete()
                    messages.success(request, message='ثبت نام با موفقیت انجام شد', extra_tags='success')
                    return redirect('home:home')
                else:
                    return redirect('accounts:user_register')
            else:
                messages.error(request, message='کد وارد شده اشتباه است', extra_tags='danger')
                return redirect('accounts:verify_code')

        return redirect('accounts:verify_code')


class ResendOtpCodeView(View):
    def get(self, request):
        user_session = request.session.get('user_registeration_info')
        if not user_session:
            messages.error(request, 'اطلاعات ثبت نام یافت نشد', extra_tags='danger')
            return redirect('accounts:register')
        try:
            code_instance = OtpCode.objects.get(email=user_session['email'])
            if not code_instance.can_resend():
                messages.error(request, 'لطفا 30 ثانیه صبر کنید و دوباره تلاش کنید', extra_tags='danger')
                return redirect('accounts:verify_code')
            code_instance.delete()
        except:
            pass
        random_code = random.randint(1000, 9999)
        OtpCode.objects.create(email=user_session['email'], code=random_code)
        send_mail(subject='کد جدید فعال سازی', message=f"کد فعال سازی شما: {random_code}",
                  from_email=settings.EMAIL_HOST_USER, recipient_list=[user_session['email']], fail_silently=False)
        messages.success(request, 'کد جدید برای شما ارسال شد', extra_tags='success')
        return redirect('accounts:verify_code')


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def __init__(self):
        super().__init__()
        self.next = None

    def setup(self, request, *args, **kwargs):
        #         (http method) (python get)
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['email'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, 'خوش آمدید', extra_tags='success')
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            else:
                messages.error(request, 'ایمیل یا رمز ورود اشتباه است', extra_tags='danger')
        return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):

    @staticmethod
    def get(request):
        logout(request)
        messages.info(request, 'با موفقیت خارج شدید', extra_tags='info')
        return redirect('home:home')


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = SimpleNamespace(image=None, full_name='', age=None)
        return render(request, 'accounts/profile.html', context={'user': user, 'profile': profile})


class EditUserView(LoginRequiredMixin, View):
    form_class = EditUserForm
    template_name = 'accounts/edit_profile.html'

    def get_profile(self, user):
        profile, created = Profile.objects.get_or_create(user=user)
        return profile

    def get(self, request):
        profile = self.get_profile(request.user)
        form = self.form_class(instance=profile, user=request.user)
        return render(request, self.template_name, context={'form': form})

    def post(self, request):
        profile = self.get_profile(request.user)
        form = self.form_class(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            if form.cleaned_data.get('remove_image'):
                if profile.image:
                    profile.image.delete(save=False)
                    profile.image = None
                    profile.save()
            else:
                profile.save()

            messages.info(request, 'تغییرات با موفقیت ثبت شد', extra_tags='info')
            return redirect('accounts:user_profile', request.user.id)
        return render(request, self.template_name, context={'form': form})


class UserPasswordResetView(auth_view.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserPasswordResetDoneView(auth_view.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class PasswordResetConfirmView(auth_view.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class PasswordResetCompleteView(auth_view.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

class ManageAddressView(LoginRequiredMixin, View):
    template_name = 'accounts/manage_addresses.html'
    form_class = AddressForm

    def get(self, request):
        addresses = request.user.addresses.all()
        form = self.form_class()
        return render(request, self.template_name, context={'addresses': addresses, 'form': form})

    def post(self, request):
        edit_id = request.POST.get('edit_id')
        if edit_id:
            address = get_object_or_404(Address, id=edit_id, user=request.user)
            form = self.form_class(request.POST, instance=address)
        else:
            form = self.form_class(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            return redirect('accounts:manage_addresses')
        addresses = request.user.addresses.all()
        return render(request, self.template_name, context={'addresses': addresses, 'form': form})
