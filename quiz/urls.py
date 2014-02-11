from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       
    #  progress 
    url(r'^progress/$', 'quiz.views.progress'),
    url(r'^progress$', 'quiz.views.progress'),

    
    #  passes variable 'quiz_name' to quiz_take view
    url(r'^(?P<quiz_name>[\w-]+)/$',
        'quiz.views.quiz_take'),  #  quiz/

    url(r'^(?P<quiz_name>[\w-]+)$',
        'quiz.views.quiz_take'),  #  quiz

    url(r'^(?P<quiz_name>[\w-]+)/take/$',
        'quiz.views.quiz_take'),  #  quiz/take/

    url(r'^(?P<quiz_name>[\w-]+)take$',
        'quiz.views.quiz_take')  #  quiz/take



)
