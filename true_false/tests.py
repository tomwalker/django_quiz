from django.test import TestCase

from true_false.models import TF_Question


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
        self.assertEqual(red.check_if_correct("T"), True)
        self.assertEqual(red.check_if_correct("F"), False)
        self.assertEqual(red.check_if_correct("4"), False)

    def test_false_q(self):
        blue = TF_Question.objects.get(explanation = "it is not")
        self.assertEqual(blue.correct, False)
        self.assertEqual(blue.check_if_correct("T"), False)
        self.assertEqual(blue.check_if_correct("F"), True)
