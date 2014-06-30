import random

from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render, render_to_response

from quiz.models import Quiz, Category, Progress, Sitting, Question
from multichoice.models import MCQuestion, Answer
from true_false.models import TF_Question

def index(request):
    all_quizzes = Quiz.objects.all()
    return render(request, 'quiz_index.html',
                  {'quiz_list': all_quizzes,})


def list_categories(request):
    return render(request, 'list_categories.html',
                  {'categories': Category.objects.all(),})


def view_category(request, slug):
    category = get_object_or_404(Category,
                                 category = slug.replace(' ', '-').lower())
    quizzes = Quiz.objects.filter(category = category)

    return render(request, 'view_quiz_category.html',
                  {'category': category,
                   'quizzes': quizzes,})

def quiz_take(request, quiz_name):
    quiz = Quiz.objects.get(url = quiz_name.lower())

    if request.user.is_authenticated() == True:

        if quiz.single_attempt == True:
            try:
                single = Sitting.objects.get(user = request.user,
                                            quiz = quiz,
                                            complete = True)
            except Sitting.DoesNotExist:
                pass
            except Sitting.MultipleObjectsReturned:
                return render(request, 'single_complete.html')
            else:
                return render(request, 'single_complete.html')

        try:
            previous_sitting = Sitting.objects.get(user = request.user,
                                                   quiz = quiz,
                                                   complete = False,)

        except Sitting.DoesNotExist:
            return user_new_quiz_session(request, quiz)

        except Sitting.MultipleObjectsReturned:
            previous_sitting = Sitting.objects.filter(user = request.user,
                                                      quiz = quiz,
                                                      complete = False,
                                                      )[0]

            return user_load_next_question(request, previous_sitting, quiz)

        else:
            return user_load_next_question(request, previous_sitting, quiz)


    else:  #  anon user
        if quiz.single_attempt == True:
            return render(request, 'single_complete.html')
        quiz_id = str(quiz.id)
        q_list = quiz_id + "_q_list"

        if q_list in request.session:
            return load_anon_next_question(request, quiz)
        else:
            return new_anon_quiz_session(request, quiz)


def new_anon_quiz_session(request, quiz):
    """
    Sets the session variables when starting a quiz for the first time
    """

    request.session.set_expiry(259200)  #  expires after 3 days

    questions = quiz.question_set.all().select_subclasses()
    question_list = []
    for question in questions:
        #  question_list is a list of question IDs, which are integers
        question_list.append(question.id)

    if quiz.random_order == True:
        random.shuffle(question_list)

    # session score for anon users
    request.session[str(quiz.id) + "_score"] = 0

    # session list of questions
    request.session[str(quiz.id)+ "_q_list"] = question_list

    if 'page_count' not in request.session:
        # session page count, used for adverts on original website
        request.session['page_count'] = 0

    return load_anon_next_question(request, quiz)


def user_new_quiz_session(request, quiz):
    sitting = Sitting.objects.new_sitting(request.user, quiz)

    if 'page_count' not in request.session:
        #  session page count
        request.session['page_count'] = 0

    return user_load_next_question(request, sitting, quiz)


def load_anon_next_question(request, quiz):
    question_list = request.session[str(quiz.id)+ "_q_list"]
    previous = {}

    if 'guess' in request.GET and request.GET['guess']:
        #  if there has been a previous question
        #  returns a dictionary with previous question details
        previous = question_check_anon(request, quiz)
        question_list = question_list[1:]
        request.session[str(quiz.id)+ "_q_list"] = question_list
        request.session['page_count'] = request.session['page_count'] + 1

    if not request.session[str(quiz.id)+ "_q_list"]:
        #  no questions left!
        return final_result_anon(request, quiz, previous)

    show_advert = False

    """
    This is a counter that allows you to add something into the
    template every X amount of pages.
    In my original site, I used this to show a full page advert
    every 10 pages.
    """

    # try:
    #     if request.session['page_count'] > 0 and \
    #        request.session['page_count'] % 10 == 0:
    #         request.session['page_count'] = request.session['page_count'] + 1
    #         show_advert = True

    # except KeyError:
    #     request.session['page_count'] = 0

    next_question_id = question_list[0]
    next_question = Question.objects.get_subclass(id = next_question_id)
    question_type = next_question.__class__.__name__

    return render_to_response('question.html',
                              {'quiz': quiz,
                               'question': next_question,
                               'question_type': question_type,
                               'previous': previous,
                               'show_advert': show_advert,},
                              context_instance = RequestContext(request))


def user_load_next_question(request, sitting, quiz):
    previous = {}

    if 'guess' in request.GET and request.GET['guess']:
        previous = question_check_user(request, quiz, sitting)
        sitting.remove_first_question()
        request.session['page_count'] = request.session['page_count'] + 1

    question_ID = sitting.get_next_question()

    if question_ID == False:
        #  no questions left
        return final_result_user(request, sitting, previous)

    show_advert = False

    # try:
    #     if request.session['page_count'] > 0 and \
    #        request.session['page_count'] % 10 == 0:
    #         request.session['page_count'] = request.session['page_count'] + 1
    #         show_advert = True

    # except KeyError:
    #     request.session['page_count'] = 0

    next_question = Question.objects.get_subclass(id = question_ID)
    question_type = next_question.__class__.__name__

    return render_to_response('question.html',
                              {'quiz': quiz,
                               'question': next_question,
                               'question_type': question_type,
                               'previous': previous,
                               'show_advert': show_advert,},
                              context_instance = RequestContext(request))


