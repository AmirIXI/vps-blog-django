from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Post, Comment, Vote
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import PostUpdateForm, PostCreateForm, CommentCreateForm, CommentReplyForm, PostSearchForm
from django.utils.text import slugify
from django.utils.decorators import method_decorator # decorator convertor from get decorators to post decorators
from django.contrib.auth.decorators import login_required



from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post
from .forms import PostSearchForm

class HomeView(View):
    form_class = PostSearchForm
    template_name = 'home/home.html'
    paginate_by = 4  # تعداد پست‌ها در هر صفحه

    def get(self, request):
        posts = Post.objects.all().order_by('-created')  # فرض می‌کنیم که فیلد 'created' وجود دارد
        search_query = request.GET.get('search')
        
        if search_query:
            posts = posts.filter(title__contains=search_query)
        
        paginator = Paginator(posts, self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'form': self.form_class(request.GET),
        }
        
        return render(request, self.template_name, context)


class PostDetailView(View):
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'], slug=kwargs['post_slug'])

        return super().setup(request, *args, **kwargs)
    def get(self, request, *args, **kwargs):
        comments = self.post_instance.pcomments.filter(is_reply=False).order_by('-created')

        post_is_like = False
        if request.user.is_authenticated:
            relation = Vote.objects.filter(user=request.user, post=self.post_instance)
            if relation.exists():
                post_is_like = True

        context = {
            'post': self.post_instance,
            'comments': comments,
            'form': self.form_class,
            'form_reply': self.form_class_reply,
            'post_is_like': post_is_like
        }
        # return render(request, 'home/detail.html', {'post': self.post_instance, 'comments': comments, 'form': self.form_class, 'form_reply': self.form_class_reply})

        return render(request, 'home/detail.html', context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = self.post_instance
            new_comment.save()
            messages.success(request, 'your comment has benn send successfully :)', 'success')
            return redirect('home:post_detail', self.post_instance.id, self.post_instance.slug)

class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if request.user.id == post.user.id:
            post.delete()
            messages.success(request, 'your post has been deleted successfully', 'success')
            return redirect('account:user_profile', post.user.id)

        messages.error(request, 'You Can Delete Your Own Post Only !', 'danger')
        return redirect('home:post_detail', post.id, post.slug)


class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostUpdateForm
    template_name = 'home/update.html'

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])

        return super().setup(request, *args, **kwargs)


    def dispatch(self, request, *args, **kwargs):
        if request.user.id != self.post_instance.user.id:
            messages.error(request, 'you can update your own posts only', 'danger')
            return redirect('account:user_profile', request.user.id)
        return super().dispatch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.post_instance)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.post_instance)
        if form.is_valid():
            new_update = form.save(commit=False)
            new_update.slug = slugify(form.cleaned_data['body'][:50])
            new_update.save()
            messages.success(request, 'your post has been updated successfully', 'success')
            return redirect('home:post_detail', self.post_instance.id, self.post_instance.slug)

        return render(request, self.template_name, {'form': form})


class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateForm
    template_name = 'home/create.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.title = form.cleaned_data['title']
            new_post.body = form.cleaned_data['body']
            new_post.slug = slugify(form.cleaned_data['body'][:50])
            new_post.save()

            messages.success(request, 'your post has been created', 'success')
            return redirect('home:post_detail', new_post.id, new_post.slug)

        return render(request, self.template_name, {'form': form})


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, post_id, comment_id):
        post = get_object_or_404(Post, pk=post_id)
        comment = get_object_or_404(Comment, pk=comment_id)

        form = self.form_class(request.POST)
        if form.is_valid():
            new_reply = form.save(commit=False)
            new_reply.user = request.user
            new_reply.post = post
            new_reply.reply = comment
            new_reply.is_reply = True
            new_reply.save()

            messages.success(request, 'your reply has been send', 'success')


        return redirect('home:post_detail', post.id, post.slug)



class PostLikeView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        relation = Vote.objects.filter(user=request.user, post=post)
        if relation.exists():
            messages.error(request, 'you already lied this post', 'danger')

        else:
            like = Vote(user=request.user, post=post)
            like.save()
            messages.success(request, 'you liked this post', 'success')

        return redirect('home:post_detail', post.id, post.slug)


class PostUnlikeView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        relation = Vote.objects.filter(user=request.user, post=post)
        if relation.exists():
            relation.delete()
            messages.success(request, 'you unlike this post', 'success')

        else:
            messages.error(request, 'you does not like this post', 'danger')


        return redirect('home:post_detail', post.id, post.slug)
