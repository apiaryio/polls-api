import os
import json
from hashlib import sha1

try:
    from ldclient import LDClient
except ImportError:
    LDClient = None

from polls.settings import CAN_CREATE_QUESTION, CAN_DELETE_QUESTION, CAN_VOTE_QUESTION

if LDClient and 'LD_API_KEY' in os.environ:
    ld_client = LDClient(os.environ['LD_API_KEY'])
else:
    ld_client = None


with open('initial_data.json') as fp:
    initial_data = json.load(fp)
initial_questions = filter(lambda m: m['model'] == 'polls.question', initial_data)
initial_question_pks = map(lambda m: m['pk'], initial_questions)


def is_feature_enabled(feature_key, request, default=False):
    if ld_client:
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        key = sha1(ip_address).hexdigest()
        user = {'key': key}
        return ld_client.toggle(feature_key, user, default)

    return default


def can_create_question(request):
    return is_feature_enabled('question.create', request, CAN_CREATE_QUESTION)


def can_delete_question(question, request):
    if question.pk in initial_question_pks:
        return False

    return is_feature_enabled('question.delete', request, CAN_DELETE_QUESTION)


def can_vote_choice(request):
    return is_feature_enabled('choice.vote', request, CAN_VOTE_QUESTION)

