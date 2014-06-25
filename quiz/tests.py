# -*- coding: iso-8859-15 -*-

from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client, RequestFactory


from quiz.models import Category, Quiz, Progress, Sitting, Question
from quiz.views import quiz_take
from multichoice.models import MCQuestion, Answer
from true_false.models import TF_Question

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
        quiz1 = Quiz.objects.create(id = 1,
                                 title = "test quiz 1",
                                 description = "d1",
                                 url = "tq1",)

        question1 = MCQuestion.objects.create(id = 1,
                                              content = "squawk",)
        question1.quiz.add(quiz1)

        question2 = MCQuestion.objects.create(id = 2,
                                              content = "squeek",)
        question2.quiz.add(quiz1)

        self.user = User.objects.create_user(username = "jacob",
                                             email = "jacob@jacob.com",
                                             password = "top_secret")

        Sitting.objects.new_sitting(self.user, quiz1)

    def test_get_next_remove_first(self):
        s1 = Sitting.objects.get(id = 1)
        self.assertEqual(s1.get_next_question(), 1)

        s1.remove_first_question()
        self.assertEqual(s1.get_next_question(), 2)

        s1.remove_first_question()
        self.assertEqual(s1.get_next_question(), False)

        s1.remove_first_question()
        self.assertEqual(s1.get_next_question(), False)

    def test_scoring(self):
        s1 = Sitting.objects.get(id = 1)
        self.assertEqual(s1.get_current_score(), 0)

        s1.add_to_score(1)
        self.assertEqual(s1.get_current_score(), 1)
        self.assertEqual(s1.get_percent_correct(), 50)

        s1.add_to_score(1)
        self.assertEqual(s1.get_current_score(), 2)
        self.assertEqual(s1.get_percent_correct(), 100)

        s1.add_to_score(1)
        self.assertEqual(s1.get_current_score(), 3)
        self.assertEqual(s1.get_percent_correct(), 100)

    def test_incorrect_and_complete(self):
        s1 = Sitting.objects.get(id = 1)
        self.assertEqual(s1.get_incorrect_questions(), [])

        question1 = MCQuestion.objects.get(id = 1)
        s1.add_incorrect_question(question1)
        self.assertIn("1", s1.get_incorrect_questions())

        question3 = TF_Question.objects.create(id = 3,
                                               content = "oink",)
        s1.add_incorrect_question(question3)
        self.assertIn("3", s1.get_incorrect_questions())

        quiz = Quiz.objects.get(id = 1)
        f_test = s1.add_incorrect_question(quiz)
        self.assertEqual(f_test, False)
        self.assertNotIn("test", s1.get_incorrect_questions())

        self.assertEqual(s1.complete, False)
        s1.mark_quiz_complete()
        self.assertEqual(s1.complete, True)

"""
Tests relating to views
"""

class TestNonQuestionViews(TestCase):
    """
    Starting on questions not directly involved with questions.
    """
    def setUp(self):
        Category.objects.new_category(category = "elderberries")
        c1 = Category.objects.get(id = 1)
        Category.objects.new_category(category = "straw.berries")
        Category.objects.new_category(category = "black berries")

        Quiz.objects.create(id = 1,
                            title = "test quiz 1",
                            description = "d1",
                            url = "tq1",
                            category = c1)
        Quiz.objects.create(id = 2,
                            title = "test quiz 2",
                            description = "d2",
                            url = "t q2",)


    def test_index(self):
        response = self.client.get('/q/')

        self.assertContains(response, 'test quiz 1')

    def test_list_categories(self):
        response = self.client.get('/q/category/')

        self.assertContains(response, 'elderberries')
        self.assertContains(response, 'straw.berries')
        self.assertContains(response, 'black-berries')

    def test_view_cat(self):
        response = self.client.get('/q/category/elderberries/')

        self.assertContains(response, 'test quiz 1')
        self.assertNotContains(response, 'test quiz 2')

    def test_progress_anon(self):
        response = self.client.get('/q/progress/')
        self.assertContains(response, 'Sign up')

        session = self.client.session
        session["session_score"] = 1
        session["session_score_possible"] = 2
        session.save()

        response = self.client.get('/q/progress/')
        self.assertContains(response, '1 out of 2')

    def test_progress_user(self):
        self.user = User.objects.create_user(username = "jacob",
                                             email = "jacob@jacob.com",
                                             password = "top_secret")


        self.client.login(username='jacob', password='top_secret')
        p1 = Progress.objects.new_progress(self.user)
        p1.update_score("elderberries", 1, 2)

        response = self.client.get('/q/progress/')

        self.assertContains(response, "elderberries")


