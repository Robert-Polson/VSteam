"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls.static import static
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path

from my_codes import views


from mysite import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.open_page),
    path("mainsss/", views.niknem_page, name="mainssss"),
    path("login_pages/", views.login_page, name="login"),
    path("register_page/", views.register_page, name="register"),
    path("account_pages/", views.account_page, name="account_page"),
    path("remember_password/", views.remember_password, name="remember_password"),
    path("find_users/", views.find_users_page, name="find_users_page"),
    path("achievements//", views.achievements),
    path("open_page", views.open_page, name="open_page"),
    path("home_pages/", views.home_page, name="homePage"),
    path("tournament_page/", views.tournament_page, name="tournament"),
    path("reviews/<int:user_id>/", views.reviews, name="reviews"),
    path("settings/", views.settings_page),
    path("user/<str:username>", views.account_page, name="user_profile"),
    path("my_profile/", views.my_profile, name="my_profile"),
    path("logout/", views.logout_page, name="logout"),
    path("profile/<str:username>/", views.profile, name="profile_pk"),
    path("api/v1/user/change_avatar/", views.api_v1_user_upload_avatar),
    path(
        "connect/<str:operation>/<int:pk>/", views.change_friends, name="change_friends"
    ),
    path(
        "change-friends/<str:operation>/<int:pk>/",
        views.change_friends,
        name="change_friends",
    ),
    path(
        "polzovatels_account/<int:user_id>/",
        views.settings_page,
        name="polzovatels_account",
    ),

    path("social_network/", views.social_network, name="social_network"),
    path("charts/", views.charts, name="charts"),
    path("create_post", views.create_post, name="create_post"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
