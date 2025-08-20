from django.db import models
from django.contrib.auth import get_user_model
from .test_this import Test_this

# Create your models here.
class Result(models.Model):
  # define fields
  # https://docs.djangoproject.com/en/3.0/ref/models/fields/
    score = models.CharField(max_length=20)
    correct = models.CharField(max_length=10)
    wrong = models.CharField(max_length=10)
    wrong_question_ids = models.JSONField(default=list, blank=True)
    total = models.CharField(max_length=10)
    percent = models.CharField(max_length=10)
    time = models.CharField(max_length=20)
    time_completed = models.CharField(max_length=10)
    the_test = models.ForeignKey(
        Test_this,
        on_delete=models.CASCADE,
        related_name='test_results'
    )
    # Link result to a specific restaurant (nullable for existing data; make required after backfill)
    restaurant = models.ForeignKey(
        "Restaurant",
        on_delete=models.CASCADE,
        related_name="results",
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # This must return a string
        return f"{self.owner}'s score is {self.score} or {self.percent}% on the ({self.the_test}) test. {self.correct} correct, {self.wrong} wrong, {self.total} total questions, completion time was {self.time}"

    def as_dict(self):
        """Returns dictionary version of Result models"""
        return {
            'id': self.id,
            'score': self.score,
            'correct': self.correct,
            'wrong': self.wrong,
            'wrong_question_ids': self.wrong_question_ids,
            'total': self.total,
            'percent': self.percent,
            'time': self.time,
            'time_completed': self.time_completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'restaurant': self.restaurant_id,
        }