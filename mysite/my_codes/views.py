from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils.datastructures import MultiValueDictKeyError

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
                user = User.objects.create_user(first_name=name, username=username, last_name=second_name, email=email,password=hashed_password)

                table_item = Account(name=name, second_name=second_name, email=email, password=hashed_password)
                table_item.save()
                context['message'] = 'Вы успешно зарегистрировались'

            else:
                context['error'] = 'Пользователь с таким email уже существует'
    return render(request, 'register.html', context)


def niknem_page(request):
    name = request.session.get('username')
    second_name = request.session.get('user_seconds')
    email = request.session.get('email')

    try:
        account = Account.objects.filter(name=name, second_name=second_name, email=email).first()

    except Account.DoesNotExist:
        return HttpResponse("Account not found")

    context = {}

    if request.method == 'POST':
        niknem = request.POST.get("niknem")
        if not niknem:
            context['error'] = "Введите никнейм"
        else:
            request.session['niknem'] = niknem
            context['niknem'] = niknem
            niknem_item = NIKNEM(niknem=niknem, account=account)
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
                if check_password (make_password(password), user.password):
                    print ("good")
                    request. session[ 'username'] = user.username
                    request. session[ 'email'] = user.email
                    context[ "good"] = "Вы успешно зашли в аккаунт"
                    return render (request,'login.html', context)
                else:
                    print ("bad" )
                context[ "error"] = "Попробуйте ввести деугой дароль"
        else:
            context ["error"] = "Такого пользователя нет"
    return render(request,"login.html", context)


def open_page(request):
    context={}
    context={'text':"Добро пожаловать в мир возможностей и новых знакомств! Здесь каждый может найти не только друзей, но и надежных игровых партнеров для захватывающих приключений. Давайте создадим незабываемые воспоминания вместе! Добро пожаловать в наше сообщество, где дружба и игры ждут вас на каждом шагу. Присоединяйтесь и откройте для себя мир новых возможностей!"}

    return render(request, 'open_page.html',context)


def account_page(request):
    name = request.session.get('username')
    second_name = request.session.get('user_seconds')
    email = request.session.get('email')

    try:
        account = Account.objects.filter(name=name, second_name=second_name, email=email).first()
        niknem = NIKNEM.objects.filter(account=account).first()

        if not account:
            raise Account.DoesNotExist

        avatar = Avatar.objects.filter(account=account).first()

        if request.method == 'POST' and 'avatarInput' in request.FILES:
            image = request.FILES['avatarInput']

            if avatar:
                avatar.image = image
                avatar.save()
            else:
                new_avatar = Avatar(image=image, account=account)
                new_avatar.save()
            return redirect('account_page')

        if request.method == 'GET':
            context = {'account': account, 'avatar': avatar, 'niknem': niknem}
            return render(request, 'account_page.html', context)
        else:
            return HttpResponseBadRequest()

    except Account.DoesNotExist:
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
            account = Account.objects.filter(name=name, second_name=second_name, email=email).first()
            if account:
                account.password = make_password(password)
                account.save()
                context['good'] = "Пароль успешно изменен"
            else:
                context['error'] = "Пароль не сохранен"
        except Account.DoesNotExist:
            context['error'] = 'Произошла ошибка при попытке изменения пароля'

    return render(request, "remember_password.html", context)


def achievements(request):
    return render(request, "Achievements.html")


from django.shortcuts import render
from .models import NIKNEM

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
    return render(request,'homePage.html')

def turnir_page(request):
    return render(request,'turnir_page.html')

def reviews(request):
    return render(request,'reviews.html')
def settings_page(request):
    context={}
    return render(request,'settings.html',context)