from django.test import TestCase

from .models import Essay_Question


class TestEssayQuestionModel(TestCase):
    def setUp(self):
        self.essay = Essay_Question.objects.create(content="Tell me stuff",
                                                   explanation="Wow!")

    def test_always_false(self):
        self.assertEqual(self.essay.check_if_correct('spam'), False)
        self.assertEqual(self.essay.get_answers(), False)
        self.assertEqual(self.essay.get_answers_list(), False)

    def test_returns_guess(self):
        guess = "To be or not to be"
        self.assertEqual(self.essay.answer_choice_to_string(guess), guess)

    def test_answer_to_string(self):
        self.assertEqual('To be...',
                         self.essay.answer_choice_to_string('To be...'))
