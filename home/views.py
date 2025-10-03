from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Product, Category
from . import tasks
from django.contrib import messages
from utils import IsAdminUserMixin
from orders.forms import CardAddForm
from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery, SearchRank
from django.db.models import Q
from .forms import SearchForm
from django.db.models.functions import Greatest
from rating_comments.forms import CommentCreateForm, CommentReplyForm, RatingForm
from rating_comments.models import Rating, Comments
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.paginator import Paginator

class HomeView(View):
    def get(self, request, category_slug=None):
        products = Product.objects.filter(available=True)
        categories = Category.objects.filter(is_sub=False)
        form = SearchForm(request.GET or None)
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)

        if form.is_valid() and form.cleaned_data.get('search'):
            cd = form.cleaned_data['search']

            query = SearchQuery(cd)
            vector = SearchVector('name', 'slug')
            products = products.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.1)
            if not products.exists():
                products = Product.objects.filter(available=True).annotate(similarity=Greatest(
                    TrigramSimilarity('slug', cd),
                    TrigramSimilarity('name', cd),
                )).filter(Q(similarity__gte=0.3) | Q(name__icontains=cd) | Q(slug__icontains=cd)).order_by('-similarity')
            categories = categories.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.1)
            if not categories.exists():
                categories = Category.objects.filter(is_sub=False).annotate(similarity=Greatest(
                    TrigramSimilarity('slug', cd),
                    TrigramSimilarity('name', cd),
                )).filter(Q(similarity__gte=0.3) | Q(name__icontains=cd) | Q(slug__icontains=cd)).order_by('-similarity')
        paginator = Paginator(products, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'home/index.html', context={'products': products,
                                                           'categories': categories, 'search_form': form,
                                                           'page_obj': page_obj, 'category_slug': category_slug})

class ProductDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm
    form_rating = RatingForm

    def __init__(self):
        super().__init__()
        self.product_instance = None

    def setup(self, request, *args, **kwargs):
        self.product_instance = get_object_or_404(Product, slug=kwargs['slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        comment = self.product_instance.pcomments.filter(is_reply=False)
        form = CardAddForm()
        user_rating = Rating.objects.filter(product=self.product_instance, user=request.user).first()
        average_rating = self.product_instance.average_rating()
        return render(request, template_name='home/detail.html', context={'product': self.product_instance,
                                                                          'form': form,
                                                                          'comments_form': self.form_class,
                                                                          'comments': comment,
                                                                          'reply_form': self.form_class_reply,
                                                                          'rating_form': self.form_rating,
                                                                          'user_rating': user_rating.score if user_rating else 0,
                                                                          'average_rating': round(average_rating, 2)})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'score' in request.POST:
            form = self.form_rating(request.POST)
            if form.is_valid():
                rating, _ = Rating.objects.update_or_create(product=self.product_instance, user=request.user,
                                                            defaults={'score': form.cleaned_data['score']})
                messages.success(request, 'امتیاز شما ثبت شد', extra_tags='success')
                avg = self.product_instance.average_rating()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'ok',
                        'score': rating.score,
                        'average_rating': round(avg, 2),
                    })
            else:
                messages.error(request, 'فرم معتبر نیست', extra_tags='danger')
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({
                        "status": "error",
                    })
            return redirect('home:product_detail', slug=self.product_instance.slug)
        else:
            form = self.form_class(request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.user = request.user
                new_comment.product = self.product_instance
                parent_id = request.POST.get('parent_id')
                if parent_id:
                    parent_comment = Comments.objects.filter(pk=parent_id).first()
                    if parent_comment:
                        new_comment.reply = parent_comment
                        new_comment.is_reply = True
                new_comment.save()
                messages.success(request, 'نظر شما ثبت شد', extra_tags='success')
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({
                        "status": "ok",
                        "username": request.user.username,
                        "body": new_comment.body,
                        'is_reply': new_comment.is_reply,
                        'created': new_comment.created.strftime('%Y-%m-%d %H: %M')
                    })
            else:
                messages.error(request, 'فرم معتبر نیست', extra_tags='danger')
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({
                        "status": "error",
                    })
            return self.get(request, *args, **kwargs)

class BucketHome(IsAdminUserMixin, View):
    template_name = 'home/bucket.html'

    def get(self, request):
        objects = tasks.all_bucket_objects_task()  # .delay()  for javascript
        return render(request, template_name=self.template_name, context={'objects': objects})


class DeleteBucketObject(IsAdminUserMixin, View):
    def get(self, request, key):
        tasks.delete_object_task.delay(key)
        messages.info(request, message='your object will be delete soon', extra_tags='info')
        return redirect('home:bucket')


class DownloadBucketObject(IsAdminUserMixin, View):
    def get(self, request, key):
        tasks.download_object_task.delay(key)
        messages.info(request, message='your object will be download soon', extra_tags='info')
        return redirect('home:bucket')
