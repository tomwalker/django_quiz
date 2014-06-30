import re  #  uh oh

from django.db import models
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.auth.models import User

from model_utils.managers import InheritanceManager
# the above taken from:
# https://django-model-utils.readthedocs.org/en/latest/managers.html


"""
If you want to prepopulate the category choices then here is an example.
Uncomment 'choices' in the category model.
"""
CATEGORY_CHOICES = ( ('Endocrinology', 'Endocrinology'),
                     ('Dermatology', 'Dermatology'),
                     ('Cellular Biology', 'Cellular Biology'),
                     ('Neurology', 'Neurology'),
                     ('Gastroenterology', 'Gastroenterology'),
                     ('Statistics', 'Statistics'),
                     ('Rheumatology', 'Rheumatology'),
                     ('Tropical medicine', 'Tropical medicine'),
                     ('Respiratory', 'Respiratory'),
                     ('Immunology', 'Immunology'),
                     ('Nephrology', 'Nephrology'),
                     ('Genetic Medicine', 'Genetic Medicine'),
                     ('Haematology', 'Haematology'),
                     ('Pharmacology', 'Pharmacology'),
                     ('Physiology', 'Physiology'),
                     ('Ophthalmology', 'Ophthalmology'),
                     ('Anatomy', 'Anatomy'),
                     ('Biochemistry', 'Biochemistry'),
                     ('empty', 'empty'),
                     ('Psychiatry', 'Psychiatry'),
                     ('Cardiology', 'Cardiology'),
                    )


class CategoryManager(models.Manager):

    def new_category(self, category):
        new_category = self.create(category =
                                   re.sub('\s+', '-', category).lower())

        new_category.save()
        return new_category


class Category(models.Model):

    category = models.CharField(max_length = 250,
                                blank = True,
                                # choices = CATEGORY_CHOICES,
                                unique = True,
                                null = True,)

    objects = CategoryManager()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.category


class Quiz(models.Model):

    title = models.CharField(max_length = 60,
                             blank = False,)

    description = models.TextField(blank = True,
                                   help_text = ("a description of the quiz"),)

    url = models.CharField(max_length = 60,
                           blank = False,
                           help_text = ("a user friendly url"),
                           verbose_name = ('user friendly url'),)

    category = models.ForeignKey(Category,
                                 null = True,
                                 blank = True,)

    random_order = models.BooleanField(blank = False,
                                       default = False,
                                       help_text = ("Display the questions in \
                                                    a random order or as they \
                                                    are set?"),)

    answers_at_end = models.BooleanField(blank = False,
                                         default = False,
                                         help_text = ("Correct answer is NOT \
                                                      shown after question. \
                                                      Answers displayed at \
                                                      the end"),)

    exam_paper = models.BooleanField(blank = False,
                                     default = False,
                                     help_text = ("If yes, the result of each \
                                                  attempt by a user will be \
                                                  stored"),)

    single_attempt = models.BooleanField(blank = False,
                                         default = False,
                                         help_text = ("If yes, only one \
                                                       attempt by a user will \
                                                       be permitted. Non \
                                                       users cannot sit \
                                                       this exam."),)


    def save(self, force_insert = False, force_update = False, *args, **kwargs):
        self.url = re.sub('\s+', '-', self.url).lower()

        self.url = ''.join(letter for letter in self.url if
                           letter.isalnum() or letter == '-')

        if self.single_attempt == True:
            self.exam_paper = True

        super(Quiz, self).save(force_insert, force_update, *args, **kwargs)


    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"


    def __unicode__(self):
        return self.title


"""
Progress is used to track an individual signed in users score on different
quiz's and categories
"""

class ProgressManager(models.Manager):

    def new_progress(self, user):
        new_progress = self.create(user = user, score = '')
        new_progress.save()
        return new_progress


