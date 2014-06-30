# -*- coding: iso-8859-15 -*-

from django.contrib.auth.models import User, AnonymousUser
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.template import Template, Context


from quiz.models import Category, Quiz, Progress, Sitting, Question
from quiz.views import quiz_take
from multichoice.models import MCQuestion, Answer
from true_false.models import TF_Question

class TestCategory(TestCase):
    def setUp(self):
        self.c1 = Category.objects.new_category(category = 'elderberries')
        self.c2 = Category.objects.new_category(category = 'straw.berries')
        self.c3 = Category.objects.new_category(category = 'black berries')
        self.c4 = Category.objects.new_category(category = 'squishy   berries')

    def test_categories(self):

        self.assertEqual(self.c1.category, 'elderberries')
        self.assertEqual(self.c2.category, 'straw.berries')
        self.assertEqual(self.c3.category, 'black-berries')
        self.assertEqual(self.c4.category, 'squishy-berries')

class TestQuiz(TestCase):
    def setUp(self):
        self.c1 = Category.objects.new_category(category = 'elderberries')

        self.quiz1 = Quiz.objects.create(id = 1,
                                         title = 'test quiz 1',
                                         description = 'd1',
                                         url = 'tq1',)
        self.quiz2 = Quiz.objects.create(id = 2,
                                         title = 'test quiz 2',
                                         description = 'd2',
                                         url = 't q2',)
        self.quiz3 = Quiz.objects.create(id = 3,
                                         title = 'test quiz 3',
                                         description = 'd3',
                                         url = 't   q3',)
        self.quiz4 = Quiz.objects.create(id = 4,
                                         title = 'test quiz 4',
                                         description = 'd4',
                                         url = 't-!£$%^&*q4',)


    def test_quiz_url(self):
        self.assertEqual(self.quiz1.url, 'tq1')
        self.assertEqual(self.quiz2.url, 't-q2')
        self.assertEqual(self.quiz3.url, 't-q3')
        self.assertEqual(self.quiz4.url, 't-q4')

    def test_quiz_options(self):
        q5 = Quiz.objects.create(id = 5,
                                 title = 'test quiz 5',
                                 description = 'd5',
                                 url = 'tq5',
                                 category = self.c1,
                                 exam_paper = True,)

        self.assertEqual(q5.category.category, self.c1.category)
        self.assertEqual(q5.random_order, False)
        self.assertEqual(q5.answers_at_end, False)
        self.assertEqual(q5.exam_paper, True)

    def test_quiz_single_attempt(self):
        self.quiz1.single_attempt = True
        self.quiz1.save()

        self.assertEqual(self.quiz1.exam_paper, True)


class TestProgress(TestCase):
    def setUp(self):
        self.c1 = Category.objects.new_category(category = 'elderberries')

        self.quiz1 = Quiz.objects.create(id = 1,
                                         title = 'test quiz 1',
                                         description = 'd1',
                                         url = 'tq1',)

        self.user = User.objects.create_user(username = 'jacob',
                                             email = 'jacob@jacob.com',
                                             password = 'top_secret')


    def test_list_all_empty(self):
        p1 = Progress.objects.new_progress(self.user)
        self.assertEqual(p1.score, '')

        category_dict = p1.list_all_cat_scores()

        self.assertIn(str(category_dict.keys()[0]), p1.score)

        self.assertIn(self.c1.category, p1.score)

        Category.objects.new_category(category = 'cheese')

        p1.list_all_cat_scores()

        self.assertIn('cheese', p1.score)

    def test_check_cat(self):
        p1 = Progress.objects.new_progress(self.user)
        elderberry_score = p1.check_cat_score('elderberries')

        self.assertEqual(elderberry_score, (0, 0))

        fake_score = p1.check_cat_score('monkey')

        self.assertEqual(fake_score, ('error', 'category does not exist'))

        Category.objects.new_category(category = 'cheese')
        cheese_score = p1.check_cat_score('cheese')

        self.assertEqual(cheese_score, (0, 0))
        self.assertIn('cheese', p1.score)

    def test_update_score(self):
        p1 = Progress.objects.new_progress(self.user)
        p1.list_all_cat_scores()
        p1.update_score('elderberries', 1, 2)
        elderberry_score = p1.check_cat_score('elderberries')

        self.assertEqual(elderberry_score, (1, 2))

        Category.objects.new_category(category = 'cheese')
        p1.update_score('cheese', 3, 4)
        cheese_score = p1.check_cat_score('cheese')

        self.assertEqual(cheese_score, (3, 4))

        fake_cat = p1.update_score('hamster', 3, 4)
        self.assertIn('error', str(fake_cat))

        non_int = p1.update_score('cheese', '1', 'a')
        self.assertIn('error', str(non_int))


