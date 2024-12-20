from django import forms
from django.contrib.auth.models import User
from .models import Profile, Question, Answer
from django.contrib import auth
from django.contrib.admin.widgets import FilteredSelectMultiple


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        username = data.get("username")
        password = data.get("password")

        user = auth.authenticate(username=username, password=password)

        if not user:
            raise forms.ValidationError("invalid username or password")
        return data


class SignupForm(forms.ModelForm):
    password_confirmation = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField()

    class Meta:
        model = User
        fields = ("email", "username", "password")

    def clean(self):
        data = super().clean()

        if data.get("password") != data.get("password_confirmation"):
            self.add_error("password_confirmation", "passwords don`t match")

        return data

    def save(self):
        data = self.cleaned_data
        user = super().save(commit=False)

        user.set_password(data.get("password"))

        user.save()

        profile = Profile(user=user, avatar=data.get("avatar"))
        profile.save()

        return data


class UpdateUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("email", "username")


class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ("avatar", "theme")
        
    def save(self):
        data = self.cleaned_data
        profile = super().save(commit=False)
        
        avatar = data.get("avatar")
        if not avatar:
            avatar = "avatar.png"
            profile.avatar = avatar
        
        profile.save()
        return data


class AskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(AskForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Question
        fields = ("title", "details", "tags")

    def clean(self):
        data = super().clean()

        if len(data.get("tags")) > 3:
            self.add_error("tags", "There can be no more than 3 tags")

        return data

    def save(self):
        question = super(AskForm, self).save(commit=False)

        question.author = self.user
        question.save()

        return question


class AnswerForm(forms.ModelForm):
    def __init__(self, *args, user=None, question_id=None, **kwargs):
        self.user = user
        self.question_id = question_id
        super(AnswerForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Answer
        fields = ("content",)

    def save(self):
        answer = super(AnswerForm, self).save(commit=False)

        answer.author = self.user
        answer.question = Question.objects.get(question_id=self.question_id)

        answer.save()

        return answer
