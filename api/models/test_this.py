from django.db import models
from django.contrib.auth import get_user_model
from .question_new import Question_new

# Create your models here.
class Test_this(models.Model):
  # define fields
  # https://docs.djangoproject.com/en/3.0/ref/models/fields/
    name = models.CharField(max_length=1000)
    question_new = models.ManyToManyField('Question_new', related_name='question_new', blank=True)
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    
    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # This must return a string
        return f"{self.name}"

    def as_dict(self):
        """Returns dictionary version of Test models"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }