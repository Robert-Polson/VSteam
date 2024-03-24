from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.utils.datastructures import MultiValueDictKeyError
from .forms import SearchUserForm
import re
import time
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from mysite.settings import MEDIA_ROOT

from .forms import LoginForm, RegisterForm, RememberPassword
from .forms import SearchUserForm
from .models import NIKNEM, Friend, Post


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
    username = request.session.get('username')
    email = request.session.get('email')
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
    if request.user.is_authenticated:
        return redirect('homePage')
    context = {}
    context = {
        'text': "Добро пожаловать в мир возможностей и новых знакомств! Здесь каждый может найти не только друзей, "
                "но и надежных игровых партнеров для захватывающих приключений. Давайте создадим незабываемые "
                "воспоминания вместе! Добро пожаловать в наше сообщество, где дружба и игры ждут вас на каждом шагу. "
                "Присоединяйтесь и откройте для себя мир новых возможностей!"}

    return render(request, 'open_page.html', context)


def api_v1_user_upload_avatar(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    uploaded_file = request.FILES.get('avatar', None)

    if not uploaded_file:
        return HttpResponse(status=400)

    if not uploaded_file.content_type.startswith('image/'):
        return HttpResponse(status=415)

    user = request.user

    if not user.is_authenticated:
        return HttpResponse(status=401)

    try:
        with BytesIO(uploaded_file.read()) as f:
            image = Image.open(f)
            image.verify()

            image = Image.open(f)

            image = image.resize((256, 256), Image.Resampling.LANCZOS)

            path = MEDIA_ROOT + '/avatars/' + str(user.id) + '.png'

            image.save(path)
        return HttpResponse(status=200)
    except [UnidentifiedImageError, EOFError, DecompressionBombError]:
        return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=500)


def account_page(request, username):
    try:
        user = User.objects.filter(username=username).first()

        if not user:
            raise User.DoesNotExist

        niknem = NIKNEM.objects.filter(user=user).first()
        context.update({
            'account': user,
            'niknem': niknem,
            'show_change': True,
            'show_publish_button': True,
            'show_message_button': True,
            'show_achievements_button': True,
            'show_likes':False,
            'show_dislike': False,
            'invite_friends':False,
            'add_comments':False
        })

        context = {'account': user, 'niknem': niknem.niknem if niknem is not None else 'No NickName',
                   'is_owner_of_account': user == request.user}
        return render(request, 'account_page.html', context)

    except User.DoesNotExist:
        context = {'error': 'Такого пользователя нет'}
        return render(request, 'account_page.html', context)


def remember_password(request):
    form = RememberPassword()
    if request.method == 'POST':
        form = RememberPassword(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.filter(username=username.lower(), email=email.lower()).first()
            if user:
                user.set_password(password)
                user.save()
                messages.success(request, f'Password changed successfully for user {user.username}!')
                return redirect('login')
            else:
                messages.error(request, 'User not found with the provided username and email')

    return render(request, 'remember_password.html', {'form': form})



def achievements(request):
    return render(request, "Achievements.html")

def settings_page(request, user_id=None):
    try:
        user = User.objects.get(id=user_id)
        niknem = NIKNEM.objects.filter(user=user).first()

        context = {
            'account': user,
            'niknem': niknem,
            'show_change':False,
            'show_publish_button': True,
            'show_message_button': False,
            'show_achievements_button': True,
            'show_likes': True,
            'show_dislike': True,
            'invite_friends':True,
            'add_comments':True
        }
        return render(request, 'account_page.html', context)

    except User.DoesNotExist:
        context = {'error': 'Такого пользователя нет'}
        return render(request, 'account_page.html', context)
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

    current_user = request.user
    accounts = NIKNEM.objects.filter(niknem__contains=query).exclude(user=current_user)[page * 10:page * 10 + 10]

    context['page'] = page + 1
    context['accounts'] = accounts
    context['max_page'] = all_accounts_count // 10 + (all_accounts_count % 10 != 0)
    context['query'] = query
    context['form'] = SearchUserForm(initial={'query': query})

    if 'add_friend' in request.POST:
        friend_id = request.POST.get('friend_id')
        friend = get_object_or_404(User, id=friend_id)
        Friend.make_friend(request.user, friend)

    return render(request, "find_users.html", context)
def home_page(request):
    print(request.user.username)
    context = {'account': request.user}

    return render(request, 'homePage.html', context)

def turnir_page(request):
    return render(request, 'turnir_page.html')
    context = {}
    if request.method == "POST":
        date = request.POST.get('Date')
        name = request.POST.get('Name')
        participants = request.POST.get('Participants')
        placeToWatch = request.POST.get('PlaceToWatch')
        turnir = Turnir.objects.create(date=date, name=name, participants=participants, placeToWatch=placeToWatch)
    context['turnirs'] = Turnir.objects
    return render(request,'turnir_page.html')

def reviews(request):
    return render(request, 'reviews.html')


def settings_page(request, user_id=None):
    try:
        user = User.objects.get(id=user_id)
        niknem = NIKNEM.objects.filter(user=user).first()

        context = {
            'account': user,
            'niknem': niknem,
            'show_sett_acc_page': True
        }
        return render(request, 'account_page.html', context)

    except User.DoesNotExist:
        context = {'error': 'Такого пользователя нет'}
        return render(request, 'account_page.html', context)


def my_profile(request):
    print('123')
    user = request.user
    if user.is_authenticated:
        return redirect('user_profile', username=user.username)
    return redirect('register')


def logout_page(request):
    logout(request)
    return redirect('login')


def profile(request, username=None):
    friend = Friend.objects.filter(current_user=request.user).first()
    friends_data =[]
    friends = []
    if friend:
        friends = friend.users.all()

        for friend in friends:
            friend_data = dict()
            friend_data['username'] = friend.username
            friend_data['niknem'] = NIKNEM.objects.filter(user=friend).first()
            friends_data.append(friend_data)
    if username:
        post_owner = get_object_or_404(User, username=username)

    else:
        post_owner = request.user

    args = {
        'post_owner': post_owner,
        'friends': friends_data,

    }
    return render(request, 'profile.html', args)


def change_friends(request, operation, pk):
    friend = get_object_or_404(User, pk=pk)
    if operation == 'add':
        Friend.make_friend(request.user, friend)
    return redirect('profile', username=friend.username)



