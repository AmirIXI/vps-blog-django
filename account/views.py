from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post, Vote
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .models import Relation


class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = 'account/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, f'Hi Dear {request.user.username} You Already Logged In To This Site First Logout Then Try Again !', 'danger')
            return redirect('home:home_page')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(
                username=cd['username'],
                email=cd['email'],
                password=cd['password1'],
                first_name = cd.get('first_name', ''),
                last_name = cd.get('last_name', '')
            )
            messages.success(request, 'your account has been register successfully now login', 'success')
            return redirect('account:user_login')

        return render(request, self.template_name, {'form': form})


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'account/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get('next')  # default None

        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, f'Hi Dear {request.user.username} You Already Logged In To This Site First Logout Then Try Again !', 'danger')
            return redirect('home:home_page')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome Back Dear {cd["username"]} Hope You Enjoy !', 'success')
                if self.next:
                    return redirect(self.next)

                return redirect('home:home_page')

            messages.warning(request, 'email or password is wrong ! please try again !', 'warning ')

        return render(request, self.template_name, {'form': form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'you has been logged out from blog successfully', 'success')
        return redirect('home:home_page')

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        posts = Post.objects.filter(user=user)
        is_following = False
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            is_following = True

        return render(request, 'account/profile.html', {'user': user, 'posts': posts, 'is_following': is_following})


class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = 'account/reset_password_view.html'
    success_url = reverse_lazy('account:password_reset_done')
    email_template_name = 'account/reset_password_email.html'


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'account/reset_password_done.html'

class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'account/reset_password_confirm.html'
    success_url = reverse_lazy('account:password_reset_complete')

class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            messages.warning(request, f'You Are Already Following {user.username}', 'danger')

        else:
            new_relation = Relation(from_user=request.user, to_user=user)
            new_relation.save()
            messages.success(request, f'You Now Following {user.username}')

        return redirect('account:user_profile', user.id)


class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        if relation.exists():
            relation.delete()
            messages.success(request, f'You Are Now Unfollow {user.username}')
        else:
            messages.warning(request, f'You Are Not {user.username} Followers ', 'danger')

        return redirect('account:user_profile', user.id)



class UserNotificationsView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        post = Post.objects.filter(user=user)
        relation_following = Relation.objects.filter(from_user=user)
        relation_followers = Relation.objects.filter(to_user=user)
        post_liked = Vote.objects.filter(user=user)

        context = {
            'user': user,
            'relation_following': relation_following,
            'relation_followers': relation_followers,
            'post_liked': post_liked,
            'post': post
        }

        return render(request, 'account/activity.html', context)
