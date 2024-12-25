from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("ask/", views.ask, name="ask"),
    path("login/", views.login, name="login"),
    path("logout/", views.staying_logout, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("question/<int:question_id>", views.question, name="question"),
    path("hot/", views.hot, name="hot"),
    path("tag/<str:tag>", views.tag, name="tag"),
    path("profile/edit", views.profile_edit, name="profile.edit"),
    path("question/like", views.question_like, name="question_like"),
    path("answer/like", views.answer_like, name="answer_like"),
    path("search/", views.search, name="search"),
    path("autocomplete", views.autocomplete, name="autocomplete"),
    path("staticpage", views.staticpage, name="staticpage")
]
