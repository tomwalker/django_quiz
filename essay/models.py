from quiz.models import Question


class Essay_Question(Question):

    def check_if_correct(self):
        return False

    def get_answers(self):
        return False

    def get_answers_list(self):
        return False

    class Meta:
        verbose_name = "Essay style question"
