import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView

from .models import Quiz, Category, Progress, Sitting, Question


class QuizListView(ListView):
    model = Quiz


class QuizDetailView(DetailView):
    model = Quiz
    slug_field = 'url'


class CategoriesListView(ListView):
    model = Category


class ViewQuizListByCategory(ListView):
    model = Quiz
    template_name = 'view_quiz_category.html'

    def get_context_data(self, **kwargs):
        context = super(ViewQuizListByCategory, self)\
            .get_context_data(**kwargs)

        category = get_object_or_404(Category,
                                     category=self.kwargs['category_name'])
        context['category'] = category
        return context

    def get_queryset(self):
        category = get_object_or_404(Category,
                                     category=self.kwargs['category_name'])
        queryset = super(ViewQuizListByCategory, self).get_queryset()
        return queryset.filter(category=category)


class QuizUserProgressView(TemplateView):
    template_name = 'progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)

        progress = get_object_or_404(Progress, user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores()
        context['exams'] = progress.show_exams()

        return context


def quiz_take(request, quiz_name):
    quiz = Quiz.objects.get(url=quiz_name.lower())

    if request.user.is_authenticated() is True:
        return user_load_sitting(request, quiz)

    else:  # anon user
        return anon_load_sitting(request, quiz)


def user_load_sitting(request, quiz):
    if quiz.single_attempt is True and\
       Sitting.objects.filter(user=request.user,
                              quiz=quiz,
                              complete=True)\
                      .count() > 0:

        return render(request, 'single_complete.html')

    try:
        sitting = Sitting.objects.get(user=request.user,
                                      quiz=quiz,
                                      complete=False)

    except Sitting.DoesNotExist:
        sitting = Sitting.objects.new_sitting(request.user, quiz)

    except Sitting.MultipleObjectsReturned:
        sitting = Sitting.objects.filter(user=request.user,
                                         quiz=quiz,
                                         complete=False)[0]

    finally:
        return user_load_next_question(request, sitting, quiz)


def user_load_next_question(request, sitting, quiz):
    previous = {}
    if 'guess' in request.GET:
        progress, created = Progress.objects.get_or_create(user=request.user)
        guess = request.GET['guess']
        question = sitting.get_first_question()
        is_correct = question.check_if_correct(guess)

        if is_correct is True:
            sitting.add_to_score(1)
            progress.update_score(question.category, 1, 1)

        else:
            sitting.add_incorrect_question(question)
            progress.update_score(question.category, 0, 1)

        if quiz.answers_at_end is not True:
            previous = {'previous_answer': guess,
                        'previous_outcome': is_correct,
                        'previous_question': question}

        sitting.remove_first_question()

    next_question = sitting.get_first_question()
    if next_question is False:
        #  no questions left
        return final_result_user(request, sitting, previous)

    question_type = next_question.__class__.__name__

    return render_to_response('question.html',
                              {'quiz': quiz,
                               'question': next_question,
                               'question_type': question_type,
                               'previous': previous},
                              context_instance=RequestContext(request))


def final_result_user(request, sitting, previous):
    quiz = sitting.quiz
    score = sitting.get_current_score()
    incorrect = sitting.get_incorrect_questions()
    max_score = quiz.question_set.all().select_subclasses().count()
    percent = sitting.get_percent_correct()

    sitting.mark_quiz_complete()

    if quiz.exam_paper is False:  # if we do not plan to store the outcome
        sitting.delete()

    if quiz.answers_at_end is False:
        return render_to_response('result.html',
                                  {'quiz': quiz,
                                   'score': score,
                                   'max_score': max_score,
                                   'percent': percent,
                                   'previous': previous},
                                  context_instance=RequestContext(request))
    else:
        questions = quiz.question_set.all().select_subclasses()
        return render_to_response('result.html',
                                  {'quiz': quiz,
                                   'score': score,
                                   'max_score': max_score,
                                   'percent': percent,
                                   'questions': questions,
                                   'incorrect_questions': incorrect},
                                  context_instance=RequestContext(request))


def anon_load_sitting(request, quiz):
    if quiz.single_attempt is True:
        return render(request, 'single_complete.html')
    quiz_id = str(quiz.id)
    q_list = quiz_id + "_q_list"

    if q_list in request.session:
        return load_anon_next_question(request, quiz)
    else:
        return new_anon_quiz_session(request, quiz)


def anon_session_score(request, add=0, possible=0):
    """
    Returns the session score for non-signed in users.
    If number passed in then add this to the running total and
    return session score

    examples:
        x, y = anon_session_score(1, 1) will add 1 out of a possible 1
        x, y = anon_session_score(0, 2) will add 0 out of a possible 2
        x, y = anon_session_score()     will return the session score
                                        without modification
    """
    if "session_score" not in request.session:
        request.session["session_score"] = 0
        request.session["session_score_possible"] = 0

    if possible > 0:
        request.session["session_score"] = (request.session["session_score"] +
                                            add)

        request.session["session_score_possible"] = \
            (request.session["session_score_possible"] + possible)

    return request.session["session_score"], \
        request.session["session_score_possible"]


def new_anon_quiz_session(request, quiz):
    """
    Sets the session variables when starting a quiz for the first time
    """

    request.session.set_expiry(259200)  # expires after 3 days

    questions = quiz.question_set.all().select_subclasses()
    question_list = []
    for question in questions:
        #  question_list is a list of question IDs, which are integers
        question_list.append(question.id)

    if quiz.random_order is True:
        random.shuffle(question_list)

    # session score for anon users
    request.session[str(quiz.id) + "_score"] = 0

    # session list of questions
    request.session[str(quiz.id) + "_q_list"] = question_list

    return load_anon_next_question(request, quiz)


def load_anon_next_question(request, quiz):
    question_list = request.session[str(quiz.id) + "_q_list"]
    previous = {}

    if 'guess' in request.GET and request.GET['guess']:
        #  if there has been a previous question
        #  returns a dictionary with previous question details
        previous = question_check_anon(request, quiz)
        question_list = question_list[1:]
        request.session[str(quiz.id) + "_q_list"] = question_list

    if not request.session[str(quiz.id) + "_q_list"]:
        #  no questions left!
        return final_result_anon(request, quiz, previous)

    next_question_id = question_list[0]
    next_question = Question.objects.get_subclass(id=next_question_id)
    question_type = next_question.__class__.__name__

    return render_to_response('question.html',
                              {'quiz': quiz,
                               'question': next_question,
                               'question_type': question_type,
                               'previous': previous},
                              context_instance=RequestContext(request))


def final_result_anon(request, quiz, previous):
    quiz_id = str(quiz.id)
    score = request.session[quiz_id + "_score"]
    max_score = quiz.question_set.all().select_subclasses().count()
    percent = int(round((float(score) / max_score) * 100))
    if score is 0:
        score = "0"

    session_score, session_possible = anon_session_score(request)
    del request.session[quiz_id + "_q_list"]

    if quiz.answers_at_end is False:
        return render_to_response('result.html',
                                  {'score': score,
                                   'max_score': max_score,
                                   'percent': percent,
                                   'previous': previous,
                                   'session': session_score,
                                   'possible': session_possible},
                                  context_instance=RequestContext(request))
    else:
        questions = quiz.question_set.all().select_subclasses()
        return render_to_response('result.html',
                                  {'score': score,
                                   'max_score': max_score,
                                   'percent': percent,
                                   'questions': questions,
                                   'session': session_score,
                                   'possible': session_possible},
                                  context_instance=RequestContext(request))


def question_check_anon(request, quiz):
    guess = request.GET['guess']
    question_id = request.GET['question_id']
    question = Question.objects.get_subclass(id=question_id)
    is_correct = question.check_if_correct(guess)

    if is_correct is True:
        outcome = "correct"
        current = request.session[str(quiz.id) + "_score"]
        request.session[str(quiz.id) + "_score"] = int(current) + 1
        anon_session_score(request, 1, 1)

    else:
        outcome = "incorrect"
        anon_session_score(request, 0, 1)

    if quiz.answers_at_end is not True:
        return {'previous_answer': guess,
                'previous_outcome': outcome,
                'previous_question': question}

    else:
        return {}
