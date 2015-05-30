from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=140)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'published_at'

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices')
    choice_text = models.CharField(max_length=140)

    def __str__(self):
        return self.choice_text

    def vote(self):
        """
        Create a vote on this choice.
        """
        return Vote.objects.create(choice=self)

class Vote(models.Model):
    choice = models.ForeignKey(Choice, related_name='votes')
