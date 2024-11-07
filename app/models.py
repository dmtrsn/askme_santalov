from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils.text import slugify


class QuestionManager(models.Manager):
    def get_all(self):
        return self.all()

    def get_by_tag(self, tag):
        return self.filter(tags__tag=tag)

    def get_hot(self):
        return self.annotate(
            like_count=Count("questionlike", filter=Q(questionlike__is_like=True))
            - Count("questionlike", filter=Q(questionlike__is_like=False))
        ).order_by("-like_count")

    def get_new(self):
        return self.all().order_by("-created_at")

    def get(self, question_id):
        return get_object_or_404(Question, id=question_id)


class AnswerManager(models.Manager):
    def get_by_question(self, question):
        return self.filter(question=question)

    def get_hot(self):
        return self.annotate(
            like_count=Count("questionlike", filter=Q(questionlike__is_like=True))
            - Count("questionlike", filter=Q(questionlike__is_like=False))
        ).order_by("-like_count")

    def get_new(self):
        return self.all().order_by("-created_at")


class Tag(models.Model):
    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.tag


class Question(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag)
    raiting = models.ManyToManyField(
        User, through="app.QuestionLike", related_name="QuestionLike"
    )

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_raiting_value(self):
        likes = self.questionlike_set.filter(is_like=True).count()
        dislikes = self.questionlike_set.filter(is_like=False).count()
        return likes - dislikes

    def get_answers(self):
        return Answer.objects.get_by_question(self)


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_like = models.BooleanField()

    class Meta:
        unique_together = ["question", "user"]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_correct = models.BooleanField(default=False)
    raiting = models.ManyToManyField(
        User, through="app.AnswerLike", related_name="AnswerLike"
    )

    objects = AnswerManager()

    def __str__(self):
        return self.question.title

    def get_raiting_value(self):
        likes = self.answerlike_set.filter(is_like=True).count()
        dislikes = self.answerlike_set.filter(is_like=False).count()
        return likes - dislikes


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_like = models.BooleanField()

    class Meta:
        unique_together = ["answer", "user"]


class Profile(models.Model):
    THEME_CHOICES = [
        ("light", "light"),
        ("dark", "dark"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True)
    theme = models.CharField(
        choices=THEME_CHOICES, max_length=10, default=THEME_CHOICES[0][0]
    )

    def __str__(self):
        return self.user.username
