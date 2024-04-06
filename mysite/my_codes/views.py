"""imports from other files + libraries"""
from datetime import datetime
from io import BytesIO
from sqlite3 import IntegrityError

from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, RegisterForm, RememberPassword
from .forms import SearchUserForm
from .models import nickname, Friend, Turnir, Reviews, Post1


def register_page(request):
    """Module providing a function for register_page."""
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

            nickname_item = nickname(user=user)
            nickname_item.save()

            messages.success(request, "You have signed up successfully.")
            print(messages.success(request, "You have signed up successfully."))
            return redirect("mainssss")
        return render(request, "register.html", {"form": form})


def nickname_page(request):
    """Module providing a function for nickname_page."""
    username = request.session.get("username")
    email = request.session.get("email")
    print(request.user.username)
    try:
        user = User.objects.get(username=username, email=email)
    except User.DoesNotExist:
        return HttpResponse("User not found")

    context = {}

    if request.method == "POST":
        nickname = request.POST.get("nickname")
        if not nickname:
            context["error"] = "Введите никнейм"
        else:
            request.session["nickname"] = nickname
            context["nickname"] = nickname

            nickname_item, created = nickname.objects.get_or_create(user=user)
            nickname_item.nickname = nickname
            nickname_item.save()

            context["good"] = "Никнейм успешно сохранен"

        if user:
            context["user_id"] = user.id

    return render(request, "mainssss.html", context)


def login_page(request):
    """Module providing a function for login_page."""
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
    """Module providing a function for open_page."""
    print(request.user.username)
    if request.user.is_authenticated:
        return redirect("homePage")
    context = {
        "text": "Добро пожаловать в мир возможностей и новых знакомств!"
                "Здесь каждый может найти не только друзей, "
                "но и надежных игровых партнеров для захватывающих приключений. "
                "Давайте создадим незабываемые "
                "воспоминания вместе! Добро пожаловать в наше сообщество, "
                "где дружба и игры ждут вас на каждом шагу. "
                "Присоединяйтесь и откройте для себя мир новых возможностей!"
    }

    return render(request, "open_page.html", context)


def api_v1_user_upload_avatar(request):
    """Module providing a function for user_avatar."""
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

    try:
        with BytesIO(uploaded_file.read()) as f:
            image = Image.open(f)
            image.verify()

            image = Image.open(f)

            image = image.resize((256, 256), Image.Resampling.LANCZOS)

            path = MEDIA_ROOT + "/avatars/" + str(user.id) + ".png"

            image.save(path)
        return HttpResponse(status=200)
    except [UnidentifiedImageError, EOFError, DecompressionBombError]:
        return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=500)


def account_page(request, username):
    """Module providing a function for account_page."""
    social_links = request.session.get("social_links", {})
    instagram_link = social_links.get("instagram_link")
    twitter_link = social_links.get("twitter_link")
    twitch_link = social_links.get("twitch_link")
    codepen_link = social_links.get("codepen_link")
    try:
        user = User.objects.filter(username=username).first()
        reviews = Reviews.objects.filter(id_commented=user.id)
        friends = Friend.get_friends(current_user=user)
        friends_count = friends.count()
        if not user:
            raise User.DoesNotExist
        nickname = nickname.objects.filter(user=user).first()
        context = {
            "twitter_link": twitter_link,
            "twitch_link": twitch_link,
            "codepen_link": codepen_link,
            "account": user,
            "nickname": nickname.nickname if nickname is not None else "No NickName",
            "is_owner_of_account": user == request.user,
            "reviews": reviews,
            "friends_count": friends_count
        }
        return render(request, "account_page.html", context)

    except User.DoesNotExist:
        context = {"error": "Такого пользователя нет"}
        return render(request, "account_page.html", context)


def remember_password(request):
    """Module providing a function remember_password page."""
    form = RememberPassword()
    if request.method == "POST":
        form = RememberPassword(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = User.objects.filter(username=username.lower(), email=email.lower()).first()
            if user:
                user.set_password(password)
                user.save()
                messages.success(
                    request, f"Password changed successfully for {user.username}!")
                return redirect("login")
            else:
                messages.error(request, "User not found with the provided username and email")

    return render(request, "remember_password.html", {"form": form})


def achievements(request):
    """Module providing a function for achievements."""
    return render(request, "Achievements.html")


def find_users_page(request):
    """Module providing a function for find_users_page."""
    context = {}
    if request.method == "POST":
        form = SearchUserForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]
            page = 0
        else:
            query = ""
            page = 0
    else:
        query = request.GET.get("query", "")
        page = max(0, int(request.GET.get("page", 1)) - 1)

    all_accounts_count = nickname.objects.filter(nickname__contains=query).count()

    current_user = request.user
    accounts = nickname.objects.filter(niknem__contains=query).exclude(
        user=current_user)[page * 10: page * 10 + 10]

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


