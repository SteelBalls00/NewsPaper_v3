from celery import shared_task
import datetime

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


import time

import news
from news.models import Post, Category, PostCategory


@shared_task
def send_notifications(pk):
    post = Post.objects.get(pk=pk)
    categories = post.categories.all()
    title = post.title
    subscribers: list[str] = []
    for category in categories:
        subscribers = category.subscribers.all()
    subscribers_emails = [s.email for s in subscribers]

    html_content = render_to_string(
        'subscribe/post_created.html',
        {
            'text': news.models.Post.preview,
            'link': f'http://127.0.0.1:8000/news/{pk}',
        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()
    print('рассылка завершена')


# @shared_task
# def send_notifications(preview, pk, title, subscribers):
#     html_content = render_to_string(
#         'subscribe/post_created.html',
#         {
#             'text': preview,
#             'link': f'http://127.0.0.1:8000/news/{pk}',
#         }
#     )
#
#     msg = EmailMultiAlternatives(
#         subject=title,
#         body='',
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=subscribers,
#     )
#
#     msg.attach_alternative(html_content, 'text/html')
#     msg.send()
#
#     def notify_about_new_post(sender, instance, **kwargs):
#         if kwargs['action'] == 'post_add':
#             print('Сигнал сработал')
#             categories = instance.categories.all()
#             subscribers: list[str] = []
#             for category in categories:
#                 subscribers += category.subscribers.all()
#
#             subscribers = [s.email for s in subscribers]
#
#             send_notifications(instance.preview, instance.pk, instance.title, subscribers)


@shared_task
def notify_about_weekly_post():
    week_news = datetime.datetime.now() - datetime.timedelta(days=7)
    posts = Post.objects.filter(time_create__gte=week_news)
    categories = set(posts.values_list('categories', flat=True))
    for category in Category.objects.all():
        post_list = posts.filter(categories=category)
        if post_list:
            subscribers = category.subscribers.values('username', 'email')
            subscribers_emails = []
            for subscriber in subscribers:
                subscribers_emails.append(subscriber['email'])

            html_contex = render_to_string(
                'subscribe/daily_post.html',
                {
                    'link': f'http://127.0.0.1:8000/news/',
                    'posts': post_list,
                }
            )
            msg = EmailMultiAlternatives(
                subject='Посты за неделю',
                body='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=subscribers_emails,
            )
            msg.attach_alternative(html_contex, 'text/html')
            msg.send()
            print('рассылка завершена')


    # if kwargs['action'] == 'post_add':
    #     print('Сигнал сработал')
    #     categories = instance.categories.all()
    #     subscribers: list[str] = []
    #     for category in categories:
    #         subscribers += category.subscribers.all()
    #
    #     subscribers = [s.email for s in subscribers]
    #
    #     send_notifications(instance.preview, instance.pk, instance.title, subscribers)
