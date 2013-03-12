from django.db import models
from quiz.models import Quiz, Category

"""
Multiple choice style question for quiz

"""

class Question(models.Model):

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
    
    
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['category']


    def __unicode__(self):
        return self.content
    

class Answer(models.Model):
    question = models.ForeignKey(Question)
    
    content = models.CharField(max_length=1000, 
                               blank=False, 
                               help_text="Enter the answer text that you want displayed",
                               )
    
    correct = models.BooleanField(blank=False, 
                                  default=False,
                                  help_text="Is this a correct answer?"
                                  )
    
    def __unicode__(self):
        return self.content