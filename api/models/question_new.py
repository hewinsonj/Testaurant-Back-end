from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Question_new(models.Model):
  # define fields
  # https://docs.djangoproject.com/en/3.0/ref/models/fields/
    question_str = models.CharField(max_length=1000)
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    option4 = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    pass
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )

    def __str__(self):
        # This must return a string
        return f"{self.question_str}? {self.option1}, {self.option2}, {self.option3}, {self.option4}. Correct answer is: {self.answer}"

    def as_dict(self):
        """Returns dictionary version of Question models"""
        return {
            'id': self.id,
            'question_str': self.question_str,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'answer': self.answer
        }


