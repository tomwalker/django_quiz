from django import template
from multichoice.models import Question, Answer

register = template.Library()

@register.inclusion_tag('answers_for_question.html', takes_context=True)
def answers_for_question(context, question, quiz):
    """
    Displays the possible answers to a question
    """
    answers = Answer.objects.filter(question__id=question.id).order_by('?')
    return {'answers': answers, 'quiz': quiz}

@register.inclusion_tag('correct_answer.html', takes_context=True)
def correct_answer(context, previous):
    """
    processes the correct answer based on the previous question dict
    """
    q = previous['previous_question']
    answers = Answer.objects.filter(question__id=q.id)
    return {'answers': answers, }

@register.inclusion_tag('correct_answer.html', takes_context=True)
def correct_answer_for_all(context, question):
    """
    processes the correct answer based on a given question object
    """
    answers = Answer.objects.filter(question__id=question.id)
    return {'answers': answers, }

@register.inclusion_tag('correct_answer.html', takes_context=True)
def correct_answer_for_all_with_users_incorrect(context, question, incorrect_list):
    """
    processes the correct answer based on a given question object
    if the answer is incorrect, informs the user
    """
    answers = Answer.objects.filter(question__id=question.id)  #  if question was answered wrongly, tell the user
    question_id = str(question.id)
    if question_id in incorrect_list:
        user_was_incorrect = True
    else:
        user_was_incorrect = False
    return {'answers': answers, 'user_was_incorrect': user_was_incorrect, }