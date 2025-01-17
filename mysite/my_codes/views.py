""" file views.py """
from collections import OrderedDict
from sqlite3 import IntegrityError

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.core import serializers
from django.db.models import Count, Q, Max
from django.db.models.functions import TruncMonth, TruncDate
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import SearchUserForm
from .models import NIKNEM, Friend, Turnir, Reviews, Post1, Avatar, Message, Socials, PostFile, Achievement, Likes

from .forms import LoginForm, RegisterForm, RememberPassword
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
import requests
# import datetime
from datetime import datetime, date as datetime_date


def register_page(request):
    """Code for register page"""
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "register.html", {"form": form})

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            request.session["username"] = user.username
            request.session["email"] = user.email

            niknem_item = NIKNEM(user=user)
            niknem_item.save()

            messages.success(request, "You have signed up successfully.")
            print(messages.success(request, "You have signed up successfully."))
            return redirect("mainssss")
        else:
            return render(request, "register.html", {"form": form})


def niknem_page(request):
    """Code for nikname page"""
    username = request.session.get("username")
    email = request.session.get("email")
    print(request.user.username)
    try:
        user = User.objects.get(username=username, email=email)
    except User.DoesNotExist:
        return HttpResponse("User not found")

    context = {}

    if request.method == "POST":
        niknem = request.POST.get("niknem")
        if not niknem:
            context["error"] = "Введите никнейм"
        else:
            request.session["niknem"] = niknem
            context["niknem"] = niknem

            niknem_item, created = NIKNEM.objects.get_or_create(user=user)
            niknem_item.niknem = niknem
            niknem_item.save()

            context["good"] = "Никнейм успешно сохранен"

        if user:
            context["user_id"] = user.id

    return render(request, "mainssss.html", context)


def login_page(request):
    """Code for login page"""
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username.lower(), password=password)
            if user:
                login(request, user)
                messages.success(request, f"Hi {user.username.title()}, welcome back!")
                print(request.user.username)
                return redirect("homePage")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html", {"form": form})


def open_page(request):
    """Code for open page"""
    print(request.user.username)
    if request.user.is_authenticated:
        return redirect("homePage")
    context = {}
    context = {
        "text": "Добро пожаловать в мир возможностей и новых знакомств! Здесь каждый может найти не только друзей, "
                "но и надежных игровых партнеров для захватывающих приключений. Давайте создадим незабываемые "
                "воспоминания вместе! Добро пожаловать в наше сообщество, где дружба и игры ждут вас на каждом шагу. "
                "Присоединяйтесь и откройте для себя мир новых возможностей!"
    }

    return render(request, "open_page.html", context)


def api_v1_user_upload_avatar(request):
    """Code for avatar page"""
    if request.method != "POST":
        return HttpResponse(status=405)

    uploaded_file = request.FILES.get("avatar", None)

    if not uploaded_file:
        return HttpResponse(status=400)

    if not uploaded_file.content_type.startswith("image/"):
        return HttpResponse(status=415)

    user = request.user

    if not user.is_authenticated:
        return HttpResponse(status=401)

    Avatar.save_avatar(user, uploaded_file)

    return HttpResponse(status=200)


def account_page(request, username):
    """Code for account page"""
    friends_count = 0
    posts_count = 0
    posts_liked = 0
    try:
        user = User.objects.filter(username=username).first()
        reviews = Reviews.objects.filter(id_commented=user.id)
        friends = Friend.get_friends(current_user=user)
        friends_count = friends.count()
        posts = Post1.objects.filter(author=user)
        posts_count = posts.count()
        for post in posts:
            posts_liked += post.liked.all().count()
        author = Socials.objects.filter(author=user.id).last()
        niknem = NIKNEM.objects.filter(user=user).first()
        achievement_text = Achievement.objects.filter(author_achievement=user.id).last()

        context = {
            "account": user,
            "author": author,
            "niknem": niknem.niknem if niknem else "No NickName",
            "is_owner_of_account": user == request.user,
            "reviews": reviews,
            "post_count": posts_count,
            "friends_count": friends_count,
            "posts_liked": posts_liked,
            "achievement_text": achievement_text,
        }

        return render(request, "account_page.html", context)

    except User.DoesNotExist:
        context = {"error": "Такого пользователя нет"}
        return render(request, "account_page.html", context)


