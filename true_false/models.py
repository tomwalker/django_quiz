from django.db import models
from quiz.models import Quiz, Category
from multichoice.models import Question

class TF_Question(Question):
    """
    Using the multichoice question as the base class, inheriting properties:
    quiz - quiz that it belongs to
    category
    content - question text
    explanation - shown afterwards
    """

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text="Tick this if the question is true."+
                                  " Leave it blank for false."
                                  )

    class Meta:
        verbose_name = "True/False Question"
        verbose_name_plural = "True/False Questions"
        ordering = ['category']


    def __unicode__(self):
        return self.content[:50]