def tournament_page(request):
    """Module providing a function tournament_page."""
    context = {}
    if request.method == "POST":
        date = request.POST.get("Date")
        name = request.POST.get("Name")
        participants = request.POST.get("Participants")
        placetowatch = request.POST.get("PlaceToWatch")
        t = Turnir.objects.create(
            date=date, name=name, participants=participants, placeToWatch=placetowatch)

    context["turnirs"] = Turnir.objects
    return render(request, "tournament.html")


def reviews(request, user_id=None):
    """Module providing a function for reviews."""
    bad_words = ['']
    try:
        user1 = User.objects.get(id=user_id)
        current_user = request.user
        id_topic = request.POST.get("id_topic")
        id_comm = request.POST.get("id_comm")

        if id_topic:
            id_table = Reviews(
                id_commentator=current_user, id_topic_comm=id_topic,
                text_id_comm=id_comm, id_commented=user1
            )
            id_table.save()
            context = {"account": user1}
            return render(request, "reviews.html", context)
        else:
            return render(request, "reviews.html", {"error_message": "id_topic is required"})
    except IntegrityError as e:
        return render(request, "reviews.html", {"error_message": f"IntegrityError: {e}"})


def settings_page(request, user_id=None):
    """Module providing a function for settings_page."""
    try:
        user = User.objects.get(id=user_id)
        nickname = nickname.objects.filter(user=user).first()
        reviews = Reviews.objects.filter(id_commented=user_id)
        context = {"account": user,
                   "nickname": nickname,
                   "show_sett_acc_page": True,
                   'reviews': reviews}
        return render(request, "account_page.html", context)
    except User.DoesNotExist:
        context = {"error": "Такого пользователя нет"}
    return render(request, "account_page.html", context)


def my_profile(request):
    """Module providing a function for profile page."""
    print("123")
    user = request.user
    if user.is_authenticated:
        return redirect("user_profile", username=user.username)
    return redirect("register")


def logout_page(request):
    """Module providing a function for logout_page."""
    logout(request)
    return redirect("login")


def profile(request, username=None):
    """Module providing a function about profile."""
    friend_instance = Friend.objects.filter(current_user=request.user).first()
    friends_data = []

    if friend_instance:
        friends = friend_instance.users.all()
        for friend_obj in friends:
            friend_data = dict()
            friend_data["username"] = friend_obj.username
            friend_data["nickname"] = nickname.objects.filter(user=friend_obj).first()
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

    return render(request, "profile.html", args)


def change_friends(request, operation, pk):
    """Module providing a function for change_friends page."""
    friend = get_object_or_404(User, pk=pk)
    if operation == "add":
        Friend.make_friend(request.user, friend)
    return redirect("profile", username=friend.username)


def social_network(request):
    """Module providing a function social_network."""
    context = {}
    if request.method == "POST":
        instagram_link = request.POST.get("instagram_link")
        twitter_link = request.POST.get("twitter_link")
        twitch_link = request.POST.get("twitch_link")
        codepen_link = request.POST.get("codepen_link")

        social_links = {
            "instagram_link": instagram_link,
            "twitter_link": twitter_link,
            "twitch_link": twitch_link,
            "codepen_link": codepen_link,
        }
        request.session["social_links"] = social_links
        context = social_links
    return render(request, "social_network.html", context)


def charts(request):
    """Module providing a function for charts."""
    user_data_2023 = list(
        User.objects.annotate(month=TruncMonth('date_joined')).filter(
            date_joined__year=2023).values('month').annotate(
            user_count=Count('id')).order_by('month'))
    user_data_2024 = list(
        User.objects.annotate(month=TruncMonth('date_joined')).filter(
            date_joined__year=2024).values('month').annotate(
            user_count=Count('id')).order_by('month'))
    return render(request, 'charts.html', {"user_data_2023": user_data_2023,
                                           "user_data_2024": user_data_2024})


def create_post(request):
    """Module providing a function for create_post page."""
    context = {}
    if request.method == "POST":
        topic = request.POST.get('topic')
        texts = request.POST.get('texts')
        files_image = request.FILES.get('file_image')
        post_author = Post1(
            author=request.user, title=topic, text=texts, date=datetime.now(), image=files_image)
        post_author.save()
    return render(request, "create_post.html", context)


def home_page(request):
    """Module providing a function for home_page."""
    context = {
        'account': request.user
    }
    posts = Post1.objects.filter(author=request.user)
    context["posts"] = posts

    friend_instance = Friend.objects.filter(current_user=request.user).first()

    if friend_instance:
        friends = friend_instance.users.all()
        friend_posts = Post1.objects.filter(author__in=friends)
        context["friend_posts"] = friend_posts

    return render(request, 'homePage.html', context)
