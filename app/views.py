import jwt
import time
from cent import *
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.contrib import auth
from django.urls import reverse
from .forms import (
    LoginForm,
    SignupForm,
    UpdateUserForm,
    UpdateProfileForm,
    AskForm,
    AnswerForm,
)
from . import models
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.postgres.search import SearchVector
from django.http import JsonResponse, HttpResponse
from django.conf import settings as conf_settings
from django.db.models import Q
from django.core.cache import cache

client = Client(
    conf_settings.CENTRIFUGO_API_URL, conf_settings.CENTRIFUGO_API_KEY, timeout=1
)


def generate_centrifugo_data(user_id, channel):
    return {
        "centrifugo": {
            "token": jwt.encode(
                {"sub": str(user_id), "exp": int(time.time()) + 10 * 60},
                conf_settings.CENTRIFUGO_TOKEN_HMAC_SECRET,
                algorithm="HS256",
            ),
            "ws_url": conf_settings.CENTRIFUGO_WS_URL,
            "channel": channel,
            "user_id": user_id,
        }
    }


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page = request.GET.get("page", 1)

    items = paginator.page(page)
    return items


def cache_popular_users():
    cache_key = "popular_users"
    users = models.Profile.objects.get_popular_users()
    cache.set(cache_key, users, 604800)


def get_popular_users():
    cache_key = "popular_users"
    users = cache.get(cache_key)
    return users


def cache_popular_tags():
    cache_key = "popular_tags"
    tags = models.Tag.objects.get_popular_tags()
    cache.set(cache_key, tags, 7776000)


def get_popular_tags():
    cache_key = "popular_tags"
    tags = cache.get(cache_key)
    return tags


def authenticate(request, next_url, form_data):
    user = auth.authenticate(request, **form_data)
    auth.login(request, user)
    return redirect(next_url)


def edit_profile_success(request, user_form, profile_form):
    user_form.save()
    profile_form.save()
    messages.success(request, "Your profile is updated successfully")


def index(request):
    items = paginate(models.Question.objects.get_new(), request)
    return render(
        request,
        "index.html",
        context={
            "pag_items": items,
            "popular_tags": get_popular_tags(),
            "popular_users": get_popular_users(),
        },
    )


@login_required
def ask(request):
    form = AskForm(user=request.user)
    if request.method == "POST":
        form = AskForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save()
            return redirect("question", question.id)
    return render(
        request,
        "ask.html",
        {
            "form": form,
            "popular_tags": get_popular_tags(),
            "popular_users": get_popular_users(),
        },
    )


def search(request):
    query = request.GET.get("q")
    results = ""
    if query:
        results = models.Question.objects.annotate(q=SearchVector('title') + SearchVector('details')).filter(q=query)
    questions = paginate(results, request)
    return render(
        request,
        "search.html",
        context={
            "pag_items": questions,
            "popular_tags": get_popular_tags(),
            "popular_users": get_popular_users(),
        },
    )


def autocomplete(request):
    query = request.GET.get('q')
    if not query:
        return JsonResponse({'results': []})
    
    questions = models.Question.objects.annotate(q=SearchVector('title') + SearchVector('details')).filter(q=query)[:10]
    results = [{'id': q.id, 'title': q.title} for q in questions]
    return JsonResponse({'results': results})


def login(request):
    next_url = request.GET.get("next", "index")

    if request.method == "POST":
        form = LoginForm(request.POST)
        next_url = request.POST.get("next", next_url)
        if form.is_valid():
            return authenticate(request, next_url, form.cleaned_data)
    else:
        form = LoginForm()
    return render(
        request,
        "login.html",
        {
            "form": form,
            "next": next_url,
            "popular_tags": get_popular_tags(),
            "popular_users": get_popular_users(),
        },
    )


def staying_logout(request):
    next_url = request.GET.get("next", "index")
    logout(request)
    return redirect(next_url)


def signup(request):
    form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            auth_data = form.save()
            return authenticate(request, auth_data)

    return render(
        request,
        "signup.html",
        {
            "form": form,
            "popular_tags": get_popular_tags(),
            "popular_users": get_popular_users(),
        },
    )


