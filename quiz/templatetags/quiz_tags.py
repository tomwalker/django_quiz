from django import template

register = template.Library()


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
    previous = {'answers': answers}

    return {'previous': previous,
            'user_was_incorrect': user_was_incorrect}
