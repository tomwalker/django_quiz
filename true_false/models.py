from django.db import models
from django_quiz.quiz.models import Quiz, Category

class TF_Question(models.Model):

    quiz = models.ManyToManyField(Quiz, blank=True, )
    
    category = models.ForeignKey(Category, blank=True, null=True, )
    
    content = models.CharField(max_length=1000, 
                               blank=False, 
                               help_text="Enter the question text that you want displayed",
                               verbose_name='Question',
                               )
    
    explanation = models.TextField(max_length=2000,
                                   blank=True,
                                   help_text="Explanation to be shown after the question has been answered.",
                                   verbose_name='Explanation',
                               )
    
    correct = models.BooleanField(blank=False, 
                                  default=False,
                                  help_text="Is this question true or false?"
                                  )
    
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['category']


    def __unicode__(self):
        return self.content
    
