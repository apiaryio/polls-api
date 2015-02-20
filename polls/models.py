import datetime
import peewee
from rivr_peewee import Database


database = Database()


class Question(database.Model):
    question_text = peewee.CharField(max_length=140)
    published_at = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-published_at',)

    def __str__(self):
        return self.question_text

    def get_absolute_url(self):
        return '/questions/{}'.format(self.id)

    def as_dictionary(self):
        return {
            'question': self.question_text,
            'published_at': self.published_at.isoformat(),
            'url': self.get_absolute_url(),
            'choices': [choice.as_dictionary() for choice in self.choices],
        }


class Choice(database.Model):
    question = peewee.ForeignKeyField(Question, related_name='choices')
    choice_text = peewee.CharField(max_length=140)

    def __str__(self):
        return self.choice_text

    def as_dictionary(self):
        return {
            'choice': self.choice_text,
        }

