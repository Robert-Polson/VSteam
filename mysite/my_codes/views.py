from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import Account, NIKNEM, Avatar
import re


def register_page(request):
    context = {}
    if request.method == "POST":
        name = request.POST.get('name')
        second_name = request.POST.get('second_name')
        email = request.POST.get('email')  # Исправлено на 'email'
        password = request.POST.get('password')  # Исправлено на 'password'
        hashed_password = make_password(password)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            context['error'] = 'Неправильно введён логин'
        elif len(password) < 8:
            context['error'] = 'Пароль должен содержать минимум 8 символов'
        else:
            request.session['username'] = name
            request.session['user_seconds'] = second_name
            request.session['email']=email
            table_item = Account(name=name, second_name=second_name, email=email, password=hashed_password)
            table_item.save()
            context['message'] = 'Вы успешно зарегистрировались'

    return render(request, 'register.html', context)


def niknem_page(request):
    context={}
    niknem=request.POST.get("niknem")
    s=str()
    if niknem=="":
        context['error']="введите никнейм"
    else:
        context['good']=""
        table_item1=NIKNEM(niknem=niknem)
        table_item1.save()
    return render(request,'mainssss.html',context)

def login_page(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        accounts = Account.objects.filter(email=email)
        if accounts.exists():
            for account in accounts:
                if check_password(password, account.password):
                    request.session['username'] = account.name
                    request.session['user_seconds'] = account.second_name
                    request.session['email'] = account.email
                    context["good"] = "Вы успешно зашли в аккаунт"
                    break
            else:
                context["error"] = "Попробуйте ввести другой пароль"
        else:
            context["error"] = "Такого пользователя нет"
    return render(request, 'login.html', context)



def account_page(request):
    name = request.session.get('username')
    second_name = request.session.get('user_seconds')
    email = request.session.get('email')

    try:
        account = Account.objects.filter(name=name, second_name=second_name, email=email).first()
        if not account:
            raise Account.DoesNotExist

        avatar = Avatar.objects.filter(account=account).first()

        if request.method == "POST":
            if 'image' in request.FILES:
                image = request.FILES['image']
                if avatar:
                    avatar.image = image
                    avatar.save()
                else:
                    new_avatar = Avatar(image=image, account=account)
                    new_avatar.save()
                return redirect('account_page')

        return render(request, 'account_page.html', {'account': account, 'avatar': avatar})
    except Account.DoesNotExist:
        context = {'error': 'Такого пользователя нет'}
        return render(request, 'account_page.html', context)


