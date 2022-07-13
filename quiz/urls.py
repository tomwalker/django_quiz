from django.urls import path

from .views import (
    QuizListView,
    CategoriesListView,
    ViewQuizListByCategory,
    QuizUserProgressView,
    QuizMarkingList,
    QuizMarkingDetail,
    QuizDetailView,
    QuizTake,
)

urlpatterns = [
    path("", view=QuizListView.as_view(), name="quiz_index"),
    path("category/", view=CategoriesListView.as_view(), name="quiz_category_list_all"),
    path(
        "category/<str:category_name>",
        view=ViewQuizListByCategory.as_view(),
        name="quiz_category_list_matching",
    ),
    path("progress/", view=QuizUserProgressView.as_view(), name="quiz_progress"),
    path("marking/", view=QuizMarkingList.as_view(), name="quiz_marking"),
    path(
        "marking/<int:pk>/",
        view=QuizMarkingDetail.as_view(),
        name="quiz_marking_detail",
    ),
    #  passes variable 'quiz_name' to quiz_take view
    path("<slug:slug>/", view=QuizDetailView.as_view(), name="quiz_start_page"),
    path("<str:quiz_name>/take/", view=QuizTake.as_view(), name="quiz_question"),
]
