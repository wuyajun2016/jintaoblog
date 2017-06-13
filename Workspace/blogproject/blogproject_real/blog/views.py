# -*- coding: utf-8 -*
import markdown
from django.shortcuts import render, get_object_or_404
from .models import Post,Category
from comments.forms import CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView, ListView
import pdb

def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 2)
    page = request.GET.get('page')

    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'blog/index.html', context={'post_list': post_list})
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # 一旦该视图被调用，阅读量 +1
    post.increase_views()
    post.body = markdown.markdown(post.body,
                                  extensions=[
                                     'markdown.extensions.extra',
                                     'markdown.extensions.codehilite',
                                     'markdown.extensions.toc',
                                  ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    blog = Post.objects.get(pk=pk)  # 当前打开的博客
    pre_blog = Post.objects.filter(pk__gt=blog.pk).order_by('pk')
    next_blog = Post.objects.filter(pk__lt=blog.pk).order_by('-pk')


    # 取第1条记录
    if pre_blog.count() > 0:
        pre_blog = pre_blog[0]
    else:
        pre_blog = None

    if next_blog.count() > 0:
        next_blog = next_blog[0]
    else:
        next_blog = None
    context = {'post': post,
               'form': form,
               'comment_list': comment_list,
               "pre_blog": pre_blog,
               "next_blog": next_blog
               }
    return render(request, 'blog/detail.html', context=context)
def archives(request,year,month):
    post_list = Post.objects.filter(created_time__year=year, created_time__month=month)
    return render(request, 'blog/index.html', context={'post_list': post_list})
def category(request, pk):
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
def search(request):
    q = request.GET.get('q')
    error_msg = ''
    
    if not q:
        error_msg = '请输入关键字'
        return render(request,'blog/index.html',{'error_msg':error_msg})
    post_list = Post.objects.filter(title__icontains=q)
    return render(request, 'blog/index.html', {'error_msg': error_msg,
                                               'post_list': post_list})
#首页展示，以及首页中的分页功能
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 3

    def get_context_data(self, **kwargs):

        
        context = super(IndexView,self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        pagination_data = self.pagination_data(paginator, page, is_paginated)

        context.update(pagination_data)

        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}

        left = []

        right = []

        left_has_more = False

        right_has_more = False

        first = False

        last = False

        page_number = page.number

        total_pages = paginator.num_pages

        page_range = list(paginator.page_range)


        if page_number == 1:
            right = page_range[page_number:page_number + 2]

            if right[-1] < total_pages - 1:
                right_has_more = True

            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True
        else:
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
            right = page_range[page_number:page_number + 2]

            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        context = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return context
