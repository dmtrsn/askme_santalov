from django.core.management.base import BaseCommand, CommandError
from app import models
from django.contrib.auth.models import User
from django.conf import settings
import csv
import random

qa_path = settings.BASE_DIR / "questions_answers.csv"
qa_list = []
qa_len = 0

names_path = settings.BASE_DIR / "names.csv"
names_list = []
names_len = 0

questions_list = []
answers_list = []


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("ratio", nargs="+", type=int)

    def handle(self, *args, **options):
        with open(qa_path, newline="") as qa:
            reader = csv.reader(qa)
            qa_list = list(reader)[1:]

        questions_list, answers_list = zip(*qa_list)
        qa_len = len(qa_list)
        ratio = int(options["ratio"][0])

        with open(names_path, newline="") as n:
            reader = csv.reader(n)
            names_list = list(reader)
        names_len = len(names_list)

        users = []
        profiles = []
        tags = []
        questions = []
        answers = []
        q_likes = []
        a_likes = []

        users_count = ratio
        tags_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        likes_count = ratio * 200

        for i in range(ratio):
            username = names_list[random.randint(0, names_len - 1)][0] + "_" + str(i)
            user = User(username=username)
            tag = models.Tag(tag=f"Тег {i}")
            profile = models.Profile(user=user)
            users.append(user)
            tags.append(tag)
            profiles.append(profile)

        User.objects.bulk_create(users)
        models.Tag.objects.bulk_create(tags)
        models.Profile.objects.bulk_create(profiles)

        print("Inserted Users, Profiles, Tags")

        for i in range(questions_count):
            q_num = random.randint(0, qa_len - 1)
            q_user = users[random.randint(0, users_count - 1)]
            q_tags = [
                tags[random.randint(0, tags_count - 1)]
                for i in range(random.randint(1, 3))
            ]

            title = str(i) + ". " + questions_list[q_num]
            details = title
            title = title[:252] + "..."
            question = models.Question(
                title=title,
                details=details,
                author=q_user,
            )
            question.save()
            question.tags.add(*q_tags)
            questions.append(question)

        print("Inserted Questions")

        for i in range(answers_count):
            a_num = random.randint(0, qa_len - 1)
            a_user = users[random.randint(0, users_count - 1)]
            a_question = questions[random.randint(0, questions_count - 1)]

            content = str(i) + ". " + answers_list[a_num]
            answer = models.Answer(content=content, author=a_user, question=a_question)
            answers.append(answer)

        models.Answer.objects.bulk_create(answers)
        print("Inserted Answers")

        i = 0
        a_likes_used = set()
        q_likes_used = set()

        while i < likes_count:
            l_id = random.randint(0, users_count - 1)
            l_user = users[l_id]
            for_question = random.randint(0, 1)
            if for_question:
                q_id = random.randint(0, questions_count - 1)
                l_question = questions[q_id]
                if (l_id, q_id) not in q_likes_used:
                    like = models.QuestionLike(
                        user=l_user,
                        question=l_question,
                        is_like=bool(random.randint(0, 1)),
                    )
                    q_likes.append(like)
                    q_likes_used.add((l_id, q_id))
                else:
                    continue
            else:
                a_id = random.randint(0, answers_count - 1)
                l_answer = answers[a_id]
                if (l_id, a_id) not in a_likes_used:
                    like = models.AnswerLike(
                        user=l_user,
                        answer=l_answer,
                        is_like=bool(random.randint(0, 1)),
                    )
                    a_likes.append(like)
                    a_likes_used.add((l_id, a_id))
                else:
                    continue

            i += 1

        models.QuestionLike.objects.bulk_create(q_likes)
        models.AnswerLike.objects.bulk_create(a_likes)
        print("Inserted Likes")
        print("All insertions completed!")
