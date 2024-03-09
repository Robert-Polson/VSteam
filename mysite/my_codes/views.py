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
def register_page(request):
    context = {}
    if request.method == "POST":
        name = request.POST.get('name')
        second_name = request.POST.get('second_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        hashed_password = make_password(password)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            context['error'] = 'Неправильно введён логин'
        elif len(password) < 8:
            context['error'] = 'Пароль должен содержать минимум 8 символов'
        else:
            account_exists = Account.objects.filter(email=email).exists()
            if not account_exists:
                username = name.lower() + '_' + second_name.lower()
                user = User.objects.create_user(first_name=name, username=username, last_name=second_name, email=email,password=password)

                table_item = Account(name=name, second_name=second_name, email=email, password=hashed_password)
                table_item.save()
                context['message'] = 'Вы успешно зарегистрировались'

            else:
                context['error'] = 'Пользователь с таким email уже существует'
    return render(request, 'register.html', context)


def niknem_page(request):
    first_name = request.session.get('username')
    last_name = request.session.get('user_seconds')
    email = request.session.get('email')

    try:
        user = User.objects.filter(first_name=first_name, last_name=last_name, email=email).first()

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
            niknem_item = NIKNEM(niknem=niknem, user=user)
            niknem_item.save()
            context['good'] = "Никнейм успешно сохранен"

    return render(request, 'mainssss.html', context)

def login_page (request) :
    context = {}
    if request.method =="POST":
        email = request. POST.get("email")
        password = request. POST. get ("password")

        users = User.objects. filter (email=email)
        if users.exists():
            for user in users:
                if check_password(password, user.password):
                    print ("good")

                    request.session['username'] = user.first_name
                    request.session['user_seconds'] = user.last_name
                    request.session['email'] = user.email

                    context[ "good"] = "Вы успешно зашли в аккаунт"
                    return render (request,'login.html', context)
                else:
                    print(make_password(password),password)
                    print ("bad" )
                    context[ "error"] = "Попробуйте ввести другой пароль"
        else:
            context ["error"] = "Такого пользователя нет"
    return render(request,"login.html", context)


def open_page(request):
    context={}
    context={'text':"Добро пожаловать в мир возможностей и новых знакомств! Здесь каждый может найти не только друзей, но и надежных игровых партнеров для захватывающих приключений. Давайте создадим незабываемые воспоминания вместе! Добро пожаловать в наше сообщество, где дружба и игры ждут вас на каждом шагу. Присоединяйтесь и откройте для себя мир новых возможностей!"}

    return render(request, 'open_page.html',context)


def account_page(request):
    context = {'name': User.first_name, 'second_name': User.last_name, 'email': User.email}

    try:
        user = User.objects.filter(username=context['name'], last_name=context['second_name'], email=context['email']).first()

        if not user:
            raise User.DoesNotExist

        niknem = NIKNEM.objects.filter(account=user).first()
        avatar = Avatar.objects.filter(account=user).first()

        if request.method == 'POST' and 'avatarInput' in request.FILES:
            image = request.FILES['avatarInput']

            if avatar:
                avatar.image = image
                avatar.save()
            else:
                new_avatar = Avatar(image=image, account=user)
                new_avatar.save()
            return redirect('account_page')

        context = {'account': user, 'avatar': avatar, 'niknem': niknem}
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
    else:
        query = request.GET.get('query', '')
        page = max(0, int(request.GET.get('page', 1)) - 1)

    all_accounts_count = NIKNEM.objects.filter(niknem__contains=query).count()
    accounts = NIKNEM.objects.filter(niknem__contains=query)[page * 10:page * 10 + 10]

    context['page'] = page + 1
    context['accounts'] = accounts
    context['max_page'] = all_accounts_count // 10 + (all_accounts_count % 10 != 0)
    context['query'] = query
    context['form'] = SearchUserForm()

    return render(request, "find_users.html", context)
def home_page(request):
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