class TestQuestionViewsAnon(TestCase):

    def setUp(self):
        Category.objects.new_category(category = "elderberries")
        c1 = Category.objects.get(id = 1)

        quiz1 = Quiz.objects.create(id = 1,
                                    title = "test quiz 1",
                                    description = "d1",
                                    url = "tq1",
                                    category = c1)

        question1 = MCQuestion.objects.create(id = 1,
                                              content = "squawk",)
        question1.quiz.add(quiz1)

        question2 = MCQuestion.objects.create(id = 2,
                                              content = "squeek",)
        question2.quiz.add(quiz1)

        Answer.objects.create(id = 123,
                              question = question1,
                              content = "bing",
                              correct = False,)

        Answer.objects.create(id = 456,
                              question = question2,
                              content = "bong",
                              correct = True,)

    def test_quiz_take_anon_view_only(self):
        found = resolve('/q/tq1/')

        self.assertEqual(found.func, quiz_take)
        self.assertEqual(found.kwargs, {'quiz_name': 'tq1'})
        self.assertEqual(found.url_name, 'quiz_start_page')

        response = self.client.get('/q/tq1/')

        self.assertContains(response, 'squawk', status_code = 200)
        self.assertEqual(self.client.session.get_expiry_age(), 259200)
        self.assertEqual(self.client.session['1_q_list'], [1, 2])
        self.assertEqual(self.client.session['1_score'], 0)
        self.assertEqual(self.client.session['page_count'], 0)
        self.assertEqual(response.context['quiz'].id, 1)
        self.assertEqual(response.context['question'].content, "squawk")
        self.assertEqual(response.context['question_type'], "MCQuestion")
        self.assertEqual(response.context['previous'], {})
        self.assertEqual(response.context['show_advert'], False)
        self.assertTemplateUsed('question.html')

        session = self.client.session
        session.set_expiry(1) # session is set when user first starts a
        session.save()        # quiz, not on subsequent visits

        response2 = self.client.get('/q/tq1/')
        self.assertEqual(self.client.session.get_expiry_age(), 1)
        self.assertEqual(self.client.session['1_q_list'], [1, 2])
        self.assertEqual(self.client.session['1_score'], 0)
        self.assertEqual(self.client.session['page_count'], 0)

    def test_quiz_take_anon_submit(self):
        # show first question
        response = self.client.get('/q/tq1/')
        self.assertNotContains(response, 'previous question')
        first_question = response.context['question']

        # submit first answer
        response = self.client.get('/q/tq1/',
                                   {'guess': '123',
                                    'question_id':
                                    self.client.session['1_q_list'][0],})

        self.assertContains(response, 'previous question', status_code = 200)
        self.assertContains(response, 'incorrect')
        self.assertContains(response, 'Explanation:')
        self.assertContains(response, 'squeek')
        self.assertEqual(self.client.session['1_q_list'], [2])
        self.assertEqual(self.client.session['session_score'], 0)
        self.assertEqual(self.client.session['session_score_possible'], 1)
        self.assertEqual(response.context['previous'],
                         {'previous_answer': '123',
                          'previous_outcome': 'incorrect',
                          'previous_question': first_question,})
        self.assertTemplateUsed('question.html')
        second_question = response.context['question']

        # submit second and final answer of quiz, show final result page
        response = self.client.get('/q/tq1/',
                                   {'guess': '456',
                                    'question_id':
                                    self.client.session['1_q_list'][0],})

        self.assertContains(response, 'previous question', status_code = 200)
        self.assertNotContains(response, 'incorrect')
        self.assertContains(response, 'Explanation:')
        self.assertContains(response, 'results')
        self.assertNotIn('1_q_list', self.client.session)
        self.assertEqual(response.context['score'], 1)
        self.assertEqual(response.context['max_score'], 2)
        self.assertEqual(response.context['percent'], 50)
        self.assertEqual(response.context['session'], 1)
        self.assertEqual(response.context['possible'], 2)
        self.assertEqual(response.context['previous'],
                         {'previous_answer': '456',
                          'previous_outcome': 'correct',
                          'previous_question': second_question,})
        self.assertTemplateUsed('result.html')

        # quiz restarts
        response = self.client.get('/q/tq1/')
        self.assertNotContains(response, 'previous question')

        # session score continues to increase
        response = self.client.get('/q/tq1/',
                                   {'guess': '123',
                                    'question_id':
                                    self.client.session['1_q_list'][0],})
        self.assertEqual(self.client.session['session_score'], 1)
        self.assertEqual(self.client.session['session_score_possible'], 3)