class TestSitting(TestCase):
    def setUp(self):
        self.quiz1 = Quiz.objects.create(id = 1,
                                         title = 'test quiz 1',
                                         description = 'd1',
                                         url = 'tq1',)

        self.question1 = MCQuestion.objects.create(id = 1,
                                                   content = 'squawk',)
        self.question1.quiz.add(self.quiz1)

        self.question2 = MCQuestion.objects.create(id = 2,
                                                   content = 'squeek',)
        self.question2.quiz.add(self.quiz1)

        self.user = User.objects.create_user(username = 'jacob',
                                             email = 'jacob@jacob.com',
                                             password = 'top_secret')

        self.sitting = Sitting.objects.new_sitting(self.user, self.quiz1)

    def test_get_next_remove_first(self):
        self.assertEqual(self.sitting.get_next_question(), 1)

        self.sitting.remove_first_question()
        self.assertEqual(self.sitting.get_next_question(), 2)

        self.sitting.remove_first_question()
        self.assertEqual(self.sitting.get_next_question(), False)

        self.sitting.remove_first_question()
        self.assertEqual(self.sitting.get_next_question(), False)

    def test_scoring(self):
        self.assertEqual(self.sitting.get_current_score(), 0)

        self.sitting.add_to_score(1)
        self.assertEqual(self.sitting.get_current_score(), 1)
        self.assertEqual(self.sitting.get_percent_correct(), 50)

        self.sitting.add_to_score(1)
        self.assertEqual(self.sitting.get_current_score(), 2)
        self.assertEqual(self.sitting.get_percent_correct(), 100)

        self.sitting.add_to_score(1)
        self.assertEqual(self.sitting.get_current_score(), 3)
        self.assertEqual(self.sitting.get_percent_correct(), 100)

    def test_incorrect_and_complete(self):
        self.assertEqual(self.sitting.get_incorrect_questions(), [])

        self.sitting.add_incorrect_question(self.question1)
        self.assertIn('1', self.sitting.get_incorrect_questions())

        question3 = TF_Question.objects.create(id = 3,
                                               content = 'oink',)
        self.sitting.add_incorrect_question(question3)
        self.assertIn('3', self.sitting.get_incorrect_questions())

        f_test = self.sitting.add_incorrect_question(self.quiz1)
        self.assertEqual(f_test, False)
        self.assertNotIn('test', self.sitting.get_incorrect_questions())

        self.assertEqual(self.sitting.complete, False)
        self.sitting.mark_quiz_complete()
        self.assertEqual(self.sitting.complete, True)


'''
Tests relating to views
'''

