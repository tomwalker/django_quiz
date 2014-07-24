from django.test import TestCase

from .models import Essay_Question


class TestEssayQuestionModel(TestCase):
    def setUp(self):
        self.essay = Essay_Question.objects.create(content="Tell me stuff",
                                                   explanation="Wow!")

    def test_always_false(self):
        self.assertEqual(self.essay.check_if_correct(), False)
        self.assertEqual(self.essay.get_answers(), False)
        self.assertEqual(self.essay.get_answers_list(), False)
