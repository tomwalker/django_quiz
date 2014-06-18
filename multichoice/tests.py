from django.test import TestCase

from multichoice.models import MCQuestion, Answer


class TestMCQuestionModel(TestCase):
    def setUp(self):
        q = MCQuestion.objects.create(id = 1,
                                      content = ("WHAT is the airspeed" +
                                                 "velocity of an unladen" +
                                                 "swallow?"),
                                      explanation = "I, I don't know that!",)

        Answer.objects.create(question = q,
                              content = "African",
                              correct = False,)

        Answer.objects.create(question = q,
                              content = "European",
                              correct = True)


    def test_correct_answer(self):
        china = Country.objects.get(name="China")
        self.assertEqual(china.population, 1400000000)
        self.assertEqual(china.climate, 'TEMPERATE')
        self.assertEqual(china.healthcare, 4)
