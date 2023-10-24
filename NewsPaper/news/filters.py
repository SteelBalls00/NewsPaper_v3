import django_filters
from django import forms
from django_filters import FilterSet, CharFilter, DateFilter
from .models import Post


class PostFilter(FilterSet):
    title = CharFilter(lookup_expr='icontains', label='По заголовку')
    author = CharFilter(lookup_expr='icontains', label='По имени автора')
    time_create = DateFilter(field_name='time_create', lookup_expr='gt', widget=forms.DateInput(attrs={'type': 'date'}), label='Позже чем')
    class Meta:
       model = Post
       fields = ['title', 'author', 'time_create']