def final_result_anon(request, quiz, previous):
    quiz_id = str(quiz.id)
    score = request.session[quiz_id + "_score"]
    max_score = quiz.question_set.all().select_subclasses().count()
    percent = int(round((float(score) / max_score) * 100))
    if score == 0:
        score = "0"

    session_score, session_possible = anon_session_score(request)
    del request.session[quiz_id + "_q_list"]

    if quiz.answers_at_end == False:
        return render_to_response('result.html',
                                  {'score': score,
                                   'max_score': max_score,
                                   'percent': percent,
                                   'previous': previous,
                                   'session': session_score,
                                   'possible': session_possible,},
                                  context_instance = RequestContext(request))
    else:
        questions = quiz.question_set.all().select_subclasses()
        return render_to_response('result.html',
                                  {'score': score,
                                   'max_score': max_score,
                                   'percent': percent,
                                   'questions': questions,
                                   'session': session_score,
                                   'possible': session_possible,},
                                  context_instance = RequestContext(request))


def final_result_user(request, sitting, previous):
    quiz = sitting.quiz
    score = sitting.get_current_score()
    incorrect = sitting.get_incorrect_questions()
    max_score = quiz.question_set.all().select_subclasses().count()
    percent = sitting.get_percent_correct()

    sitting.mark_quiz_complete()

    if quiz.exam_paper == False:  #  if we do not plan to store the outcome
        sitting.delete()  #  delete the sitting to free up space

    if quiz.answers_at_end == False:
        return render_to_response('result.html',
                                  {'quiz': quiz,
                                   'score': score,
                                   'max_score': max_score,
                                   'percent': percent,
                                   'previous': previous,},
                                  context_instance = RequestContext(request))
    else:
        questions = quiz.question_set.all().select_subclasses()
        return render_to_response('result.html',
                                  {'quiz': quiz,
                                   'score': score,
                                   'max_score': max_score,
                                   'percent': percent,
                                   'questions': questions,
                                   'incorrect_questions': incorrect,},
                                  context_instance = RequestContext(request))


def question_check_anon(request, quiz):
    guess = request.GET['guess']
    question_id = request.GET['question_id']
    question = Question.objects.get_subclass(id = question_id)
    is_correct = question.check_if_correct(guess)

    if is_correct == True:
        outcome = "correct"
        current = request.session[str(quiz.id) + "_score"]
        request.session[str(quiz.id) + "_score"] = int(current) + 1
        anon_session_score(request, 1, 1)

    else:
        outcome = "incorrect"
        anon_session_score(request, 0, 1)

    if quiz.answers_at_end != True:
        return {'previous_answer': guess,
                'previous_outcome': outcome,
                'previous_question': question,}

    else:
        return {}


def question_check_user(request, quiz, sitting):
    guess = request.GET['guess']
    question_id = request.GET['question_id']
    question = Question.objects.get_subclass(id = question_id)
    is_correct = question.check_if_correct(guess)

    if is_correct == True:
        outcome = "correct"
        sitting.add_to_score(1)
        user_progress_score_update(request, question.category, 1, 1)
    else:
        outcome = "incorrect"
        sitting.add_incorrect_question(question)
        user_progress_score_update(request, question.category, 0, 1)

    if quiz.answers_at_end != True:
        return {'previous_answer': guess,
                'previous_outcome': outcome,
                'previous_question': question,}
    else:
        return {}


def user_progress_score_update(request, category, score, possible):
    try:
        progress = Progress.objects.get(user = request.user)

    except Progress.DoesNotExist:
        progress = Progress.objects.new_progress(request.user)

    progress.update_score(category, score, possible)


def anon_session_score(request, add = 0, possible = 0):
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
        request.session["session_score"] = (request.session["session_score"] + \
                                           add)

        request.session["session_score_possible"] = \
            (request.session["session_score_possible"] + possible)

    return request.session["session_score"], \
        request.session["session_score_possible"]


def progress(request):
    if request.user.is_authenticated() != True:
        #  display session score and encourage to sign up
        score, possible = anon_session_score(request)
        return render_to_response('signup.html',
                                  {'anon_score': score,
                                   'anon_possible': possible,},
                                  context_instance = RequestContext(request))

    try:
        progress = Progress.objects.get(user = request.user)

    except Progress.DoesNotExist:
        progress = Progress.objects.new_progress(request.user)
        return render_to_response('progress.html',
                                  {'new_user': True,},
                                  context_instance = RequestContext(request))

    cat_scores = progress.list_all_cat_scores()
    exams = progress.show_exams()

    return render_to_response('progress.html',
                              {'cat_scores': cat_scores,
                               'exams': exams},
                              context_instance = RequestContext(request))
