from django.test import TestCase

from .models import MCQuestion, Answer


class TestMCQuestionModel(TestCase):
    def setUp(self):
        self.q = MCQuestion.objects.create(id=1,
                                           content=("WHAT is the airspeed" +
                                                    "velocity of an unladen" +
                                                    "swallow?"),
                                           explanation="I, I don't know that!")

        self.answer1 = Answer.objects.create(id=123,
                                             question=self.q,
                                             content="African",
                                             correct=False)

        self.answer2 = Answer.objects.create(id=456,
                                             question=self.q,
                                             content="European",
                                             correct=True)

    def test_answers(self):
        answers = Answer.objects.filter(question=self.q)
        correct_a = Answer.objects.get(question=self.q,
                                       correct=True)
        answers_by_method = self.q.get_answers()

        self.assertEqual(answers.count(), 2)
        self.assertEqual(correct_a.content, "European")
        self.assertEqual(self.q.check_if_correct(123), False)
        self.assertEqual(self.q.check_if_correct(456), True)
        self.assertEqual(answers_by_method.count(), 2)
