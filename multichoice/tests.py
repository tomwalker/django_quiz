from django.test import TestCase

from multichoice.models import MCQuestion, Answer


class TestMCQuestionModel(TestCase):
    def setUp(self):
        q = MCQuestion.objects.create(id = 1,
                                      content = ("WHAT is the airspeed" +
                                                 "velocity of an unladen" +
                                                 "swallow?"),
                                      explanation = "I, I don't know that!",)

        Answer.objects.create(id = 123,
                              question = q,
                              content = "African",
                              correct = False,)

        Answer.objects.create(id = 456,
                              question = q,
                              content = "European",
                              correct = True)


    def test_answers(self):
        q = MCQuestion.objects.get(id = 1)
        answers = Answer.objects.filter(question__id = q.id)
        correct_a = Answer.objects.get(question__id = q.id,
                                          correct = True,)

        self.assertEqual(answers.count(), 2)
        self.assertEqual(correct_a.content, "European")
        self.assertEqual(q.check_if_correct(123), False)
        self.assertEqual(q.check_if_correct(456), True)
