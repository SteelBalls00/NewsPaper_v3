from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.urls import reverse

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name='имя')
    rating = models.IntegerField(default=0)

    def update_rating(self):
        rating_of_post_by_author = Post.objects.filter(author=self).aggregate(Sum('rating'))['rating__sum'] * 3
        rating_of_comments_by_author = Comment.objects.filter(user=self.user).aggregate(Sum('rating'))['rating__sum']
        rating_of_comments_under_post_of_author = Comment.objects.filter(post__author__user=self.user).aggregate(Sum('rating'))['rating__sum']

        self.rating = rating_of_post_by_author + rating_of_comments_by_author + rating_of_comments_under_post_of_author
        self.save()

    def __str__(self) -> str:
        return Author.objects.filter(pk=self.id).values_list('user__username')[0][0]

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Категории')
    subscribers = models.ManyToManyField(User, related_name='categories', blank=True)
    def subscribe(self):
        ...
    def get_category(self):
        return self.name
    def __str__(self):
        return self.name


class PostCategory(models.Model):
    post = models.ForeignKey('Post', null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)


class Post(models.Model):
    news = "NE"
    article = "AR"

    POST_TYPES = [
        (news, 'Новость'),
        (article, 'Статья')
    ]

    author = models.ForeignKey(Author, on_delete=models.PROTECT, verbose_name='Автор')
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=article, verbose_name='Вид поста')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    categories = models.ManyToManyField(Category, through=PostCategory)
    title = models.CharField(max_length=72, default="Пустой заголовок", verbose_name='Заголовок')
    content = models.CharField(max_length=2048, default='Место для текста', verbose_name='Контент')
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.content[:124] + '...' if len(self.content) > 124 else self.content

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.PROTECT, verbose_name='Пост')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    content = models.CharField(max_length=512, default='Коммент по умолчанию', verbose_name='Комментарий')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания комментария')
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

