from django.test import TestCase

from django_quiz.true_false.models import TF_Question


class TestTrueFalseQuestionModel(TestCase):
    def setUp(self):
        TF_Question.objects.create(content = "Is red the best colour?",
                                   explanation = "it is",
                                   correct = True,)
        TF_Question.objects.create(content = "Is blue the best colour?",
                                   explanation = "it is not",
                                   correct = False,)

    def test_true_q(self):
        red = TF_Question.objects.get(explanation = "it is")
        self.assertEqual(red.correct, True)

    def test_false_q(self):
        red = TF_Question.objects.get(explanation = "it is not")
        self.assertEqual(red.correct, False)
