import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, FormView

from .forms import QuestionForm
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


class QuizTake(FormView):
    form_class = QuestionForm
    template_name = 'question.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])

        if request.user.is_authenticated() is True:
            self.sitting = user_sitting(self.request, self.quiz)
        else:
            anon_load_sitting(self.request, self.quiz)

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        if self.request.user.is_authenticated() is True:
            self.question = self.sitting.get_first_question()
        else:
            self.question = anon_next_question(self)
        kwargs = super(QuizTake, self).get_form_kwargs()
        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        if self.request.user.is_authenticated() is True:
            form_valid_user(self, form)
            if self.sitting.get_first_question() is False:
                return final_result_user(self.request, self.sitting,
                                         self.quiz, self.previous)
        else:
            form_valid_anon(self, form)
            if not self.request.session[self.quiz.anon_q_list()]:
                return final_result_anon(self.request,
                                         self.quiz, self.previous)

        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        return context


def user_sitting(request, quiz):
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
        return sitting


def form_valid_user(self, form):
    progress, created = Progress.objects.get_or_create(
        user=self.request.user)
    guess = form.cleaned_data['answers']
    is_correct = self.question.check_if_correct(guess)

    if is_correct is True:
        self.sitting.add_to_score(1)
        progress.update_score(self.question.category, 1, 1)

    else:
        self.sitting.add_incorrect_question(self.question)
        progress.update_score(self.question.category, 0, 1)

    if self.quiz.answers_at_end is not True:
        self.previous = {'previous_answer': guess,
                         'previous_outcome': is_correct,
                         'previous_question': self.question,
                         'answers': self.question.get_answers(),
                         'question_type': {self.question
                                           .__class__.__name__: True}}
    else:
        self.previous = {}

    self.sitting.remove_first_question()


def final_result_user(request, sitting, quiz, previous):
    score = sitting.get_current_score
    incorrect = sitting.get_incorrect_questions()
    max_score = quiz.get_max_score
    percent = sitting.get_percent_correct

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
        questions = quiz.get_questions()
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

    if quiz.anon_q_list() in request.session:
        return request.session[quiz.anon_q_list()]
    else:
        return new_anon_quiz_session(request, quiz)


def new_anon_quiz_session(request, quiz):
    """
    Sets the session variables when starting a quiz for the first time
    """
    request.session.set_expiry(259200)  # expires after 3 days
    questions = quiz.get_questions()
    question_list = [question.id for question in questions]
    if quiz.random_order is True:
        random.shuffle(question_list)

    # session score for anon users
    request.session[quiz.anon_score_id()] = 0

    # session list of questions
    request.session[quiz.anon_q_list()] = question_list

    return request.session[quiz.anon_q_list()]


def anon_next_question(self):
    next_question_id = self.request.session[self.quiz.anon_q_list()][0]
    return Question.objects.get_subclass(id=next_question_id)


def form_valid_anon(self, form):
    guess = form.cleaned_data['answers']
    is_correct = self.question.check_if_correct(guess)

    if is_correct is True:
        self.request.session[self.quiz.anon_score_id()] += 1
        anon_session_score(self.request, 1, 1)
    else:
        anon_session_score(self.request, 0, 1)

    if self.quiz.answers_at_end is not True:
        self.previous = {'previous_answer': guess,
                         'previous_outcome': is_correct,
                         'previous_question': self.question,
                         'answers': self.question.get_answers(),
                         'question_type': {self.question
                                           .__class__.__name__: True}}
    else:
        self.previous = {}
    self.request.session[self.quiz.anon_q_list()] =\
        (self.request.session[self.quiz.anon_q_list()][1:])


def anon_session_score(request, to_add=0, possible=0):
    """
    Returns the session score for non-signed in users.
    If number passed in then add this to the running total and
    return session score

    examples:
        anon_session_score(1, 1) will add 1 out of a possible 1
        anon_session_score(0, 2) will add 0 out of a possible 2
        x, y = anon_session_score() will return the session score
                                    without modification
    """
    if "session_score" not in request.session:
        request.session["session_score"] = 0
        request.session["session_score_possible"] = 0

    if possible > 0:
        request.session["session_score"] = (request.session["session_score"] +
                                            to_add)

        request.session["session_score_possible"] = \
            (request.session["session_score_possible"] + possible)

    return request.session["session_score"], \
        request.session["session_score_possible"]


def final_result_anon(request, quiz, previous):
    score = request.session[quiz.anon_score_id()]
    max_score = quiz.get_max_score
    percent = int(round((float(score) / max_score) * 100))
    if score is 0:
        score = "0"

    session_score, session_possible = anon_session_score(request)
    del request.session[quiz.anon_q_list()]

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
        questions = quiz.get_questions()
        return render_to_response('result.html',
                                  {'score': score,
                                   'max_score': max_score,
                                   'percent': percent,
                                   'questions': questions,
                                   'session': session_score,
                                   'possible': session_possible},
                                  context_instance=RequestContext(request))