class TestNonQuestionViews(TestCase):
    '''
    Starting on questions not directly involved with questions.
    '''
    def setUp(self):
        self.c1 = Category.objects.new_category(category = 'elderberries')
        self.c2 = Category.objects.new_category(category = 'straw.berries')
        self.c3 = Category.objects.new_category(category = 'black berries')

        self.quiz1 = Quiz.objects.create(id = 1,
                                         title = 'test quiz 1',
                                         description = 'd1',
                                         url = 'tq1',
                                         category = self.c1)
        self.quiz2 = Quiz.objects.create(id = 2,
                                         title = 'test quiz 2',
                                         description = 'd2',
                                         url = 't q2',)


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
        session['session_score'] = 1
        session['session_score_possible'] = 2
        session.save()

        response = self.client.get('/q/progress/')
        self.assertContains(response, '1 out of 2')

    def test_progress_user(self):
        self.user = User.objects.create_user(username = 'jacob',
                                             email = 'jacob@jacob.com',
                                             password = 'top_secret')

        self.client.login(username='jacob', password='top_secret')
        p1 = Progress.objects.new_progress(self.user)
        p1.update_score(self.c1.category, 1, 2)
        response = self.client.get('/q/progress/')

        self.assertContains(response, 'elderberries')
        self.assertIn('straw.berries', response.context['cat_scores'])
        self.assertEqual([1, 2, 50], response.context['cat_scores']['elderberries'])
        self.assertContains(response, 'var difference = 2 - 1;')
        self.assertContains(response, 'var correct = 1;')

