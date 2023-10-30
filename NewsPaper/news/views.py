from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, resolve
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView
from django.core.mail import EmailMultiAlternatives
# from django import settings

from django.http.response import HttpResponse
from django.utils import timezone
import pytz

# from django.utils.translation import activate, get_supported_language_variant, LANGUAGE_SESSION_KEY
from django.utils.translation import gettext as _

from .forms import PostForm
from .models import Post, Category
from .filters import PostFilter


class NewsList(ListView):
    model = Post
    ordering = '-time_create'
    template_name = 'all_news.html'
    context_object_name = 'all_news'
    paginate_by = 10

    # Переопределяем функцию получения списка товаров
    def get_queryset(self):
        # self.category =get_object_or_404(Category, id=self.kwargs['pk'])
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        # context['category'] = self.category
        context['current_time'] = timezone.now()
        context['timezones'] = pytz.common_timezones

        return context

    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('post_list')




class NewsDetail(DetailView):
    model = Post
    template_name = 'one_news.html'
    context_object_name = 'one_news'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        context['timezones'] = pytz.common_timezones

        return context

    # def post(self, request):
    #     request.session['django_timezone'] = request.POST['timezone']
    #     return redirect('post_detail')


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post')
    form_class = PostForm
    model = Post
    template_name = 'edit_news.html'
    context_object_name = 'edit_news'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/news/article/create/':
            post.post_type = 'AR'
        if self.request.path == '/news/create/':
            post.post_type = 'NE'
        print(self.request.path)
        print(post.post_type)
        post.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        context['timezones'] = pytz.common_timezones



class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post')
    form_class = PostForm
    model = Post
    template_name = 'edit_news.html'
    # success_url = reverse_lazy('post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        context['timezones'] = pytz.common_timezones



class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post')
    model = Post
    template_name = 'delete_news.html'
    success_url = reverse_lazy('post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        context['timezones'] = pytz.common_timezones



class PostSearch(ListView):
    model = Post
    ordering = '-time_create'
    template_name = 'search_news.html'
    context_object_name = 'search_news'
    paginate_by = 10

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        context['current_time'] = timezone.now()
        context['timezones'] = pytz.common_timezones
        return context



class PostCategoryView(ListView):
    model = Post
    template_name = 'subscribe/category.html'
    context_object_name = 'posts'
    ordering = '-time_create'
    paginate_by = 10

    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        c = Category.objects.get(id=self.id)
        queryset = Post.objects.filter(category=c)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        category = Category.objects.get(id=self.id)
        subscribed = category.subscribers.filter(email=user.email)
        if not subscribed:
            context['category'] = category
        return context


# def subscribe_to_category(request, pk):
#     user = request.user
#     category = Category.objects.get(id=pk)
#     if not category.subscribers.filter(id=user. id).exists():
#         category.subscribers.add(user)
#         email = user.email
#         html = render_to_string('mail/suscribed.html',
#                                 {
#                                     'category': category,
#                                     'user': user,
#                                 },
#                                 )
#         msg = EmailMultiAlternatives (
#             subject=f'{category} subscription',
#             body='',
#             from_email=DEFAULT_FROM_EMAIL,
#             to=[email,],
#         )
#         msg.attach_alternative(html, 'text/html')
#
#         try:
#             msg.send()
#         except Exception as e:
#                 print(e)
#         return redirect('users:index')
#     return redirect(request.META.get('HTTP_REFERER'))


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    message = 'Вы успешно подписались на рассылку новостей категории'
    return render(request, 'subscribe/subscribed.html', {'category':category, 'message':message})


@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)

    if category.subscribers.filter(id=user.id).exists():
        category.subscribers.remove(user)
    return redirect('/')

class CategoryListView(ListView):
    model = Post
    template_name = 'subscribe/category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category =get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(categories=self.category).order_by('-time_create')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['is not subscriber'] = not self.category.subscribers.filter(id=self.request.user.id).exists()
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        context['current_time'] = timezone.now()
        context['timezones'] = pytz.common_timezones

        return context


