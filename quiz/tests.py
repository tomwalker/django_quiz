from django.test import TestCase

from quiz.models import Category, Quiz, Progress, Sitting, Question

class TestCategory(TestCase):
    def setUp(self):
        Category.objects.new_category(category = "elderberries")