class TestQuestionViewsUser(TestCase):

    def setUp(self):
        Category.objects.new_category(category = "elderberries")
        c1 = Category.objects.get(id = 1)

        quiz1 = Quiz.objects.create(id = 1,
                                    title = "test quiz 1",
                                    description = "d1",
                                    url = "tq1",
                                    category = c1)

        quiz2 = Quiz.objects.create(id = 2,
                                    title = "test quiz 2",
                                    description = "d2",
                                    url = "tq2",
                                    category = c1,
                                    answers_at_end = True,
                                    exam_paper = True)

        self.user = User.objects.create_user(username = "jacob",
                                             email = "jacob@jacob.com",
                                             password = "top_secret")

        question1 = MCQuestion.objects.create(id = 1,
                                              content = "squawk")
        question1.quiz.add(quiz1)
        question1.quiz.add(quiz2)

        question2 = MCQuestion.objects.create(id = 2,
                                              content = "squeek")
        question2.quiz.add(quiz1)
        question2.quiz.add(quiz2)

        Answer.objects.create(id = 123,
                              question = question1,
                              content = "bing",
                              correct = False,)

        Answer.objects.create(id = 456,
                              question = question2,
                              content = "bong",
                              correct = True,)

    def test_quiz_take_user_view_only(self):
        sittings_before = Sitting.objects.count()
        self.assertEqual(sittings_before, 0)

        self.client.login(username='jacob', password='top_secret')
        response = self.client.get('/q/tq1/')
        quiz1 = Quiz.objects.get(id = 1)
        sitting = Sitting.objects.get(quiz = quiz1)
        sittings_after = Sitting.objects.count()

        self.assertEqual(sittings_after, 1)
        self.assertEqual(sitting.user.username, 'jacob')
        self.assertEqual(sitting.question_list, '1,2,')
        self.assertEqual(sitting.current_score, 0)
        self.assertEqual(self.client.session['page_count'], 0)
        self.assertEqual(response.context['quiz'].id, 1)
        self.assertEqual(response.context['question'].content, "squawk")
        self.assertEqual(response.context['question_type'], "MCQuestion")
        self.assertEqual(response.context['previous'], {})
        self.assertEqual(response.context['show_advert'], False)
        self.assertTemplateUsed('question.html')

        response = self.client.get('/q/tq1/')
        sittings_after = Sitting.objects.count()

        self.assertEqual(sittings_after, 1) # new sitting not made

        Sitting.objects.new_sitting(sitting.user, quiz1)

        sittings_after_doubled = Sitting.objects.count()
        self.assertEqual(Sitting.objects.count(), 2)

        response = self.client.get('/q/tq1/')
        sitting = Sitting.objects.filter(quiz = quiz1)[0]
        self.assertEqual(sitting.question_list, '1,2,')


    def test_quiz_take_user_submit(self):
        self.client.login(username='jacob', password='top_secret')
        response = self.client.get('/q/tq1/')
        progress_count = Progress.objects.count()

        self.assertNotContains(response, 'previous question')
        self.assertEqual(progress_count, 0)

        quiz1 = Quiz.objects.get(id = 1)
        next_question = Sitting.objects.get(quiz = quiz1).get_next_question()

        response = self.client.get('/q/tq1/',
                                   {'guess': '123',
                                    'question_id':
                                    next_question,})

        sitting = Sitting.objects.get(quiz = quiz1)
        progress_count = Progress.objects.count()
        progress = Progress.objects.get(user = sitting.user).list_all_cat_scores()

        self.assertContains(response, 'previous question', status_code = 200)
        self.assertEqual(sitting.current_score, 0)
        self.assertEqual(sitting.incorrect_questions, '1,')
        self.assertEqual(sitting.complete, False)
        self.assertEqual(progress_count, 1)
        self.assertIn('elderberries', progress)
        self.assertEqual(sitting.question_list, '2,')
        self.assertEqual(self.client.session['page_count'], 1)
        self.assertIn('123', response.context['previous']['previous_answer'])
        self.assertEqual(response.context['question'].content, "squeek")
        self.assertTemplateUsed('question.html')

        response = self.client.get('/q/tq1/',
                                   {'guess': '456',
                                    'question_id': 2})

        self.assertEqual(Sitting.objects.count(), 0)
        self.assertTemplateUsed('result.html')
        self.assertEqual(response.context['score'], 1)

    def test_quiz_take_user_answer_end(self):
        self.client.login(username='jacob', password='top_secret')
        response = self.client.get('/q/tq2/',
                                   {'guess': '123',
                                    'question_id': 1})

        self.assertNotContains(response, 'previous question')
        self.assertEqual(response.context['previous'], {})

        response = self.client.get('/q/tq2/',
                                   {'guess': 456,
                                    'question_id': 2})
        question1 = Question.objects.get_subclass(id = 1)
        question2 = Question.objects.get_subclass(id = 2)

        self.assertEqual(response.context['score'], 1)
        self.assertEqual(response.context['max_score'], 2)
        self.assertEqual(response.context['percent'], 50)
        self.assertIn(question1, response.context['questions'])
        self.assertIn(question2, response.context['questions'])


        sitting = Sitting.objects.get(quiz = Quiz.objects.get(id = 2),
                                      user = self.user)
        progress = Progress.objects.get(user = self.user)

        # test that exam_paper = True prevents sitting deletion
        self.assertEqual(Sitting.objects.count(), 1)
        # test that exam result can be recalled later
        self.assertIn(sitting, progress.show_exams())
