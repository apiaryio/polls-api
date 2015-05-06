from django.test import TestCase, Client

from polls.views import QuestionResource
from polls.models import Question, Choice, Vote


class CreateQuestionTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_creating_question(self):
        response = self.client.post('/questions', '{"question": "Test Question?", "choices": ["A", "B", "C"]}', content_type='application/json')

        self.assertEqual(response.status_code, 201)

        question = Question.objects.all()[0]
        self.assertEqual(question.question_text, 'Test Question?')

        choice_a, choice_b, choice_c = question.choices.order_by('choice_text')
        self.assertEqual(choice_a.choice_text, 'A')
        self.assertEqual(choice_b.choice_text, 'B')
        self.assertEqual(choice_c.choice_text, 'C')

    def test_creating_duplicate_question_doesnt_duplicate(self):
        """
        Creating two identical questions should result in a single question
        """

        response1 = self.client.post('/questions', '{"question": "Test Question?", "choices": ["A", "B", "C"]}', content_type='application/json')
        response2 = self.client.post('/questions', '{"question": "Test Question?", "choices": ["A", "B", "C"]}', content_type='application/json')

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(Question.objects.all()), 1)

    def test_creating_similar_questions_creates(self):
        """
        Creating two similar questions should result in two questions
        """

        response1 = self.client.post('/questions', '{"question": "Test Question?", "choices": ["A", "B", "C"]}', content_type='application/json')
        response2 = self.client.post('/questions', '{"question": "Test Question?", "choices": ["D", "E", "F"]}', content_type='application/json')

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(len(Question.objects.all()), 2)


class QuestionDetailTestCase(TestCase):
    def test_choices_ordered_by_votes_then_alphabetical(self):
        question = Question.objects.create(question_text='Are choices ordered correctly?')
        yes_choice = Choice.objects.create(question=question, choice_text='Yes')
        no_choice = Choice.objects.create(question=question, choice_text='No')
        resource = QuestionResource()
        resource.obj = question

        def get_choices():
            return map(lambda r: r.obj, resource.get_relations()['choices'])

        self.assertEqual(get_choices(), [no_choice, yes_choice])

        yes_choice.vote()
        self.assertEqual(get_choices(), [yes_choice, no_choice])
