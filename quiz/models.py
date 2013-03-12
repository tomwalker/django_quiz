from django.db import models
from django.utils.encoding import smart_str 
from django.conf import settings
from django.contrib.auth.models import User



"""
Quiz is a container that can be filled with various different question types
or other content
"""


class CategoryManager(models.Manager):
    """
    custom manager for Progress class
    """ 
    def new_category(self, category):
        """
        add a new category
        """
        new_category = self.create(category=category)
        new_category.save()        

class Category(models.Model):
    
    category = models.CharField(max_length=250, 
                                blank=True, 
                                choices=CATEGORY_CHOICES,
                                unique=True,
                                null=True,
                                )
    

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    
    def __unicode__(self):
        return self.category


class Quiz(models.Model):
    
    title = models.CharField(max_length=60)
    
    description = models.TextField(blank=True)
    
    url = models.CharField(max_length=60, 
                               blank=False, 
                               help_text="an SEO friendly url",
                               verbose_name='SEO friendly url',
                               )
    
    category = models.ForeignKey(Category, null=True, blank=True, )
    
    random_order = models.BooleanField(blank=False,
                                       default=False,
                                       help_text="Display the questions in a random order or as they are set?",
                                       )
    
    answers_at_end = models.BooleanField(blank=False,
                                         default=False,
                                         help_text="Correct answer is NOT shown after question. Answers displayed at end",
                                       )
    
    exam_paper = models.BooleanField(blank=False,
                                         default=False,
                                         help_text="If yes, the result of each attempt by a user will be stored",
                                       )


    def save(self, force_insert=False, force_update=False):  # automatically converts url to lowercase 
        self.url = self.url.lower()
        super(Quiz, self).save(force_insert, force_update)


    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"


    def __unicode__(self):
        return self.title
    

class ProgressManager(models.Manager):
    """
    custom manager for Progress class
    """ 
    def new_progress(self, user):
        """
        method to call when a user is accessing the progress section for the first time
        """
        new_progress = self.create(user=user, score='')
        new_progress.save()
        return new_progress

class Progress(models.Model):
    """
    Stores the score for each category, max possible and previous exam paper scores
    
    data stored in csv using the format [category, score, possible, category, score, possible, ...]
    
    to do:
            combine the check and update functions into one
    """
    
    user = models.OneToOneField('auth.User')  #  one user per progress class
    
    score = models.TextField()  #  the god awful csv. guido forgive me. Always end this with a comma
    
    objects = ProgressManager()
    
    def list_all_cat_scores(self):
        """
        Returns a dict in which the key is the category name and the item is a list of three integers. 
        The first is the number of questions correct, the second is the possible best score,
        the third is the percentage correct 
        """
        import re  #  uh oh
        
        categories = Category.objects.all()  #  all the categories possible
        output = {}        
        
        for cat in categories:  # for each of the categories
            my_regex = re.escape(cat.category) + r",(\d+),(\d+),"  #  group 1 is score, group 2 is possible
            match = re.search(my_regex, self.score, re.IGNORECASE)
            
            if match:
                score = int(match.group(1))
                possible = int(match.group(2))
                percent = int(round((float(score) / float(possible)) * 100))
                score_list = [score, possible, percent]
                output[cat.category] = score_list
            
            
            else:  #  Is possible to remove/comment this section out
                temp = self.score
                temp = temp + cat.category + ",0,0,"  #  always end with a comma
                self.score = temp
                output[cat.category] = [0, 0]
                self.save()  #  add this new output to disk
            
        return output
            

    def check_cat_score(self, category_queried):
        """
        pass in a category, get the users score and possible score as x,y respectively
        
        note: score returned as integers
        """
        
        category_test = Category.objects.filter(category=category_queried).exists()
        
        if category_test == False:
            return "error",  "category does not exist"  #  to do: update
        
        import re  #  :'(  always a bad start
        my_regex = re.escape(category_queried) + r",(\d+),(\d+),"  #  group 1 is score, group 2 is possible
        
        match = re.search(my_regex, self.score, re.IGNORECASE)
        
        if match:
            score = int(match.group(1))
            possible = int(match.group(2))
            return score, possible
        
        else:  #  if not found, and since category exists, add category to the csv with 0 points
            """
            #  removed to lower disk writes
            temp = self.score
            temp = temp + category_queried + ",0,0,"  #  always end with a comma
            self.score = temp
            self.save()
            """  
            return 0, 0
    
    def update_score(self, category_queried, score_to_add, possible_to_add):
        """
        pass in category, amount to increase score and max possible increase if all were correct
        
        does not return anything
        
        data stored in csv using the format [category, score, possible, category, score, possible, ...] 
        """                                          
        
        category_test = Category.objects.filter(category=category_queried).exists()
        
        if category_test == False:
            return "error",  "category does not exist"  #  to do: update
        
        import re  #  :'(  always a bad start
        my_regex = re.escape(str(category_queried)) + r",(\d+),(\d+),"  #  group 1 is score, group 2 is possible
        
        match = re.search(my_regex, self.score, re.IGNORECASE)
        
        if match:
            current_score = int(match.group(1))
            current_possible = int(match.group(2))
                        
            updated_current_score = current_score + score_to_add
            updated_current_possible = current_possible + possible_to_add
            
            new_score = str(category_queried) + "," + str(updated_current_score) + "," + str(updated_current_possible) + ","
            
            temp = self.score
            found_instance = match.group()
            temp = temp.replace(found_instance, new_score)  #  swap the old score for the new one
            
            self.score = temp
            self.save()
        
        
        else:
            """
            if not present but a verified category, add with the points passed in
            """
            temp = self.score
            temp = temp + str(category_queried) + "," + str(score_to_add) + "," + str(possible_to_add) + ","
            self.score = temp
            self.save()  

    
    def show_exams(self,):
        """
        finds the previous exams marked as 'exam papers'
        
        returns a queryset of the exams
        """
        
        exams = Sitting.objects.filter(user=self.user).filter(complete=True)  #  list of exam objects from user that are complete
        
        return exams
    

