import json
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from polls.models import Question, Vote


class Command(BaseCommand):
    help = 'Removes questions older than an hour except initial data'

    def handle(self, *args, **kwargs):
        with open('polls/fixtures/initial_data.json') as fp:
            initial_data = json.load(fp)

        initial_questions = filter(
            lambda m: m['model'] == 'polls.question', initial_data
        )
        initial_question_pks = map(lambda m: m['pk'], initial_questions)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        qs = Question.objects.exclude(id__in=initial_question_pks).filter(
            published_at__lt=one_hour_ago
        )

        print('Deleting {} questions'.format(qs.count()))
        qs.delete()

        qs = Vote.objects.all()

        print('Deleting {} votes'.format(qs.count()))
        qs.delete()
