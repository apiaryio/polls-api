from rivr.views import RESTView
from rivr.http import Http404, RESTResponse

from polls.models import Question, Choice, Vote
from polls.settings import *


class RootView(RESTView):
    def get(self, request):
        return {
            'questions_url': '/questions',
        }


class QuestionListView(RESTView):
    def get(self, request):
        return [q.as_dictionary() for q in Question.select()]

    def post(self, request):
        if not CAN_CREATE_QUESTION:
            return self.http_method_not_allowed(request)

        body = request.POST

        if 'question' not in body or 'choices' not in body:
            return RESTResponse(request, {'error': 'Missing question and choices'}, status=400)

        question = Question.create(question_text=body['question'])
        for choice_text in body['choices']:
            Choice.create(question=question, choice_text=choice_text)

        response = RESTResponse(request, question.as_dictionary(), status=201)
        response.headers['Location'] = question.get_absolute_url()
        return response


class QuestionDetailView(RESTView):
    def get_last_modified(self, request):
        question = self.get_object()
        return question.published_at

    def get_object(self):
        try:
            question = Question.get(id=self.kwargs['pk'])
        except Question.DoesNotExist:
            raise Http404

        return question

    def get(self, request, *args, **kwargs):
        return self.get_object().as_dictionary()

    def delete(self, request, *args, **kwargs):
        if not CAN_DELETE_QUESTION:
            return self.http_method_not_allowed(request)

        choice = self.get_object()
        choice.delete_instance()

class ChoiceDetailView(RESTView):
    def get_object(self):
        try:
            choice = Choice.get(id=self.kwargs['pk'])
        except Choice.DoesNotExist:
            raise Http404

        return choice

    def post(self, request, *args, **kwargs):
        if not CAN_VOTE_QUESTION:
            return self.http_method_not_allowed(request)

        choice = self.get_object()
        Vote.create(choice=choice)

        response = RESTResponse(request, None, status=201)
        response.headers['Location'] = choice.question.get_absolute_url()
        return response

