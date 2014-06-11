from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       # quiz base url
                       url(r'^$',
                           'quiz.views.index',
                           name = 'quiz_index'),

                       url(r'^category/$',
                           'quiz.views.list_categories',
                           name = 'quiz_category_list_all'),

                       # quiz category: list quizzes
                       url(r'^category/(?P<slug>[\w.-]+)/$',
                           'quiz.views.view_category',
                           name='quiz_category_list_matching'),

                       #  progress
                       url(r'^progress/$',
                           'quiz.views.progress',
                           name = 'quiz_progress'),

                       #  passes variable 'quiz_name' to quiz_take view
                       url(r'^(?P<quiz_name>[\w-]+)/$',
                           'quiz.views.quiz_take',
                           name = 'quiz_start_page'),

                       url(r'^(?P<quiz_name>[\w-]+)/take/$',
                           'quiz.views.quiz_take',
                           name = 'quiz_question'),

)
