from django.shortcuts import render
from django.core.paginator import Paginator
from . import models


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page = request.GET.get("page", 1)

    items = paginator.page(page)
    return items


def index(request):
    items = paginate(models.Question.objects.get_new(), request)
    return render(request, "index.html", context={"pag_items": items})


def ask(request):
    return render(request, "ask.html")


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def question(request, question_id):
    item = models.Question.objects.get(question_id)
    answers = paginate(models.Answer.objects.get_by_question(question_id), request, 30)
    return render(
        request, "question.html", context={"question": item, "pag_items": answers}
    )


def hot(request):
    items = paginate(models.Question.objects.get_hot(), request)
    return render(request, "hot.html", context={"pag_items": items})


def tag(request, tag):
    items = paginate(models.Question.objects.get_by_tag(tag), request, 5)
    return render(request, "tag.html", context={"tag": tag, "pag_items": items})