class TestQuestionViewsAnon(TestCase):

    def setUp(self):
        self.c1 = Category.objects.new_category(category = 'elderberries')

        self.quiz1 = Quiz.objects.create(id = 1,
                                         title = 'test quiz 1',
                                         description = 'd1',
                                         url = 'tq1',
                                         category = self.c1)

        self.question1 = MCQuestion.objects.create(id = 1,
                                                   content = 'squawk',)
        self.question1.quiz.add(self.quiz1)

        self.question2 = MCQuestion.objects.create(id = 2,
                                                   content = 'squeek',)
        self.question2.quiz.add(self.quiz1)

        self.answer1 = Answer.objects.create(id = 123,
                                             question = self.question1,
                                             content = 'bing',
                                             correct = False,)

        self.answer2 = Answer.objects.create(id = 456,
                                             question = self.question2,
                                             content = 'bong',
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
        self.assertEqual(response.context['quiz'].id, self.quiz1.id)
        self.assertEqual(response.context['question'].content,
                         self.question1.content)
        self.assertEqual(response.context['question_type'],
                         self.question1.__class__.__name__)
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

    def test_anon_cannot_sit_single_attempt(self):
        self.quiz1.single_attempt = True
        self.quiz1.save()
        response = self.client.get('/q/tq1/')

        self.assertContains(response, 'accessible')
        self.assertTemplateUsed('single_complete.html')



class TestQuestionViewsUser(TestCase):

    def setUp(self):
        self.c1 = Category.objects.new_category(category = 'elderberries')

        self.quiz1 = Quiz.objects.create(id = 1,
                                         title = 'test quiz 1',
                                         description = 'd1',
                                         url = 'tq1',
                                         category = self.c1)

        self.quiz2 = Quiz.objects.create(id = 2,
                                         title = 'test quiz 2',
                                         description = 'd2',
                                         url = 'tq2',
                                         category = self.c1,
                                         answers_at_end = True,
                                         exam_paper = True)

        self.user = User.objects.create_user(username = 'jacob',
                                             email = 'jacob@jacob.com',
                                             password = 'top_secret')

        self.question1 = MCQuestion.objects.create(id = 1,
                                                   content = 'squawk')
        self.question1.quiz.add(self.quiz1)
        self.question1.quiz.add(self.quiz2)

        self.question2 = MCQuestion.objects.create(id = 2,
                                                   content = 'squeek')
        self.question2.quiz.add(self.quiz1)

        self.question3 = TF_Question.objects.create(id = 3,
                                                    content = 'oink',
                                                    correct = True)
        self.question3.quiz.add(self.quiz2)

        self.answer1 = Answer.objects.create(id = 123,
                                             question = self.question1,
                                             content = 'bing',
                                             correct = False,)

        self.answer2 = Answer.objects.create(id = 456,
                                             question = self.question2,
                                             content = 'bong',
                                             correct = True,)

    def test_quiz_take_user_view_only(self):
        sittings_before = Sitting.objects.count()
        self.assertEqual(sittings_before, 0)

        self.client.login(username='jacob', password='top_secret')
        response = self.client.get('/q/tq1/')
        sitting = Sitting.objects.get(quiz = self.quiz1)
        sittings_after = Sitting.objects.count()

        self.assertEqual(sittings_after, 1)
        self.assertEqual(sitting.user.username, 'jacob')
        self.assertEqual(sitting.question_list, '1,2,')
        self.assertEqual(sitting.current_score, 0)
        self.assertEqual(self.client.session['page_count'], 0)
        self.assertEqual(response.context['quiz'].id, self.quiz1.id)
        self.assertEqual(response.context['question'].content, self.question1.content)
        self.assertEqual(response.context['question_type'], self.question1.__class__.__name__)
        self.assertEqual(response.context['previous'], {})
        self.assertEqual(response.context['show_advert'], False)
        self.assertTemplateUsed('question.html')

        response = self.client.get('/q/tq1/')
        sittings_after = Sitting.objects.count()

        self.assertEqual(sittings_after, 1) # new sitting not made

        Sitting.objects.new_sitting(sitting.user, self.quiz1)

        sittings_after_doubled = Sitting.objects.count()
        self.assertEqual(Sitting.objects.count(), 2)

        response = self.client.get('/q/tq1/')
        sitting = Sitting.objects.filter(quiz = self.quiz1)[0]
        self.assertEqual(sitting.question_list, '1,2,')


    def test_quiz_take_user_submit(self):
        self.client.login(username='jacob', password='top_secret')
        response = self.client.get('/q/tq1/')
        progress_count = Progress.objects.count()

        self.assertNotContains(response, 'previous question')
        self.assertEqual(progress_count, 0)

        next_question = Sitting.objects.get(quiz = self.quiz1).get_next_question()

        response = self.client.get('/q/tq1/',
                                   {'guess': '123',
                                    'question_id':
                                    next_question,})

        sitting = Sitting.objects.get(quiz = self.quiz1)
        progress_count = Progress.objects.count()
        progress = Progress.objects.get(user = sitting.user).list_all_cat_scores()

        self.assertContains(response, 'previous question', status_code = 200)
        self.assertEqual(sitting.current_score, 0)
        self.assertEqual(sitting.incorrect_questions, '1,')
        self.assertEqual(sitting.complete, False)
        self.assertEqual(progress_count, 1)
        self.assertIn(self.c1.category, progress)
        self.assertEqual(sitting.question_list, '2,')
        self.assertEqual(self.client.session['page_count'], 1)
        self.assertIn('123', response.context['previous']['previous_answer'])
        self.assertEqual(response.context['question'].content, self.question2.content)
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
                                   {'guess': 'T',
                                    'question_id': 3})

        self.assertEqual(response.context['score'], 1)
        self.assertEqual(response.context['max_score'], 2)
        self.assertEqual(response.context['percent'], 50)
        self.assertIn(self.question1, response.context['questions'])
        self.assertIn(self.question3, response.context['questions'])
        self.assertContains(response, 'above question incorrectly')
        self.assertContains(response, 'True')


        sitting = Sitting.objects.get(quiz = self.quiz2,
                                      user = self.user)
        progress = Progress.objects.get(user = self.user)

        # test that exam_paper = True prevents sitting deletion
        self.assertEqual(Sitting.objects.count(), 1)
        # test that exam result can be recalled later
        self.assertIn(sitting, progress.show_exams())

    def test_user_cannot_sit_single_attempt(self):
        self.quiz2.single_attempt = True
        self.quiz2.save()
        self.client.login(username='jacob', password='top_secret')
        response = self.client.get('/q/tq2/',
                                   {'guess': '123',
                                    'question_id': 1})
        response = self.client.get('/q/tq2/',
                                   {'guess': 'T',
                                    'question_id': 3})

        # quiz complete, trying it again
        response = self.client.get('/q/tq2/')

        self.assertContains(response, 'only one sitting is permitted.')
        self.assertTemplateUsed('single_complete.html')