class Progress(models.Model):
    """
    Currently stores the score for each category, max possible they could
    have got, and previous exam paper scores.

    Data stored in csv using the format:
        category, score, possible, category, score, possible, ...
    """
    user = models.OneToOneField('auth.User')  #  one user per progress class

    score = models.CommaSeparatedIntegerField(max_length = 1024)

    objects = ProgressManager()

    class Meta:
        verbose_name = "User Progress"
        verbose_name_plural = "User progress records"

    def list_all_cat_scores(self):
        """
        Returns a dict in which the key is the category name and the item is
        a list of three integers.

        The first is the number of questions correct,
        the second is the possible best score,
        the third is the percentage correct.

        The dict will have one key for every category that you have defined
        """
        categories = Category.objects.all()
        score_before = self.score
        output = {}

        for cat in categories:
            to_find = re.escape(cat.category) + r",(\d+),(\d+),"
            #  group 1 is score, group 2 is possible

            match = re.search(to_find, self.score, re.IGNORECASE)

            if match:
                score = int(match.group(1))
                possible = int(match.group(2))

                try:
                    percent = int(round((float(score) / float(possible)) * 100))
                except:
                    percent = 0

                score_list = [score, possible, percent]
                output[cat.category] = score_list


            else:  #  if category has not been added yet, add it.
                temp = self.score + cat.category + ",0,0,"
                self.score = temp
                output[cat.category] = [0, 0]


        if len(self.score) > len(score_before):
            """
            If a new category has been added, save changes. Otherwise nothing
            will be saved.
            """
            self.save()

        return output


    def check_cat_score(self, category_queried):
        """
        Pass in a category, get the users score and possible maximum score
        as the integers x,y respectively
        """

        category_test = Category.objects.filter(category = category_queried) \
                                        .exists()

        if category_test == False:
            return "error",  "category does not exist"

        to_find = re.escape(category_queried) + r",(\d+),(\d+),"

        match = re.search(to_find, self.score, re.IGNORECASE)

        if match:
            score = int(match.group(1))
            possible = int(match.group(2))
            return score, possible

        else:  #  if not found but category exists, add category  with 0 points
            temp = self.score + category_queried + ",0,0,"
            self.score = temp
            self.save()

            return 0, 0


    def update_score(self, category_queried, score_to_add, possible_to_add):
        """
        Pass in category, amount to increase score and max possible.
        Increase if all were correct.

        Does not return anything.

        TO DO: Raise error when necessary
        """

        category_test = Category.objects.filter(category = category_queried) \
                                        .exists()

        if any([category_test == False, score_to_add == False,
                possible_to_add == False, str(score_to_add).isdigit() == False,
                str(possible_to_add).isdigit() == False]):
            return "error",  "category does not exist or invalid score"

        to_find = re.escape(str(category_queried)) + r",(\d+),(\d+),"

        match = re.search(to_find, self.score, re.IGNORECASE)

        if match:
            current_score = int(match.group(1))
            current_possible = int(match.group(2))

            updated_current_score = current_score + score_to_add
            updated_current_possible = current_possible + possible_to_add

            new_score = (str(category_queried) + "," +
                         str(updated_current_score) + "," +
                         str(updated_current_possible) + ",")

            temp = self.score
            found_instance = match.group()

            # swap old score for the new one
            self.score = temp.replace(found_instance, new_score)
            self.save()

        else:
            """
            if not present but existing category, add with the points passed in
            """
            temp = (self.score +
                    str(category_queried) + "," +
                    str(score_to_add) + "," +
                    str(possible_to_add) + ",")
            self.score = temp
            self.save()


    def show_exams(self):
        """
        Finds the previous quizzes marked as 'exam papers'.
        Returns a queryset of complete exams.
        """
        return Sitting.objects.filter(user = self.user) \
                              .filter(complete = True)


class SittingManager(models.Manager):

    def new_sitting(self, user, quiz):
        if quiz.random_order == True:
            question_set = quiz.question_set.all() \
                                            .select_subclasses() \
                                            .order_by('?')
        else:
            question_set = quiz.question_set.all() \
                                            .select_subclasses()

        questions = ""
        for question in question_set:
            questions = (questions + str(question.id) + ",")

        new_sitting = self.create(user = user,
                                  quiz = quiz,
                                  question_list = questions,
                                  incorrect_questions = "",
                                  current_score = 0,
                                  complete = False,)
        new_sitting.save()
        return new_sitting


class Sitting(models.Model):
    """
    Used to store the progress of logged in users sitting a quiz.
    Replaces the session system used by anon users.

    Question_list is a list of integers which represent id's of
    the unanswered questions in csv format.

    Incorrect_questions is a list in the same format.

    Sitting deleted when quiz finished unless quiz.exam_paper is true.
    """

    user = models.ForeignKey('auth.User')

    quiz = models.ForeignKey(Quiz)

    question_list = models.CommaSeparatedIntegerField(max_length = 1024)

    incorrect_questions = models.CommaSeparatedIntegerField(max_length = 1024,
                                                            blank = True)

    current_score = models.IntegerField()

    complete = models.BooleanField(default = False, blank = False)

    objects = SittingManager()

    def get_next_question(self):
        """
        Returns integer of the next question ID.
        If no question is found, returns False
        Does NOT remove the question from the front of the list.
        """
        first_comma = self.question_list.find(',')
        if first_comma == -1 or first_comma == 0:
            return False

        return int(self.question_list[:first_comma])


    def remove_first_question(self):
        first_comma = self.question_list.find(',')
        if first_comma != -1 or first_comma != 0:
            self.question_list = self.question_list[first_comma+1:]
            self.save()

    def add_to_score(self, points):
        present_score = int(self.get_current_score())
        updated_score = present_score + int(points)
        self.current_score = updated_score
        self.save()

    def get_current_score(self):
        return self.current_score

    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = self.quiz.question_set.all().select_subclasses().count()
        if divisor < 1:
            return 0            # prevent divide by zero error

        if dividend > divisor:
            return 100

        correct = int(round((dividend / divisor) * 100))

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_quiz_complete(self):
        self.complete = True
        self.save()

    def add_incorrect_question(self, question):
        """
        Adds uid of incorrect question to the list.
        The question object must be passed in.
        """
        if isinstance(question, Question) == False:
            return False
        current_incorrect = self.incorrect_questions
        question_id = question.id

        self.incorrect_questions = current_incorrect + str(question_id) + ","
        self.save()

    def get_incorrect_questions(self):
        question_list = self.incorrect_questions
        split_questions = filter(None, question_list.split(','))
        return split_questions


class Question(models.Model):
    """
    Base class for all question types.
    Shared properties placed here.
    """

    quiz = models.ManyToManyField(Quiz, blank = True, )

    category = models.ForeignKey(Category, blank = True, null = True, )

    content = models.CharField(max_length = 1000,
                               blank = False,
                               help_text = ("Enter the question text that " +
                                            "you want displayed"),
                               verbose_name = 'Question',)

    explanation = models.TextField(max_length = 2000,
                                   blank = True,
                                   help_text = ("Explanation to be shown " +
                                                "after the question has " +
                                                "been answered."),
                                   verbose_name = 'Explanation',)

    objects = InheritanceManager()

    class Meta:
        ordering = ['category']

    def __unicode__(self):
        return self.content
