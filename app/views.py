from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import auth
from django.urls import reverse
from .forms import LoginForm, SignupForm, UpdateUserForm, UpdateProfileForm, AskForm, AnswerForm
from . import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page = request.GET.get("page", 1)

    items = paginator.page(page)
    return items


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
    return render(request, "index.html", context={"pag_items": items})


@login_required
def ask(request):
    form = AskForm(user=request.user)
    if request.method == "POST":
        form = AskForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save()
            return redirect("question", question.id)
    return render(request, "ask.html", {"form": form})


def login(request):
    next_url = request.GET.get("next", "index")

    if request.method == "POST":
        form = LoginForm(request.POST)
        next_url = request.POST.get("next", next_url)
        if form.is_valid():
            return authenticate(request, next_url, form.cleaned_data)
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form, "next": next_url})


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

    return render(request, "signup.html", {"form": form})


def question(request, question_id):
    item = models.Question.objects.get(question_id)
    answers = paginate(models.Answer.objects.get_by_question(question_id), request, 30)
    form = AnswerForm(user=request.user, question_id=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST, user=request.user, question_id=question_id)
        if form.is_valid():
            form.save()
            return redirect("question", question_id)
    return render(
        request, "question.html", context={"question": item, "pag_items": answers, "form": form, "question_id": question_id}
    )


def hot(request):
    items = paginate(models.Question.objects.get_hot(), request)
    return render(request, "hot.html", context={"pag_items": items})


def tag(request, tag):
    items = paginate(models.Question.objects.get_by_tag(tag), request, 5)
    return render(request, "tag.html", context={"tag": tag, "pag_items": items})


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
        request, "settings.html", {"user_form": user_form, "profile_form": profile_form}
    )