class TestTemplateTags(TestCase):

    def setUp(self):
        self.question1 = MCQuestion.objects.create(id = 1,
                                                   content = 'squawk')

        self.answer1 = Answer.objects.create(id = 123,
                                             question = self.question1,
                                             content = 'bing',
                                             correct = False,)

        self.answer2 = Answer.objects.create(id = 456,
                                             question = self.question1,
                                             content = 'bong',
                                             correct = True,)

        self.question2 = TF_Question.objects.create(id = 3,
                                                    content = 'oink',
                                                    correct = True)
        self.quiz1 = Quiz.objects.create(id = 1,
                                         title = 'test quiz 1',
                                         description = 'd1',
                                         url = 'tq1',)

        self.question1.quiz.add(self.quiz1)
        self.question2.quiz.add(self.quiz1)

        self.user = User.objects.create_user(username = 'jacob',
                                             email = 'jacob@jacob.com',
                                             password = 'top_secret')

        self.sitting = Sitting.objects.new_sitting(self.user, self.quiz1)
        self.sitting.current_score = 1

    def test_answers_mc(self):
        template = Template( '{% load quiz_tags %}' +
                             '{% answers_for_mc_question question %}')
        context = Context({'question': self.question1})

        self.assertTemplateUsed('answers_for_mc_question.html')
        self.assertIn('bing', template.render(context))

    def test_correct_answer_MC(self):
        template = Template( '{% load quiz_tags %}' +
                             '{% correct_answer previous %}')

        previous_MC = {'previous_answer': 123,
                       'previous_outcome': 'incorrect',
                       'previous_question': self.question1}

        context = Context({'previous': previous_MC})

        self.assertTemplateUsed('correct_answer.html')
        self.assertIn('bing', template.render(context))
        self.assertIn('bong', template.render(context))
        self.assertIn('your answer', template.render(context))

    def test_correct_answer_TF(self):
        template = Template( '{% load quiz_tags %}' +
                             '{% correct_answer previous %}')

        previous_TF = {'previous_answer': 'T',
                       'previous_outcome': 'correct',
                       'previous_question': self.question2}

        context = Context({'previous': previous_TF})

        self.assertTemplateUsed('correct_answer.html')
        self.assertIn('True', template.render(context))
        self.assertIn('False', template.render(context))
        self.assertNotIn('your answer', template.render(context))

    def test_correct_answer_all_anon(self):
        template = Template( '{% load quiz_tags %}' +
                             '{% correct_answer_for_all_with_users_incorrect' +
                             ' question  incorrect_questions %}')

        context = Context({'question': self.question1,})

        self.assertTemplateUsed('correct_answer.html')
        self.assertIn('bing', template.render(context))
        self.assertNotIn('incorrectly', template.render(context))

    def test_correct_answer_all_user(self):
        template = Template( '{% load quiz_tags %}' +
                             '{% correct_answer_for_all_with_users_incorrect ' +
                             'question  incorrect_questions %}')

        context = Context({'question': self.question1,
                            'incorrect_questions': '1,'})

        self.assertTemplateUsed('correct_answer.html')
        self.assertIn('bing', template.render(context))
        self.assertIn('incorrectly', template.render(context))

    def test_previous_exam(self):
        template = Template( '{% load quiz_tags %}' +
                             '{% user_previous_exam exam %}')

        context = Context({'exam': self.sitting})

        self.assertTemplateUsed('user_previous_exam.html')
        self.assertIn('test quiz 1', template.render(context))
        self.assertIn('<td>1</td>', template.render(context))
        self.assertIn('<td>2</td>', template.render(context))
        self.assertIn('<td>50</td>', template.render(context))
