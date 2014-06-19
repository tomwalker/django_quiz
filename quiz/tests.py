# -*- coding: iso-8859-15 -*-

from django.contrib.auth.models import User
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
                                 category = c1,
                                 exam_paper = True,)

        self.assertEqual(q5.category.category, c1.category)
        self.assertEqual(q5.random_order, False)
        self.assertEqual(q5.answers_at_end, False)
        self.assertEqual(q5.exam_paper, True)


class TestProgress(TestCase):
    def setUp(self):
        Category.objects.new_category(category = "elderberries")

        Quiz.objects.create(id = 1,
                            title = "test quiz 1",
                            description = "d1",
                            url = "tq1",)

        self.user = User.objects.create_user(username = "jacob",
                                             email = "jacob@jacob.com",
                                             password = "top_secret")


    def test_list_all_empty(self):
        p1 = Progress.objects.new_progress(self.user)
        self.assertEqual(p1.score, "")

        category_dict = p1.list_all_cat_scores()

        self.assertIn(str(category_dict.keys()[0]), p1.score)

        category_dict = p1.list_all_cat_scores()

        self.assertIn("elderberries", p1.score)

        Category.objects.new_category(category = "cheese")

        category_dict = p1.list_all_cat_scores()

        self.assertIn("cheese", p1.score)

    def test_check_cat(self):
        p1 = Progress.objects.new_progress(self.user)
        elderberry_score = p1.check_cat_score("elderberries")

        self.assertEqual(elderberry_score, (0, 0))

        fake_score = p1.check_cat_score("monkey")

        self.assertEqual(fake_score, ("error", "category does not exist"))

        Category.objects.new_category(category = "cheese")
        cheese_score = p1.check_cat_score("cheese")

        self.assertEqual(cheese_score, (0, 0))
        self.assertIn("cheese", p1.score)

    def test_update_score(self):
        p1 = Progress.objects.new_progress(self.user)
        p1.list_all_cat_scores()
        p1.update_score("elderberries", 1, 2)
        elderberry_score = p1.check_cat_score("elderberries")

        self.assertEqual(elderberry_score, (1, 2))

        Category.objects.new_category(category = "cheese")
        p1.update_score("cheese", 3, 4)
        cheese_score = p1.check_cat_score("cheese")

        self.assertEqual(cheese_score, (3, 4))

        fake_cat = p1.update_score("hamster", 3, 4)
        self.assertIn('error', str(fake_cat))

        non_int = p1.update_score("hamster", "1", "a")
        self.assertIn('error', str(non_int))


class TestSitting(TestCase):
    def setUp(self):
        q1 = Quiz.objects.create(id = 1,
                                 title = "test quiz 1",
                                 description = "d1",
                                 url = "tq1",)

        Question.objects.create(id = 1,
                                quiz = q1,
                                content = "squawk",)

        Question.objects.create(id = 2,
                                quiz = q1,
                                content = "squeek",)

        self.user = User.objects.create_user(username = "jacob",
                                 email = "jacob@jacob.com",
                                 password = "top_secret")

        Sitting.objects.new_sitting(self.user, q1)

    def test_get_next(self):
        s1 = Sitting.objects.get(id = 1)
        print s1.question_list
