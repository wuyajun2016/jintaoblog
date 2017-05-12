from django import template
from ..models import Post
from ..models import Category
from django.db.models.aggregates import Count
import sys
sys.path.append("../../../")
import comments.models

register = template.Library()

@register.simple_tag
def get_recent_posts(num=5):
    return Post.objects.all()[:num]

@register.simple_tag
def archives():
    return Post.objects.dates('created_time', 'month', order='DESC')

@register.simple_tag
def get_categories():
    return Category.objects.annotate(num_posts=Count('post'))
    