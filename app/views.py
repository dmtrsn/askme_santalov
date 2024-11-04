from django.shortcuts import render
from django.core.paginator import Paginator

QUESTIONS = []
for i in range(1, 30):
    QUESTIONS.append({"title": "title " + str(i), "id": i - 1, "text": "text" + str(i)})


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page = request.GET.get("page", 1)

    items = paginator.page(page)
    return items


def index(request):
    items = paginate(QUESTIONS, request)
    return render(request, "index.html", context={"items": items})


def ask(request):
    return render(request, "ask.html")


def login(request):
    return render(request, "login.html")


def signup(request):
    return render(request, "signup.html")


def question(request, question_id):
    item = QUESTIONS[question_id]
    return render(request, "question.html", context={"question": item})


def hot(request):
    items = paginate(QUESTIONS[:11], request, 5)
    return render(request, "hot.html", context={"items": items})


def tag(request, tag):
    items = paginate(QUESTIONS[14:20], request, 5)
    return render(request, "tag.html", context={"tag": tag, "items": items})
