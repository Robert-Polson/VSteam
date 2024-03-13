from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils.datastructures import MultiValueDictKeyError
from passlib.hash import pbkdf2_sha256
from .forms import SearchUserForm
from .models import Account, NIKNEM, Avatar
import re
import time
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect

def register_page(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            request.session['username'] = user.username
            request.session['email'] = user.email

            niknem_item = NIKNEM(user=user)
            niknem_item.save()

            messages.success(request, 'You have signed up successfully.')
            print(messages.success(request, 'You have signed up successfully.'))
            return redirect('mainssss')
        else:
            return render(request, 'register.html', {'form': form})



def niknem_page(request):
    username=request.session.get('username')
    email=request.session.get('email')
    print(request.user.username)
    try:
        user = User.objects.get(username=username, email=email)
    except User.DoesNotExist:
        return HttpResponse("User not found")

    context = {}

    if request.method == 'POST':
        niknem = request.POST.get("niknem")
        if not niknem:
            context['error'] = "Введите никнейм"
        else:
            request.session['niknem'] = niknem
            context['niknem'] = niknem

            niknem_item, created = NIKNEM.objects.get_or_create(user=user)
            niknem_item.niknem = niknem
            niknem_item.save()

            context['good'] = "Никнейм успешно сохранен"

        if user:
            context['user_id'] = user.id

    return render(request, 'mainssss.html', context)


def login_page(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username.lower(), password=password)
            if user:
                login(request, user)
                messages.success(request, f'Hi {user.username.title()}, welcome back!')
                print(request.user.username)
                return redirect('homePage')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html', {'form': form})


def open_page(request):
    print(request.user.username)
    if request.user.is_authenticated== True:
        return redirect('homePage')
    context={}
    context={'text':"Добро пожаловать в мир возможностей и новых знакомств! Здесь каждый может найти не только друзей, но и надежных игровых партнеров для захватывающих приключений. Давайте создадим незабываемые воспоминания вместе! Добро пожаловать в наше сообщество, где дружба и игры ждут вас на каждом шагу. Присоединяйтесь и откройте для себя мир новых возможностей!"}

    return render(request, 'open_page.html',context)


def account_page(request):
    username = request.user.username
    context = {'email': request.user.email}

    try:
        user = User.objects.filter(username=username, email=context['email']).first()

        if not user:
            raise User.DoesNotExist

        niknem = NIKNEM.objects.filter(user=user).first()


        context = {'account': user, 'niknem': niknem, 'username': username}
        return render(request, 'account_page.html', context)

    except User.DoesNotExist:
        context = {'error': 'Такого пользователя нет'}
        return render(request, 'account_page.html', context)






def remember_password(request):
    context = {}
    if request.method == "POST":
        name = request.POST.get("name")
        second_name = request.POST.get("second_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.filter(first_name=name, last_name=second_name, email=email).first()
            if user:
                user.set_password(password)
                user.save()
                context['good'] = "Пароль успешно изменен"
            else:
                context['error'] = "Пароль не сохранен"
        except User.DoesNotExist:
            context['error'] = 'Произошла ошибка при попытке изменения пароля'

    return render(request, "remember_password.html", context)


def achievements(request):
    return render(request, "Achievements.html")




def find_users_page(request):
    context = {}

    if request.method == 'POST':
        form = SearchUserForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            page = 0
        else:
            query = ''
            page = 0
    else:
        query = request.GET.get('query', '')
        page = max(0, int(request.GET.get('page', 1)) - 1)

    all_accounts_count = NIKNEM.objects.filter(niknem__contains=query).count()
    accounts = NIKNEM.objects.filter(niknem__contains=query)[page * 10:page * 10 + 10]

    context['page'] = page + 1
    context['accounts'] = accounts
    context['max_page'] = all_accounts_count // 10 + (all_accounts_count % 10 != 0)
    context['query'] = query
    context['form'] = SearchUserForm(initial={'query': query})

    return render(request, "find_users.html", context)
def home_page(request):
    print(request.user.username)
    context={}

    context['username']=f'Welcome'
    return render(request,'homePage.html',context)

def turnir_page(request):
    return render(request,'turnir_page.html')

def reviews(request):
    return render(request,'reviews.html')
def settings_page(request):
    context={}
    return render(request,'settings.html',context)