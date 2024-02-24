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
from django.contrib import admin
from django.urls import path

from my_codes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.open_page),
    path('mainsss/', views.niknem_page),
    path('login_pages/', views.login_page),
    path('register_page/', views.register_page),
    path('login_pages/', views.login_page),
    path('account_pages/',views.account_page, name='account_page'),
    path('remember_password/',views.remember_password),
    path('find_users/',views.find_users_page),
    path('achievements//',views.achievements)
]