import json

from django.test import TestCase, Client
from django.http import HttpRequest

from polls.resource import Action, Resource
from polls.views import QuestionResource
from polls.models import Question, Choice, Vote


class ResourceTestCase(TestCase):
    def test_json_includes_allow_header(self):
        class TestAllowActionResource(Resource):
            def get_actions(self):
                return { 'delete': Action(method='DELETE', attributes=None) }

        request = HttpRequest()
        request.META['HTTP_ACCEPT'] = 'application/json'
        response = TestAllowActionResource().get(request)

        self.assertEqual(response['Allow'], 'HEAD, GET, DELETE')

    def test_invalid_accept_header(self):
        class TestResource(Resource):
            pass

        request = HttpRequest()
        request.META['HTTP_ACCEPT'] = 'application'
        response = TestResource().get(request)

        self.assertEqual(response.status_code, 200)


class RootTestCase(TestCase):
    def test_supports_cors(self):
        client = Client()
        response = client.options('/', HTTP_ORIGIN='https://example.com/', secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')


class QuestionListTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unfound_page(self):
        response = self.client.get('/questions?page=5', secure=True)

        self.assertEqual(response.status_code, 404)

    def test_non_numeric_page(self):
        response = self.client.get('/questions?page=one', secure=True)

        self.assertEqual(response.status_code, 404)


class CreateQuestionTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_creating_question(self):
        response = self.client.post(
            '/questions',
            '{"question": "Test Question?", "choices": ["A", "B", "C"]}',
            content_type='application/json',
            secure=True
        )

        self.assertEqual(response.status_code, 201)

        question = Question.objects.latest()
        self.assertEqual(question.question_text, 'Test Question?')

        choice_a, choice_b, choice_c = question.choices.order_by('choice_text')
        self.assertEqual(choice_a.choice_text, 'A')
        self.assertEqual(choice_b.choice_text, 'B')
        self.assertEqual(choice_c.choice_text, 'C')

    def test_creating_duplicate_question_doesnt_duplicate(self):
        """
        Creating two identical questions should result in a single question
        """

        original_question_count = len(Question.objects.all())

        response1 = self.client.post(
            '/questions',
            '{"question": "Test Question?", "choices": ["A", "B", "C"]}',
            content_type='application/json',
            secure=True
        )
        response2 = self.client.post(
            '/questions',
            '{"question": "Test Question?", "choices": ["A", "B", "C"]}',
            content_type='application/json',
            secure=True
        )

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(Question.objects.all()), original_question_count + 1)

    def test_creating_similar_questions_creates(self):
        """
        Creating two similar questions should result in two questions
        """

        original_question_count = len(Question.objects.all())

        response1 = self.client.post('/questions',
            '{"question": "Test Question?", "choices": ["A", "B", "C"]}',
            content_type='application/json',
            secure=True
        )
        response2 = self.client.post(
            '/questions',
            '{"question": "Test Question?", "choices": ["D", "E", "F"]}',
            content_type='application/json',
            secure=True
        )

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(len(Question.objects.all()), original_question_count + 2)

    def test_creating_question_without_body(self):
        response = self.client.post(
            '/questions',
            content_type='application/json',
            secure=True
        )

        self.assertEqual(response.status_code, 400)

    def test_creating_question_with_invalid_question(self):
        response = self.client.post(
            '/questions', '{"question": null, "choices": ["A", "B"]}',
            content_type='application/json',
            secure=True
        )

        self.assertEqual(response.status_code, 400)

    def test_creating_question_with_invalid_choices(self):
        response = self.client.post(
            '/questions',
            '{"question": "Test Question?", "choices": ["A", "B", null]}',
            content_type='application/json',
            secure=True
        )

        self.assertEqual(response.status_code, 400)

    def test_creating_question_with_few_choices(self):
        response = self.client.post(
            '/questions',
            '{"question": "Test Question?", "choices": ["A"]}',
            content_type='application/json',
            secure=True
        )

        self.assertEqual(response.status_code, 400)


class QuestionDetailTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_choices_ordered_by_votes_then_alphabetical(self):
        question = Question.objects.create(question_text='Are choices ordered correctly?')
        yes_choice = Choice.objects.create(question=question, choice_text='Yes')
        no_choice = Choice.objects.create(question=question, choice_text='No')
        resource = QuestionResource()
        resource.obj = question

        def get_choices():
            return list(map(lambda r: r.obj, resource.get_relations()['choices']))

        self.assertEqual(get_choices(), [no_choice, yes_choice])

        yes_choice.vote()
        self.assertEqual(get_choices(), [yes_choice, no_choice])

    def test_unfound_page(self):
        response = self.client.get('/questions/1337', secure=True)

        self.assertEqual(response.status_code, 404)


class ChoiceDetailTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_choice(self):
        question = Question.objects.create(question_text='Testing Question?')
        Choice.objects.create(question=question, choice_text='Best Choice')

        response = self.client.get('/questions/1/choices/1', secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            'url': '/questions/1/choices/1',
            'choice': 'Best Choice',
            'votes': 0
        })

    def test_get_missing_choice(self):
        question = Question.objects.create(question_text='Testing Question?')
        Choice.objects.create(question=question, choice_text='Best Choice')

        response = self.client.get('/questions/1/choices/100', secure=True)

        self.assertEqual(response.status_code, 404)

    def test_get_missing_question(self):
        response = self.client.get('/questions/100/choices/1', secure=True)

        self.assertEqual(response.status_code, 404)

    def test_vote_choice(self):
        question = Question.objects.create(question_text='Testing Question?')
        choice = Choice.objects.create(question=question, choice_text='Best Choice')

        path = '/questions/{}/choices/{}'.format(question.pk, choice.pk)

        response = self.client.post(path, secure=True)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content), {
            'url': path,
            'choice': 'Best Choice',
            'votes': 1
        })

    def test_vote_unknown_choice(self):
        response = self.client.post('/questions/1/choices/5', secure=True)

        self.assertEqual(response.status_code, 404)


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_healthy(self):
        response = self.client.get('/healthcheck', secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/health+json')
        self.assertEqual(json.loads(response.content), {
            'status': 'ok',
        })
