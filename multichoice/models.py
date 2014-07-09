from django.db import models
from quiz.models import Question


class MCQuestion(Question):

    def check_if_correct(self, guess):
        answer = Answer.objects.get(id=guess)

        if answer.correct is True:
            return True
        else:
            return False

    def get_answers(self):
        return Answer.objects.filter(question=self)

    class Meta:
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"


class Answer(models.Model):
    question = models.ForeignKey(MCQuestion)

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text="Enter the answer text that "
                                         "you want displayed")

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text="Is this a correct answer?")

    def __unicode__(self):
        return unicode(self.content)
