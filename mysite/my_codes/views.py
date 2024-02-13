from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from .models import Account, NIKNEM
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
    context={}
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        try:
            account=Account.objects.get(email=email)
            if check_password(password,account.password):
                context["good"]="Вы успешно зашли в аккаунт"
            else:
                context["error"]="Попробуйте ввести другой пароль"
        except Account.DoesNotExist:
            context["error"]="Такого пользователя нет"
    return render(request,'login.html', context)
