from django.test import TestCase

from true_false.models import TF_Question


class TestTrueFalseQuestionModel(TestCase):
    def setUp(self):
        self.red = TF_Question.objects.create(content = "Is red the best colour?",
                                              explanation = "it is",
                                              correct = True,)
        self.blue = TF_Question.objects.create(content = "Is blue the best colour?",
                                               explanation = "it is not",
                                               correct = False,)

    def test_true_q(self):
        self.assertEqual(self.red.correct, True)
        self.assertEqual(self.red.check_if_correct("T"), True)
        self.assertEqual(self.red.check_if_correct("F"), False)
        self.assertEqual(self.red.check_if_correct("4"), False)

    def test_false_q(self):
        self.assertEqual(self.blue.correct, False)
        self.assertEqual(self.blue.check_if_correct("T"), False)
        self.assertEqual(self.blue.check_if_correct("F"), True)
