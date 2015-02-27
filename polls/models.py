from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=140)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=140)

    def __str__(self):
        return self.choice_text

    @property
    def votes(self):
        return self.vote_set.count()


class Vote(models.Model):
    choice = models.ForeignKey(Choice)

