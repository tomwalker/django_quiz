from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from parler.forms import TranslatableModelForm

from .models import Quiz, Category, SubCategory, Progress, Question
from multichoice.models import MCQuestion, Answer
from true_false.models import TF_Question
from essay.models import Essay_Question


class QuizAdminForm(TranslatableModelForm):
    """
    below is from
    http://stackoverflow.com/questions/11657682/
    django-admin-interface-using-horizontal-filter-with-
    inline-manytomany-field
    """

    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all(),
        required=False,
        label=_("Questions"),
        widget=FilteredSelectMultiple(verbose_name=_("Questions"), is_stacked=False),
    )

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["questions"].initial = self.instance.question_set.all()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data["questions"])
        self.save_m2m()
        return quiz


class QuizAdmin(TranslatableAdmin):
    form = QuizAdminForm

    list_display = ("title", "category")
    list_filter = ("category",)
    search_fields = ("translations__description", "translations__category")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "url",
                    "category",
                    "description",
                    ["success_text", "fail_text"],
                    "random_order",
                    "max_questions",
                    "answers_at_end",
                    "exam_paper",
                    "single_attempt",
                    "pass_mark",
                    "draft",
                    "questions",
                ),
            },
        ),
    )

    def get_prepopulated_fields(self, request, obj=None):
        # can't use `prepopulated_fields = ..` because it breaks the admin validation
        # for translated fields. This is the official django-parler workaround.
        return {
            'url': ('title',)
        }

class CategoryAdmin(TranslatableAdmin):
    search_fields = ("translations__category",)


class SubCategoryAdmin(TranslatableAdmin):
    search_fields = ("sub_category",)
    list_display = ("sub_category", "category")
    list_filter = ("category",)


class ProgressAdmin(admin.ModelAdmin):
    """
    to do:
            create a user section
    """

    search_fields = ("user", "score")


class MCQuestionAdmin(TranslatableAdmin, PolymorphicChildModelAdmin):
    class AnswerInline(TranslatableTabularInline):
        model = Answer

    base_model = MCQuestion
    list_display = ("content", "category")
    list_filter = ("category",)
    fields = (
        "content",
        "category",
        "sub_category",
        "figure",
        "quiz",
        "explanation",
        "answer_order",
    )

    filter_horizontal = ("quiz",)

    inlines = [
        AnswerInline,
    ]


class TFQuestionAdmin(TranslatableAdmin, PolymorphicChildModelAdmin):
    base_model = TF_Question

    list_display = ("content", "category")
    list_filter = ("category",)
    fields = (
        "content",
        "category",
        "sub_category",
        "figure",
        "quiz",
        "explanation",
        "correct",
    )

    filter_horizontal = ("quiz",)


class EssayQuestionAdmin(TranslatableAdmin):
    list_display = ("content", "category")
    list_filter = ("category",)
    fields = ("content", "category", "sub_category", "quiz", "explanation")
    search_fields = ("transltations__content", "transltations__explanation")
    filter_horizontal = ("quiz",)


class QuestionAdmin(TranslatableAdmin, PolymorphicParentModelAdmin):
    base_model = Question
    child_models = (MCQuestion, TF_Question)

    list_display = ("content", "category")
    search_fields = ("base_translations__content", "base_translations__explanation")


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(TF_Question, TFQuestionAdmin)
admin.site.register(Essay_Question, EssayQuestionAdmin)
