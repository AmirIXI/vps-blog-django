from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'account'
urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('profile/<int:user_id>', views.UserProfileView.as_view(), name='user_profile'),
    path('user/reset', views.UserPasswordResetView.as_view(), name='password_reset_view'),
    path('user/reset/done', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('user/reset/confirm/<uidb64>/<token>', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('user/reset/complete', views.UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('user/follow/<int:user_id>', views.UserFollowView.as_view(), name='user_follow'),
    path('user/unfollow/<int:user_id>', views.UserUnfollowView.as_view(), name='user_unfollow'),
    path('user/activity/', views.UserNotificationsView.as_view(), name='user_activity')
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)