def question(request, question_id):
    item = models.Question.objects.get(question_id)
    answers = paginate(models.Answer.objects.get_by_question(question_id), request, 30)
    form = AnswerForm(user=request.user, question_id=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST, user=request.user, question_id=question_id)
        if form.is_valid():
            answer = form.save()
            print(answer.author.username)
            client.publish(
                PublishRequest(
                    channel=f"question.{question_id}",
                    data={
                        "author_avatar": answer.author.profile.avatar.url,
                        "content": answer.content,
                        "is_correct": answer.is_correct,
                        "username": answer.author.username,
                        "raiting": 0,
                        "q_author": answer.question.author.id,
                        "answers_count": item.get_answers().count(),
                    },
                )
            )
            return redirect("question", question_id)
    is_liked, is_dislaked = False, False
    if request.user.is_authenticated:
        is_liked, is_dislaked = models.QuestionLike.objects.get_likes_and_dislikes(
            request.user, item
        )
    return render(
        request,
        "question.html",
        context={
            "question": item,
            "pag_items": answers,
            "form": form,
            "question_id": question_id,
            "is_liked": is_liked,
            "is_dislaked": is_dislaked,
            "popular_tags": get_popular_tags(),
            "popular_users": get_popular_users(),
            **generate_centrifugo_data(request.user.id, f"question.{question_id}"),
        },
    )


def hot(request):
    items = paginate(models.Question.objects.get_hot(), request)
    return render(
        request,
        "hot.html",
        context={
            "pag_items": items,
            "popular_tags": get_popular_tags(),
            "popular_users": get_popular_users(),
        },
    )


def tag(request, tag):
    items = paginate(models.Question.objects.get_by_tag(tag), request, 5)
    return render(
        request,
        "tag.html",
        context={
            "tag": tag,
            "pag_items": items,
            "popular_tags": get_popular_tags(),
            "popular_users": get_popular_users(),
        },
    )


@login_required
def profile_edit(request):
    user_form = UpdateUserForm(instance=request.user)
    profile_form = UpdateProfileForm(instance=request.user.profile)
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            edit_profile_success(request, user_form, profile_form)
    return render(
        request,
        "settings.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "popular_tags": get_popular_tags(),
            "popular_users": get_popular_users(),
        },
    )


@csrf_protect
@login_required
def question_like(request):
    id = request.POST.get("question_id")
    question = models.Question.objects.get_or_404_json(int(id))
    raiting_type = request.POST.get("raiting_type")
    if not question:
        return JsonResponse({"404": "object does not exist"})
    is_liked, is_dislaked = models.QuestionLike.objects.toggle_like(
        user=request.user, question=question, raiting_type=raiting_type
    )  # raiting_type := {"Like", "Dislike"}
    raiting = question.get_raiting_value()
    return JsonResponse(
        {"raiting": raiting, "is_liked": is_liked, "is_dislaked": is_dislaked}
    )


@csrf_protect
@login_required
def answer_like(request):
    id = request.POST.get("answer_id")
    answer = models.Answer.objects.get_or_404_json(int(id))
    if not answer:
        return JsonResponse({"404": "object does not exist"})
    if answer.question.author != request.user:
        return JsonResponse({"404": "you cant mark this answer"})
    is_marked_right = models.Answer.objects.toggle_right(answer=answer)
    return JsonResponse({"is_maked_right": is_marked_right})


def staticpage(request):
    return HttpResponse(
        '<html> <head> <title>Welcome to nginx!</title><style>\
                            html { color-scheme: light dark; } body { width: 35em; margin: 0 auto;\
                            font-family: Tahoma, Verdana, Arial, sans-serif; } </style>\
                            </head> <body> <h1>Welcome to nginx!</h1> <p>If you see this page, the nginx web server is successfully installed and\
                            working. Further configuration is required.</p> <p>For online documentation and support please refer to\
                            <a href="http://nginx.org/">nginx.org</a>.<br/>\
                            Commercial support is available at\
                            <a href="http://nginx.com/">nginx.com</a>.</p>\
                            <p><em>Thank you for using nginx.</em></p>\
                            </body></html>'
    )
