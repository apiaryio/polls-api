from django.test import TestCase, Client

from polls.models import Question


class CreateQuestionTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_creating_question(self):
        response = self.client.post('/questions', '{"question": "Test Question?", "choices": ["A", "B", "C"]}', content_type='application/json')

        self.assertEqual(response.status_code, 201)

        question = Question.objects.all()[0]
        self.assertEqual(question.question_text, 'Test Question?')

        choice_a, choice_b, choice_c = question.choice_set.order_by('choice_text')
        self.assertEqual(choice_a.choice_text, 'A')
        self.assertEqual(choice_b.choice_text, 'B')
        self.assertEqual(choice_c.choice_text, 'C')
