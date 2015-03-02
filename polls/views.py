from django.http import HttpResponse

from polls.models import Question, Choice, Vote

from polls.resource import Action, Resource, CollectionResource, SingleObjectMixin
from polls.settings import CAN_CREATE_QUESTION, CAN_DELETE_QUESTION, CAN_VOTE_QUESTION


class RootResource(Resource):
    uri = '/'

    def get_relations(self):
        return {
            'questions': QuestionCollectionResource(),
        }

    def can_embed(self, relation):
        return False


class QuestionResource(Resource, SingleObjectMixin):
    model = Question

    def get_uri(self):
        return '/questions/{}'.format(self.get_object().pk)

    def get_attributes(self):
        question = self.get_object()

        return {
            'question': question.question_text,
            'published_at': question.published_at.isoformat(),
        }

    def get_relations(self):
        choices = self.get_object().choice_set.all()

        def choice_resource(choice):
            resource = ChoiceResource()
            resource.obj = choice
            return resource

        return {
            'choices': map(choice_resource, choices),
        }

    def get_actions(self):
        actions = {}

        if CAN_DELETE_QUESTION:
            actions['delete'] = Action(method='DELETE', attributes=None)

        return actions

    def delete(self, request, *args, **kwargs):
        if not CAN_DELETE_QUESTION:
            return self.http_method_not_allowed(request)

        self.get_object().delete()
        return HttpResponse(status=204)


class ChoiceResource(Resource, SingleObjectMixin):
    model = Choice

    def get_uri(self):
        choice = self.get_object()
        return '/questions/{}/choices/{}'.format(choice.question.pk, choice.pk)

    def get_attributes(self):
        choice = self.get_object()

        return {
            'choice': choice.choice_text,
            'votes': choice.votes,
        }

    def get_actions(self):
        actions = {}

        if CAN_VOTE_QUESTION:
            actions['vote'] = Action(method='POST', attributes=None)

        return actions

    def post(self, request, *args, **kwargs):
        if not CAN_VOTE_QUESTION:
            return self.http_method_not_allowed(request)

        choice = self.get_object()
        Vote(choice=choice).save()
        response = self.get(request)
        response.status_code = 201
        response['Location'] = self.get_uri()
        return response


class QuestionCollectionResource(CollectionResource):
    resource = QuestionResource
    model = Question
    relation = 'questions'
    uri = '/questions'

    def get_actions(self):
        actions = {}

        if CAN_CREATE_QUESTION:
            actions['create'] = Action(method='POST', attributes=('question', 'choices'))

        return actions

    def post(self, request):
        if not CAN_CREATE_QUESTION:
            return self.http_method_not_allowed(request)

        body = json.loads(request.body)
        question_text = body.get('question')
        choices = body.get('choices')

        if not question_text or not isinstance(choices, list):
            return HttpResponse(status=400)

        question = Question(question_text=question_text)
        question.save()
        for choice_text in choices:
            Choice(question=question, choice_text=choice_text).save()

        resource = self.resource()
        resource.obj = question
        response = resource.get(request)
        response.status_code = 201
        response['Location'] = resource.get_uri()
        return response
