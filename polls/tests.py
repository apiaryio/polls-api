from django.test import TestCase, Client

from polls.models import Question


class CreateQuestionTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_creating_question(self):
        response = self.client.post('/questions', '{"question": "Test Question?", "choices": ["A", "B", "C"]}', content_type='application/json')

        self.assertEqual(response.status_code, 201)

        question = Question.objects.latest()
        self.assertEqual(question.question_text, 'Test Question?')

        choice_a, choice_b, choice_c = question.choice_set.order_by('choice_text')
        self.assertEqual(choice_a.choice_text, 'A')
        self.assertEqual(choice_b.choice_text, 'B')
        self.assertEqual(choice_c.choice_text, 'C')

    def test_creating_duplicate_question_doesnt_duplicate(self):
        """
        Creating two identical questions should result in a single question
        """

        original_question_count = len(Question.objects.all())

        response1 = self.client.post('/questions', '{"question": "Test Question?", "choices": ["A", "B", "C"]}', content_type='application/json')
        response2 = self.client.post('/questions', '{"question": "Test Question?", "choices": ["A", "B", "C"]}', content_type='application/json')

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(Question.objects.all()), original_question_count + 1)

    def test_creating_similar_questions_creates(self):
        """
        Creating two similar questions should result in two questions
        """

        original_question_count = len(Question.objects.all())

        response1 = self.client.post('/questions', '{"question": "Test Question?", "choices": ["A", "B", "C"]}', content_type='application/json')
        response2 = self.client.post('/questions', '{"question": "Test Question?", "choices": ["D", "E", "F"]}', content_type='application/json')

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(len(Question.objects.all()), original_question_count + 2)

