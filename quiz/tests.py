# -*- coding: iso-8859-15 -*-


from django.test import TestCase

from quiz.models import Category, Quiz, Progress, Sitting, Question

class TestCategory(TestCase):
    def setUp(self):
        Category.objects.new_category(category = "elderberries")
        Category.objects.new_category(category = "straw.berries")
        Category.objects.new_category(category = "black berries")
        Category.objects.new_category(category = "squishy   berries")

    def test_categories(self):
        c1 = Category.objects.get(id = 1)
        c2 = Category.objects.get(id = 2)
        c3 = Category.objects.get(id = 3)
        c4 = Category.objects.get(id = 4)

        self.assertEqual(c1.category, "elderberries")
        self.assertEqual(c2.category, "straw.berries")
        self.assertEqual(c3.category, "black-berries")
        self.assertEqual(c4.category, "squishy-berries")

class TestQuiz(TestCase):
    def setUp(self):
        Category.objects.new_category(category = "elderberries")
        Quiz.objects.create(id = 1,
                            title = "test quiz 1",
                            description = "d1",
                            url = "tq1",)
        Quiz.objects.create(id = 2,
                            title = "test quiz 2",
                            description = "d2",
                            url = "t q2",)
        Quiz.objects.create(id = 3,
                            title = "test quiz 3",
                            description = "d3",
                            url = "t   q3",)
        Quiz.objects.create(id = 4,
                            title = "test quiz 4",
                            description = "d4",
                            url = "t-!£$%^&*q4",)


    def test_quiz_url(self):
        q1 = Quiz.objects.get(id = 1)
        q2 = Quiz.objects.get(id = 2)
        q3 = Quiz.objects.get(id = 3)
        q4 = Quiz.objects.get(id = 4)

        self.assertEqual(q1.url, "tq1")
        self.assertEqual(q2.url, "t-q2")
        self.assertEqual(q3.url, "t-q3")
        self.assertEqual(q4.url, "t-q4")

    def test_quiz_options(self):
        c1 = Category.objects.get(id = 1)

        q5 = Quiz.objects.create(id = 5,
                            title = "test quiz 5",
                            description = "d5",
                            url = "tq5",
                            category = c1,)

        self.assertEqual(q5.category.category, c1.category)
