from django.core.files.base import ContentFile
from django.db.models.fields.files import ImageFieldFile
from django.test import TestCase
from six import StringIO

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
        self.assertEqual(self.q.answer_choice_to_string(123),
                         self.answer1.content)

    def test_figure(self):
        # http://stackoverflow.com/a/2473445/1694979
        imgfile = StringIO(
            'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,'
            '\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        imgfile.name = 'test_img_file.gif'

        self.q.figure.save('image', ContentFile(imgfile.read()))
        self.assertIsInstance(self.q.figure, ImageFieldFile)

    def test_answer_to_string(self):
        self.assertEqual('African', self.q.answer_choice_to_string(123))
