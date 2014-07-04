from django.conf.urls import patterns, url

from .views import QuizListView, CategoriesListView,\
    ViewQuizListByCategory, QuizUserProgressView


urlpatterns = patterns('quiz.views',
                       # quiz base url
                       url(regex=r'^$',
                           view=QuizListView.as_view(),
                           name='quiz_index'),

                       url(regex=r'^category/$',
                           view=CategoriesListView.as_view(),
                           name='quiz_category_list_all'),

                       # quiz category: list quizzes
                       url(regex=r'^category/(?P<category_name>[\w.-]+)/$',
                           view=ViewQuizListByCategory.as_view(),
                           name='quiz_category_list_matching'),

                       #  progress
                       url(regex=r'^progress/$',
                           view=QuizUserProgressView.as_view(),
                           name='quiz_progress'),

                       #  passes variable 'quiz_name' to quiz_take view
                       url(regex=r'^(?P<quiz_name>[\w-]+)/$',
                           view='quiz_take',
                           name='quiz_start_page'),

                       url(regex=r'^(?P<quiz_name>[\w-]+)/take/$',
                           view='quiz_take',
                           name='quiz_question'),
                       )
