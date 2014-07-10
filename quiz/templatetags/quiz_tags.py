from django import template

from multichoice.models import Answer, MCQuestion

register = template.Library()


@register.inclusion_tag('answers_for_mc_question.html', takes_context=True)
def answers_for_mc_question(context, question):
    return {'answers': Answer.objects.filter(question=question).order_by('?')}


@register.inclusion_tag('correct_answer.html', takes_context=True)
def correct_answer(context, previous):
    """
    processes the correct answer based on the previous question dict
    """
    q = previous['previous_question']
    q_type = q.__class__.__name__
    previous_answer_id = context['previous']['previous_answer']
    if isinstance(q, MCQuestion):
        previous_answer_id = int(previous_answer_id)
    return {'answers': q.get_answers(),
            'question_type': {q_type: True},
            'previous_answer_id': previous_answer_id}


@register.inclusion_tag('correct_answer.html', takes_context=True)
def correct_answer_for_all(context, question):
    """
    processes the correct answer based on a given question object
    if the answer is incorrect, informs the user
    """
    answers = question.get_answers()
    incorrect_list = context.get('incorrect_questions', '')
    if str(question.id) in incorrect_list:
        user_was_incorrect = True
    else:
        user_was_incorrect = False
    return {'answers': answers, 'user_was_incorrect': user_was_incorrect}


@register.inclusion_tag('user_previous_exam.html', takes_context=True)
def user_previous_exam(context, exam):
    """
    Provides details of finished exams
    """
    final_score = exam.current_score
    possible_score = exam.quiz.get_max_score()
    percent = int(round((float(final_score) / float(possible_score)) * 100))
    return {'title': exam.quiz.title,
            'score': final_score,
            'possible': possible_score,
            'percent': percent}
