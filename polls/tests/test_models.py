import unittest
import datetime
from polls.models import Question, Choice


class QuestionTests(unittest.TestCase):
    def setUp(self):
        super(QuestionTests, self).setUp()
        self.question = Question.create(question_text='Favourite programming language?')
        self.choice = Choice.create(question=self.question, choice_text='Swift')

    def testHasText(self):
        self.assertEqual(self.question.question_text,
                         'Favourite programming language?')

    def testDefaultPublishedDate(self):
        """
        The default published date should be *now*, give or take a second.
        """
        delta = datetime.datetime.now() - self.question.published_at
        self.assertTrue(delta < datetime.timedelta(seconds=1))

    def testToString(self):
        self.assertEqual(str(self.question),
                         'Favourite programming language?')

    def testToDictionary(self):
        self.assertEqual(self.question.as_dictionary(), {
            'question': 'Favourite programming language?',
            'published_at': self.question.published_at.isoformat(),
            'url': '/questions/{}'.format(self.question.id),
            'choices': [
                {
                    'choice': 'Swift',
                }
            ],
        })

class ChoiceTests(unittest.TestCase):
    def setUp(self):
        super(ChoiceTests, self).setUp()
        self.question = Question.create(question_text='Favourite programming language?')
        self.choice = Choice.create(question=self.question, choice_text='Swift')

    def testHasText(self):
        self.assertEqual(self.choice.choice_text, 'Swift')

    def testHasQuestion(self):
        self.assertEqual(self.choice.question, self.question)

    def testToString(self):
        self.assertEqual(str(self.choice), 'Swift')

    def testToDictionary(self):
        self.assertEqual(self.choice.as_dictionary(), {
            'choice': 'Swift',
        })

