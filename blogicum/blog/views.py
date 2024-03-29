from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.conf import settings

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


class ProfileLoginView(LoginView):
    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=(self.request.user.get_username(),)
        )


def paginate_objects(request, objects_list, per_page=10):
    """Pagination helper function."""
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def edit_profile(request, name):
    """Изменение профиля пользователя."""
    user = get_object_or_404(User, username=name)
    if user.username != request.user.username:
        return redirect('login')
    form = ProfileForm(request.POST or None, instance=user)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, 'blog/user.html', context)


def info_profile(request, name):
    """Информация о профиле пользователя."""
    templates = 'blog/profile.html'
    user = get_object_or_404(
        User,
        username=name,
    )
    profile_post = user.posts.all()

    context = {
        'profile': user,
        'page_obj': paginate_objects(request, profile_post),
    }
    return render(request, templates, context)


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    ordering = '-pub_date'
    paginate_by = settings.BLOG_PAGINATE_BY

    def get_queryset(self):
        return Post.published.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context


def category_posts(request, category_slug):
    """Отображение по котегории постов."""
    templates = 'blog/category.html'
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    post_list = category.posts(manager='published').all()

    context = {
        'category': category,
        'page_obj': paginate_objects(request, post_list),
    }
    return render(request, templates, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Проверка валидности формы."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Получение адреса."""
        return reverse(
            'blog:profile',
            args=(self.request.user.get_username(),)
        )


class DispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        """Отправляет изменения/удаления поста."""
        self.post_id = kwargs['pk']
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.post_id)
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, DispatchMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        """Получение адреса."""
        return reverse('blog:post_detail', args=(self.post_id,))


class PostDeleteView(LoginRequiredMixin, DispatchMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        queryset = Post.objects.filter(
            Q(is_published=True) | Q(author=self.request.user)
        )
        return get_object_or_404(
            queryset,
            pk=self.kwargs.get('pk'),
        )

    def get_context_data(self, **kwargs):
        """Получение данных контекста."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related(
                'author'
            )
        )
        return context


@login_required
def add_comment(request, pk):
    """Добавление комментария."""
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, comment_id, post_id):
    """Изменение комментария."""
    instance = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    form = CommentForm(request.POST or None, instance=instance)
    if instance.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    context = {
        'form': form,
        'comment': instance
    }

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, comment_id, post_id):
    """Удаление комментария."""
    delete_comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if delete_comment.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    context = {'comment': delete_comment}
    if request.method == 'POST':
        delete_comment.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)
