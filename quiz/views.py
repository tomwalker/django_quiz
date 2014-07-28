import random

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView, FormView

from .forms import QuestionForm, EssayForm
from .models import Quiz, Category, Progress, Sitting, Question
from essay.models import Essay_Question


class QuizMarkerMixin(object):
    @method_decorator(login_required)
    @method_decorator(permission_required('quiz.view_sittings'))
    def dispatch(self, *args, **kwargs):
        return super(QuizMarkerMixin, self).dispatch(*args, **kwargs)


class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        quiz_filter = self.request.GET.get('quiz_filter')
        if quiz_filter:
            queryset = queryset.filter(quiz__title__icontains=quiz_filter)

        return queryset


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

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            category=self.kwargs['category_name']
        )

        return super(ViewQuizListByCategory, self).\
            dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewQuizListByCategory, self)\
            .get_context_data(**kwargs)

        context['category'] = self.category
        return context

    def get_queryset(self):
        queryset = super(ViewQuizListByCategory, self).get_queryset()
        return queryset.filter(category=self.category)


class QuizUserProgressView(TemplateView):
    template_name = 'progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores()
        context['exams'] = progress.show_exams()
        return context


class QuizMarkingList(QuizMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting

    def get_queryset(self):
        queryset = super(QuizMarkingList, self).get_queryset()\
                                               .filter(complete=True)

        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)

        return queryset


class QuizMarkingDetail(QuizMarkerMixin, DetailView):
    model = Sitting

    def get_object(self, queryset=None):
        sitting = super(QuizMarkingDetail, self).get_object()

        q_to_toggle = self.request.GET.get('id')
        if q_to_toggle:
            q = Question.objects.get_subclass(id=int(q_to_toggle))
            if int(q_to_toggle) in sitting.get_incorrect_questions:
                sitting.remove_incorrect_question(q)
            else:
                sitting.add_incorrect_question(q)

        return sitting


class QuizTake(FormView):
    form_class = QuestionForm
    template_name = 'question.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        self.logged_in_user = self.request.user.is_authenticated()

        if self.logged_in_user:
            self.sitting = Sitting.objects.user_sitting(request.user,
                                                        self.quiz)
        else:
            self.sitting = anon_load_sitting(request, self.quiz)

        if self.sitting is False:
            return render(request, 'single_complete.html')

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        if self.logged_in_user:
            self.question = self.sitting.get_first_question()
        else:
            self.question = anon_next_question(self)

        if self.question.__class__ is Essay_Question:
            form_class = EssayForm

        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        if self.logged_in_user:
            form_valid_user(self, form)
            if self.sitting.get_first_question() is False:
                return final_result_user(self.request, self.sitting,
                                         self.quiz, self.previous)
        else:
            form_valid_anon(self, form)
            if not self.request.session[self.quiz.anon_q_list()]:
                return final_result_anon(self.request,
                                         self.quiz, self.previous)

        self.request.POST = ''
        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['quiz'] = self.quiz
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        return context


def form_valid_user(self, form):
    progress, c = Progress.objects.get_or_create(user=self.request.user)
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

    self.sitting.add_user_answer(self.question, guess)
    self.sitting.remove_first_question()


def final_result_user(request, sitting, quiz, previous):
    results = {
        'quiz': quiz,
        'score': sitting.get_current_score,
        'max_score': quiz.get_max_score,
        'percent': sitting.get_percent_correct,
        'sitting': sitting,
        'previous': previous,
    }

    sitting.mark_quiz_complete()

    if quiz.exam_paper is False:
        sitting.delete()

    if quiz.answers_at_end:
        results['questions'] = quiz.get_questions()
        results['incorrect_questions'] = sitting.get_incorrect_questions

    return render(request, 'result.html', results)


def anon_load_sitting(request, quiz):
    if quiz.single_attempt is True:
        return False

    if quiz.anon_q_list() in request.session:
        return request.session[quiz.anon_q_list()]
    else:
        return new_anon_quiz_session(request, quiz)


def new_anon_quiz_session(request, quiz):
    """
    Sets the session variables when starting a quiz for the first time
    as a non signed-in user
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

    if is_correct:
        self.request.session[self.quiz.anon_score_id()] += 1
        anon_session_score(self.request.session, 1, 1)
    else:
        anon_session_score(self.request.session, 0, 1)

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
        self.request.session[self.quiz.anon_q_list()][1:]


def anon_session_score(session, to_add=0, possible=0):
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
    if "session_score" not in session:
        session["session_score"], session["session_score_possible"] = 0, 0

    if possible > 0:
        session["session_score"] += to_add
        session["session_score_possible"] += possible

    return session["session_score"], session["session_score_possible"]


def final_result_anon(request, quiz, previous):
    score = request.session[quiz.anon_score_id()]
    max_score = quiz.get_max_score
    percent = int(round((float(score) / max_score) * 100))
    session_score, session_possible = anon_session_score(request.session)
    if score is 0:
        score = "0"

    results = {
        'score': score,
        'max_score': max_score,
        'percent': percent,
        'session': session_score,
        'possible': session_possible
    }

    del request.session[quiz.anon_q_list()]

    if quiz.answers_at_end:
        results['questions'] = quiz.get_questions()
    else:
        results['previous'] = previous

    return render(request, 'result.html', results)