class SittingManager(models.Manager):
    """
    custom manager for Sitting class
    """ 
    def new_sitting(self, user, quiz):
        """
        method to call at the start of each new attempt at a quiz
        """
        if quiz.random_order == True:
            question_set = quiz.question_set.all().order_by('?')
        else:
            question_set = quiz.question_set.all()
        
        questions = ""
        for question in question_set:
            questions = questions + str(question.id) + ","  #  string of IDs seperated by commas
        
        new_sitting = self.create(user=user,
                                  quiz=quiz,
                                  question_list = questions,
                                  incorrect_questions = "",
                                  current_score="0",                                  
                                  complete=False,                                  
                                  )
        new_sitting.save()
        return new_sitting


class Sitting(models.Model):
    """
    Used to store the progress of logged in users sitting an exam. Replaces the session system used by anon users.
    
    user is the logged in user. Anon users use sessions to track progress
    quiz
    question_list is a list of id's of the unanswered questions. Stored as a textfield to allow >255 chars. CSV
    incorrect_questions is a list of id's of the questions answered wrongly
    current_Score is total of answered questions value. Needs to be converted to int when used.
    complete - True when exam complete. Should only be stored if quiz.exam_paper is trued, or DB will become huge 
    """
    
    user = models.ForeignKey('auth.User')  #  one user per exam class
    
    quiz = models.ForeignKey(Quiz)
    
    question_list = models.TextField()  #  another awful csv. Always end with a comma
    
    incorrect_questions = models.TextField(blank=True)  #  more awful csv. Always end with a comma
    
    current_score = models.TextField()  #  a string of the score ie 19  convert to int for use
    
    complete = models.BooleanField(default=False,)
    
    objects = SittingManager()
    
    def get_next_question(self):
        """
        Returns the next question ID (as an integer).
        Does NOT remove the question from the front of the list.
        """
        first_comma = self.question_list.find(',')  #  finds the index of the first comma in the string
        if first_comma == -1 or first_comma == 0:  #  if no question number is found
            return False
        qID = self.question_list[:first_comma]  #  up to but not including the first comma
        
        return qID
    
    def remove_first_question(self):
        """
        Removes the first question on the list.
        Does not return a value.
        """
        first_comma = self.question_list.find(',')  #  finds the index of the first comma in the string
        if first_comma != -1 or first_comma != 0:  #  if question number IS found
            temp = self.question_list[first_comma+1:]  #  saves from the first number after the first comma
            self.question_list = temp
        self.save()
            
    def add_to_score(self, points):
        """
        Adds the input (points) to the running total.
        Does not return anything
        """
        present_score = self.get_current_score()
        present_score = present_score + points
        self.current_score = str(present_score)
        
    def get_current_score(self):
        """
        returns the current score as an integer
        """
        return int(self.current_score)
    
    def mark_quiz_complete(self):
        """
        Changes the quiz to complete.
        Does not return anything
        """
        self.complete = True
        self.save()
        
    def add_incorrect_question(self, question):
        """
        Adds the uid of an incorrect question to the list of incorrect questions
        Does not return anything
        """
        current = self.incorrect_questions
        question_id = question.id
        if current == "":
            updated = str(question_id) + ","
        else:
            updated = current + str(question_id) + ","
        self.incorrect_questions = updated
        self.save()
        
    def get_incorrect_questions(self):
        """
        Returns a list of IDs that indicate all the questions that have been answered incorrectly in this sitting
        """
        question_list = self.incorrect_questions  #  string of question IDs as CSV  ie 32,19,22,3,75
        split_questions = question_list.split(',')  # list of numbers [32,19,22,3,75]
        return split_questions