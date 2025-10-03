from django.shortcuts import redirect, get_object_or_404
from django.views import View
from .models import Comments, Rating
from home.models import Product
from .forms import CommentReplyForm, RatingForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, slug, comment_id):
        product = get_object_or_404(Product, slug=slug)
        comment = get_object_or_404(Comments, pk=comment_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.product = product
            parent_comment = comment.reply if comment.is_reply else comment
            reply.reply = parent_comment
            reply.is_reply = True
            reply.save()
            messages.success(request, 'نظر شما ثبت شد', extra_tags='success')
        return redirect('home:product_detail', product.slug)

class PostDeleteCommentView(LoginRequiredMixin, View):
    def get(self, request, slug, comment_id):
        product = get_object_or_404(Product, slug=slug)
        comment = get_object_or_404(Comments, pk=comment_id)
        if comment.user.id == request.user.id:
            comment.delete()
            messages.warning(request, 'نظر شما با موفقیت پاک شد', extra_tags='warning')
        else:
            messages.error(request, 'شما نمیتوانید این نظر را پاک کنید', extra_tags='danger')
        return redirect('home:product_detail', product.slug)

class PostAddRatingView(LoginRequiredMixin, View):
    form_class = RatingForm

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        form = self.form_class(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(product=product, user=request.user,
                                            defaults={'score': form.cleaned_data['score']})
            messages.success(request, 'امتیاز شما ثبت شد', extra_tags='success')
        else:
            messages.error(request, 'امتیاز معتبر نیست', extra_tags='danger')
        return redirect('home:product_detail', slug=product.slug)
