from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.http import JsonResponse
from .models import Post, Category, Comment, Like, Profile


def home(request):
    posts = Post.objects.filter(status="published").order_by('-date')
    categories = Category.objects.all()
    category_id = request.GET.get('category')

    if category_id:
        posts = posts.filter(category_id=category_id)

    return render(request, "index.html", {
        "posts": posts,
        "categories": categories,
        "selected_category": category_id
    })


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        age = request.POST.get("age")
        bio = request.POST.get("bio", "")
        avatar = request.FILES.get("avatar")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Пользователь с таким именем уже существует!"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.create(
            user=user,
            age=age if age else 0,
            bio=bio,
            avatar=avatar
        )

        print(f" Пользователь {username} создан с профилем")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )

        if user:
            login(request, user)
            return redirect("home")

        return render(request, "login.html", {
            "error": "Неверный логин или пароль"
        })

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def create_post(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        category_id = request.POST.get("category")
        status = request.POST.get("status")
        img = request.FILES.get("img")

        print(f" Имя: {name}")
        print(f" Описание: {description}")
        print(f"Категория ID: {category_id}")
        print(f" Статус: {status}")
        print(f" Пользователь: {request.user} (ID: {request.user.id})")

        if not name or not description or not category_id:
            categories = Category.objects.all()

            return render(request, "create_post.html", {
                "categories": categories,
                "error": "Заполните все обязательные поля!"
            })

        try:
            category = Category.objects.get(id=category_id)

        except Category.DoesNotExist:
            return render(request, "create_post.html", {
                "categories": Category.objects.all(),
                "error": "Выбранная категория не существует!"
            })

        try:
            post = Post.objects.create(
                name=name,
                description=description,
                img=img,
                user=request.user,
                category=category,
                status=status or "draft"
            )

            print(f" Пост создан: {post}")

            return redirect("home")

        except Exception as e:
            print(f" Ошибка: {e}")

            return render(request, "create_post.html", {
                "categories": Category.objects.all(),
                "error": f"Ошибка: {str(e)}"
            })

    categories = Category.objects.all()

    if not categories.exists():
        return render(request, "create_post.html", {
            "error": "Сначала создайте категории в админ-панели!"
        })

    return render(request, "create_post.html", {
        "categories": categories
    })


@login_required
def drafts(request):

    posts = Post.objects.filter(
        user=request.user,
        status="draft"
    ).order_by("-date")

    return render(request, "drafts.html", {
        "posts": posts
    })


@login_required
def edit_post(request, id):

    post = get_object_or_404(
        Post,
        id=id,
        user=request.user
    )

    categories = Category.objects.all()

    if request.method == "POST":

        name = request.POST.get("name")
        description = request.POST.get("description")
        category_id = request.POST.get("category")
        status = request.POST.get("status")

        if not name or not description or not category_id:
            return render(request, "edit_post.html", {
                "post": post,
                "categories": categories,
                "error": "Заполните все обязательные поля!"
            })

        post.name = name
        post.description = description
        post.category_id = category_id

        if request.FILES.get("img"):
            post.img = request.FILES.get("img")

        if status in ["draft", "published"]:
            post.status = status

        post.save()

        if post.status == "draft":
            return redirect("drafts")

        return redirect("post", id=post.id)

    return render(request, "edit_post.html", {
        "post": post,
        "categories": categories
    })


def post_detail(request, id):

    post = get_object_or_404(
        Post,
        id=id
    )

    comments = Comment.objects.filter(
        post=post,
        parent=None
    )

    liked = False

    if request.user.is_authenticated:

        liked = Like.objects.filter(
            user=request.user,
            post=post
        ).exists()

    return render(request, "post.html", {
        "post": post,
        "comments": comments,
        "liked": liked
    })


@login_required
def profile(request):

    posts = Post.objects.filter(
        user=request.user
    )

    return render(request, "profile.html", {
        "posts": posts
    })





@login_required
def edit_profile(request):

    profile = request.user.profile

    if request.method == "POST":

        profile.age = request.POST.get("age")
        profile.bio = request.POST.get("bio")

        if request.FILES.get("avatar"):
            profile.avatar = request.FILES.get("avatar")

        profile.save()

        return redirect("profile")

    return render(request, "edit_profile.html", {
        "profile": profile
    })


@login_required
def add_comment(request, id):

    post = get_object_or_404(
        Post,
        id=id
    )

    if request.method == "POST":

        text = request.POST.get("text")
        parent_id = request.POST.get("parent")

        parent = None

        if parent_id:

            parent = get_object_or_404(
                Comment,
                id=parent_id,
                post=post
            )

        comment = Comment.objects.create(
            post=post,
            user=request.user,
            text=text,
            parent=parent
        )

        return JsonResponse({
            "id": comment.id,
            "username": comment.user.username,
            "text": comment.text,
            "date": comment.date.strftime("%d.%m.%Y %H:%M"),
            "parent": parent.id if parent else None
        })

    return JsonResponse({
        "error": "Неверный запрос"
    }, status=400)


@login_required
def like_post(request, id):

    post = get_object_or_404(
        Post,
        id=id
    )

    like = Like.objects.filter(
        user=request.user,
        post=post
    )

    if like.exists():

        like.delete()

    else:

        Like.objects.create(
            user=request.user,
            post=post
        )

    return redirect(
        "post",
        id=id
    )


@login_required
def delete_post(request, id):

    post = get_object_or_404(
        Post,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        post.delete()

        return redirect("home")

    return render(request, "delete_post.html", {
        "post": post
    })