from django.db import models
from quiz.models import Quiz, Category, Question


class MCQuestion(Question):

    def check_if_correct(self, guess):
        answer = Answer.objects.get(id = guess)

        if answer.correct == True:
            return True
        else:
            return False

    class Meta:
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"


class Answer(models.Model):
    question = models.ForeignKey(MCQuestion)

    content = models.CharField(max_length = 1000,
                               blank = False,
                               help_text = ("Enter the answer text that " +
                                            "you want displayed"),)

    correct = models.BooleanField(blank = False,
                                  default = False,
                                  help_text = "Is this a correct answer?",)

    def __unicode__(self):
        return self.content
