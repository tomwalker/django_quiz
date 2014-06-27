from django.test import TestCase

from multichoice.models import MCQuestion, Answer


class TestMCQuestionModel(TestCase):
    def setUp(self):
        self.q = MCQuestion.objects.create(id = 1,
                                      content = ("WHAT is the airspeed" +
                                                 "velocity of an unladen" +
                                                 "swallow?"),
                                      explanation = "I, I don't know that!",)

        self.answer1 = Answer.objects.create(id = 123,
                              question = self.q,
                              content = "African",
                              correct = False,)

        self.answer2 = Answer.objects.create(id = 456,
                              question = self.q,
                              content = "European",
                              correct = True)


    def test_answers(self):
        answers = Answer.objects.filter(question__id = self.q.id)
        correct_a = Answer.objects.get(question__id = self.q.id,
                                          correct = True,)

        self.assertEqual(answers.count(), 2)
        self.assertEqual(correct_a.content, "European")
        self.assertEqual(self.q.check_if_correct(123), False)
        self.assertEqual(self.q.check_if_correct(456), True)
