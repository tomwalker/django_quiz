from django.conf.urls import patterns, url


urlpatterns = patterns('quiz.views',
                       # quiz base url
                       url(regex=r'^$',
                           view='index',
                           name='quiz_index'),

                       url(regex=r'^category/$',
                           view='list_categories',
                           name='quiz_category_list_all'),

                       # quiz category: list quizzes
                       url(regex=r'^category/(?P<slug>[\w.-]+)/$',
                           view='view_category',
                           name='quiz_category_list_matching'),

                       #  progress
                       url(regex=r'^progress/$',
                           view='progress',
                           name='quiz_progress'),

                       #  passes variable 'quiz_name' to quiz_take view
                       url(regex=r'^(?P<quiz_name>[\w-]+)/$',
                           view='quiz_take',
                           name='quiz_start_page'),

                       url(regex=r'^(?P<quiz_name>[\w-]+)/take/$',
                           view='quiz_take',
                           name='quiz_question'),
                       )
