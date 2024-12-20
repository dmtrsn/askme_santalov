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
        return get_object_or_404(Question, pk=question_id)

    def get_or_404_json(self, question_id):
        if self.filter(pk=question_id).exists():
            return self.filter(pk=question_id).first()
        else:
            return False


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

    def get_or_404_json(self, answer_id):
        if self.filter(pk=answer_id).exists():
            return self.filter(pk=answer_id).first()
        else:
            return False

    def toggle_right(self, answer):
        is_marked_right = False
        if answer.is_correct:
            answer.is_correct = False
            answer.save()
        else:
            is_marked_right = True
            answer.is_correct = True
            answer.save()
        return is_marked_right


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


class QuestionLikeManager(models.Manager):
    def get_likes_and_dislikes(self, user, question):
        is_like = False
        is_dislike = False
        if self.filter(user=user, question=question).exists():
            obj = self.get(user=user, question=question)
            if obj.is_like:
                is_like = True
            else:
                is_dislike = True
        return (is_like, is_dislike)

    def toggle_like(self, user, question, raiting_type):
        is_liked = False
        is_dislaked = False
        is_like = True
        if raiting_type == "Dislike":
            is_like = False
        if self.filter(user=user, question=question).exists():
            like = self.get(user=user, question=question)
            if like.is_like and not is_like:
                is_liked = False
                is_dislaked = True
                like.is_like = False
                like.save()
            elif not like.is_like and is_like:
                is_liked = True
                is_dislaked = False
                like.is_like = True
                like.save()
            elif (like.is_like and is_like) or (not like.is_like and not is_like):
                is_liked = False
                is_dislaked = False
                self.filter(user=user, question=question).delete()
        else:
            if is_like:
                is_liked = True
                is_dislaked = False
            else:
                is_liked = False
                is_dislaked = True
            self.create(user=user, question=question, is_like=is_like)
        return (is_liked, is_dislaked)


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_like = models.BooleanField()

    objects = QuestionLikeManager()

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
    avatar = models.ImageField(
        null=True, blank=True, default="avatar.png", upload_to="avatar/%Y/%m/%d"
    )
    theme = models.CharField(
        choices=THEME_CHOICES, max_length=10, default=THEME_CHOICES[0][0]
    )

    def __str__(self):
        return self.user.username