def remember_password(request):
    """Code for remember page"""
    form = RememberPassword()
    if request.method == "POST":
        form = RememberPassword(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = User.objects.filter(
                username=username.lower(), email=email.lower()
            ).first()
            if user:
                user.set_password(password)
                user.save()
                messages.success(
                    request, f"Password changed successfully for user {user.username}!"
                )
                return redirect("login")
            else:
                messages.error(
                    request, "User not found with the provided username and email"
                )

    return render(request, "remember_password.html", {"form": form})


def find_users_page(request):
    """Code for find users page"""
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
    accounts = NIKNEM.objects.filter(niknem__contains=query).exclude(user=current_user)[
               page * 10: page * 10 + 10
               ]

    context["page"] = page + 1
    context["accounts"] = accounts
    context["max_page"] = all_accounts_count // 10 + (all_accounts_count % 10 != 0)
    context["query"] = query
    context["form"] = SearchUserForm(initial={"query": query})

    if "add_friend" in request.POST:
        friend_id = request.POST.get("friend_id")
        friend = get_object_or_404(User, id=friend_id)
        Friend.make_friend(request.user, friend)

    return render(request, "find_users.html", context)


# def tournament_page(request):
#     context = {}
#     if request.method == "POST":
#         date = request.POST.get("Date")
#         name = request.POST.get("Name")
#         participants = request.POST.get("Participants")
#         placeToWatch = request.POST.get("PlaceToWatch")
#         turnir = Turnir.objects.create(
#             date=date, name=name, participants=participants, placeToWatch=placeToWatch
#         )
#
#     context["turnirs"] = Turnir.objects
#     return render(request, "tournament.html")


def reviews(request, user_id=None):
    """Code for reviews page"""
    bad_words = [""]
    try:
        user1 = User.objects.get(id=user_id)
        current_user = request.user
        id_topic = request.POST.get("id_topic")
        id_comm = request.POST.get("id_comm")

        if id_topic:
            id_table = Reviews(
                id_commentator=current_user,
                id_topic_comm=id_topic,
                text_id_comm=id_comm,
                id_commented=user1,
            )
            id_table.save()
            context = {"account": user1}
            return render(request, "reviews.html", context)
        else:
            return render(
                request, "reviews.html", {"error_message": "id_topic is required"}
            )
    except IntegrityError as e:
        return render(
            request, "reviews.html", {"error_message": f"IntegrityError: {e}"}
        )


def settings_page(request, user_id=None):
    """Code for settings page"""
    posts_liked = 0
    try:

        user = User.objects.get(id=user_id)
        niknem = NIKNEM.objects.filter(user=user).first()
        reviews = Reviews.objects.filter(id_commented=user_id)
        friends = Friend.get_friends(current_user=user)
        friends_count = friends.count()
        posts = Post1.objects.filter(author=user)
        author = Socials.objects.filter(author=user.id).last()
        achievement_text = Achievement.objects.filter(author_achievement=user.id).last()
        posts_count = posts.count()
        for post in posts:
            posts_liked += post.liked.all().count()
        context = {
            "account": user,
            "author": author,
            "niknem": niknem,
            "show_sett_acc_page": True,
            "reviews": reviews,
            "friends_count": friends_count,
            "post_count": posts_count,
            "achievement_text": achievement_text,
            "posts_liked": posts_liked
        }
        return render(request, "account_page.html", context)
    except User.DoesNotExist:
        context = {"error": "Такого пользователя нет"}
    return render(request, "account_page.html", context)


def my_profile(request):
    """Code for my_profile page"""
    print("123")
    user = request.user
    if user.is_authenticated:
        return redirect("user_profile", username=user.username)
    return redirect("register")


def logout_page(request):
    """Code for logout page"""
    logout(request)
    return redirect("login")


def profile(request, username=None):
    """Code for profile page"""
    friend_instance = Friend.objects.filter(current_user=request.user).first()
    friends_data = []
    if friend_instance:
        friends = friend_instance.users.all()
        for friend_obj in friends:
            friend_data = dict()
            friend_data["username"] = friend_obj.username
            friend_data["niknem"] = NIKNEM.objects.filter(user=friend_obj).first()
            friend_data["id"] = friend_obj.id
            friends_data.append(friend_data)

    if username:
        post_owner = get_object_or_404(User, username=username)
    else:
        post_owner = request.user

    args = {
        "post_owner": post_owner,
        "friends": friends_data,
    }

    if request.method == "POST":
        friend_id = request.POST.get("friend_id")
        friend = get_object_or_404(User, id=friend_id)
        Friend.lose_friend(request.user, friend)
        return redirect('profile_pk', username=username)

    return render(request, "profile.html", args)


def change_friends(request, operation, pk):
    """Code for change friends page"""
    friend = get_object_or_404(User, pk=pk)
    if operation == "add":
        Friend.make_friend(request.user, friend)
    return redirect("profile", username=friend.username)


def social_network(request):
    """Code for social_network page"""
    if request.method == "POST":
        vk_name = request.POST.get('vk_name')
        youtube_name = request.POST.get('youtube_name')
        discord_name = request.POST.get('discord_name')
        steam_name = request.POST.get('steam_name')
        achievement_text = request.POST.get('achievement_text')
        items = Socials.objects.filter(author=request.user.id)

        if len(items) == 0:
            social_table = Socials(author=request.user, link_vk=vk_name, link_youtube=youtube_name,
                                   link_discord=discord_name, link_steam=steam_name)
            social_table.save()
        else:
            item = items[0]
            if vk_name != '':
                item.link_vk = vk_name

                item.save(update_fields=['link_vk'])
            if youtube_name != '':
                item.link_youtube = youtube_name
                item.save(update_fields=['link_youtube'])
            if discord_name != '':
                item.link_discord = discord_name
                item.save(update_fields=['link_discord'])
            if steam_name != '':
                item.link_steam = steam_name
                item.save(update_fields=['link_steam'])

        if achievement_text and len(achievement_text) > 2:
            achievement_table = Achievement(author_achievement=request.user, achievements=achievement_text)
            achievement_table.save()
        else:
            messages.error(request, "Please , you need write more 10 symbol")

        data = {"message": "Data saved successfully"}
        return JsonResponse(data)

    else:
        messages.error(request, "Please, you need to do a login")

    return render(request, "social_network.html")


def turnir_page(request):
    """Code for turnir page"""
    context = dict()
    if request.method == "GET":
        page = "https://www.cybersport.ru/tournaments?interval=future"
        r = requests.get(page)
        text = r.text
        count = text.count('h3 class="title_hoDOT"')
        latestfound = 0
        lh3 = len('h3 class="title_hoDOT"')
        ld = len('<div class="value_lJuD+">')
        for i in range(count):
            latestfound = text.find('h3 class="title_hoDOT"', latestfound + 1)
            pos = latestfound + lh3 + 1
            name = ""
            while text[pos] != '<':
                name += text[pos]
                pos += 1
            print(name)
            date = ""
            datepos = text.find('<div class="value_lJuD+">', pos) + ld
            while text[datepos] != '<':
                date += text[datepos]
                datepos += 1
            date = date.split()[0]
            if len(date) < 10:
                continue
            d = date.split('.')
            day = int(d[0])
            month = int(d[1])
            year = int(d[2])
            Date = datetime_date(year, month, day)
            prize = ""
            prizepos = text.find('<div class="value_lJuD+">', datepos) + ld
            while text[prizepos] != '<':
                prize += text[prizepos]
                prizepos += 1
            if prize[0] != '$':
                prize = "-"
            if Turnir.objects.filter(date=Date, name=name, prize=prize).count() == 0:
                turnir = Turnir.objects.create(date=Date, name=name, prize=prize)
                turnir.save()
    context['turnirs'] = Turnir.objects.filter().all()
    context['account'] = request.user
    return render(request, 'tournament.html', context)


def charts(request):
    """Code for chat page"""
    user_data_2023 = list(
        User.objects.annotate(date=TruncDate("date_joined"))
        .filter(date_joined__year=2023)
        .values("date")
        .annotate(user_count=Count("id"))
        .order_by("date")
    )
    user_data_2024 = list(
        User.objects.annotate(date=TruncDate("date_joined"))
        .filter(date_joined__year=2024)
        .values("date")
        .annotate(user_count=Count("id"))
        .order_by("date")
    )
    return render(
        request,
        "charts.html",
        {"user_data_2023": user_data_2023, "user_data_2024": user_data_2024},
    )


def create_post(request):
    """Code for create post page"""
    context = {}
    print(request.user.username)
    if request.method == "POST":
        topic = request.POST.get("topic")
        texts = request.POST.get("texts")
        post_author = Post1(
            author=request.user.username,
            title=topic,
            text=texts,
            date=datetime.now(),
            # image=files_image,
        )
        post_author.save()
    return render(request, "create_post.html", context)


def api_v1_user_publish_post(request):
    """Code for api page"""
    if request.method != "POST":
        return HttpResponse(status=405)

    user = request.user

    if not user.is_authenticated:
        return HttpResponse(status=401)

    title = request.POST.get('title', None)
    text = request.POST.get('text', None)

    print(request.FILES)

    if title is None or text is None:
        return HttpResponse(status=400)

    if len(request.FILES) > 10:
        return HttpResponse(status=413)

    post = Post1(
        author=user,
        title=title,
        text=text,
        date=datetime.now()
    )

    post.save()

    for file_key in request.FILES:
        file = request.FILES[file_key]
        if file.size > 10 * 1024 * 1024:
            continue

        PostFile.save_file(post, file)

    return HttpResponse(status=200)


def home_page(request):
    """Code for home page"""
    context = {"account": request.user}
    if request.method == 'POST':
        form = SearchUserForm(request.POST)
        if form.is_valid():
            posts = Post1.objects.filter(author=User.objects.filter(username=form.cleaned_data['']))

            context['posts'] = []

            for post in posts:
                post_files = PostFile.objects.filter(post=post)
                post_username = post.author.username
                post = model_to_dict(post)
                post['files'] = []
                post['username'] = post_username
                post['is_liked'] = True if request.user in post['liked'] else False
                post['likes'] = len(post['liked'])
                for file in post_files:
                    file_dict = {'url': file.file.url, 'name': file.name, 'is_image': file.is_image}
                    post['files'].append(file_dict)

                print(post)

            context['posts'].append(post)

            username = form.cleaned_data['username']
            user = User.objects.get(username=username)
            posts = Post1.objects.filter(author=user)
            context = {"account": request.user, "posts": posts}
            return render(request, "homePage.html", context)
    else:
        form = SearchUserForm()

    query = request.GET.get('author', None)

    if query is None or query == '':
        friend_instance = Friend.objects.filter(current_user=request.user).first()
        if friend_instance:
            friends = friend_instance.users.all()
            posts = Post1.objects.filter(Q(author__in=friends) | Q(author=request.user)).order_by('date')
        else:
            posts = Post1.objects.filter(author=request.user)
    else:
        try:
            posts = Post1.objects.filter(author=User.objects.get(username=query))
        except (Post1.DoesNotExist, User.DoesNotExist):
            posts = Post1.objects.none()

    context['posts'] = []

    for post in posts:
        post_files = PostFile.objects.filter(post=post)
        post_username = post.author.username
        post = model_to_dict(post)
        post['files'] = []
        post['username'] = post_username
        post['is_liked'] = True if request.user in post['liked'] else False
        post['likes'] = len(post['liked'])
        for file in post_files:
            file_dict = {'url': file.file.url, 'name': file.name, 'is_image': file.is_image}
            post['files'].append(file_dict)

        context['posts'].append(post)

    print(context['posts'])

    """
    
        friend_posts = Post1.objects.filter(author__in=friends)
        context["friend_posts"] = friend_posts
        print(context["friend_posts"])"""
    context["form"] = form

    return render(request, "homePage.html", context)


def api_v1_user_send_message(request):
    """Code for api page"""
    if request.method != "POST":
        return HttpResponse(status=405)

    user = request.user

    if not user.is_authenticated:
        return HttpResponse(status=401)

    text = request.POST.get('text', None)
    recipient = request.POST.get('recipient', None)

    if text is None or recipient is None:
        return HttpResponse(status=400)

    message = Message()
    message.author = request.user
    message.text = text
    message.recipient = User.objects.filter(username=recipient).first()
    message.save()

    return HttpResponse(status=200)


def api_v1_user_update_chat(request):
    """Code for api page"""
    if request.method != "GET":
        return HttpResponse(status=405)

    user = request.user

    if not user.is_authenticated:
        return HttpResponse(status=401)

    recipient = request.GET.get('recipient', None)
    last_message = request.GET.get('last_message', None)

    if recipient is None or last_message is None:
        return HttpResponse(status=400)

    recipient = User.objects.filter(username=recipient).first()

    messages_list = Message.objects.filter(
        Q(author=user, recipient=recipient) | Q(author=recipient, recipient=user)).filter(id__gt=last_message).order_by(
        'timestamp')

    messages = []
    for message in messages_list:
        message_dict = {}
        message_dict['id'] = message.id
        message_dict['timestamp'] = int(message.timestamp.timestamp())
        author = message.author
        message_dict['author'] = author.username
        message_dict['text'] = message.text
        messages.append(message_dict)

    return JsonResponse(messages, safe=False)


def chat_page(request, username):
    """Code for chat page"""
    user = request.user

    context = {}

    if username is None:
        return HttpResponse(status=400)

    recipient = User.objects.filter(username=username).first()

    messages_list = list(
        Message.objects.filter(Q(author=user, recipient=recipient) | Q(author=recipient, recipient=user)).order_by(
            'timestamp'))

    context['messages'] = messages_list

    return render(request, 'chat.html', context)

def contacts_page(request):
    context={}
    return render(request,'contacts.html',context)


def messenger_page(request):
    request_user = request.user

    conversations = {}

    # Get all unique pairs of users with whom request_user has exchanged messages
    recipients = Message.objects.filter(author=request_user).values_list('recipient', flat=True).distinct()
    senders = Message.objects.filter(recipient=request_user).values_list('author', flat=True).distinct()
    all_participants = set(list(recipients) + list(senders))

    # Loop through all unique pairs of users and get the latest message for each conversation
    for recipient_id in all_participants:
        conversation_partner = User.objects.get(id=recipient_id)
        latest_message = Message.objects.filter(
            (Q(author=request_user) & Q(recipient=conversation_partner)) |
            (Q(author=conversation_partner) & Q(recipient=request_user))
        ).latest('timestamp')

        conversations[conversation_partner] = latest_message

    sorted_conversations = OrderedDict(sorted(conversations.items(), key=lambda x: x[1].timestamp, reverse=True))

    print(sorted_conversations)

    context = {}

    context['conversations'] = []

    for conv, msg in sorted_conversations.items():
        convs = {'user': conv.username, 'last_message': msg.text, 'timestamp': msg.timestamp}
        context['conversations'].append(convs)

    return render(request, "messenger.html", context)


def api_v1_user_toggle_like(request):
    """Code for avatar page"""
    if request.method != "POST":
        return HttpResponse(status=405)

    uploaded_file = request.FILES.get("avatar", None)

    if request.POST.get('post', None) is None:
        return HttpResponse(status=400)

    user = request.user

    if not user.is_authenticated:
        return HttpResponse(status=401)

    post = Post1.objects.get(id=request.POST['post'])

    print(post.liked.all(), request.user)

    if post.liked.filter(id=user.id).exists():
        post.liked.remove(user)
    else:
        post.liked.add(user)
    print(post.liked.all(), request.user)
    post.save()

    print(post.liked.all(), request.user)

    return HttpResponse(status=200)
