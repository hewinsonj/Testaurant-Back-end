from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Food(models.Model):
  # define fields
  # https://docs.djangoproject.com/en/3.0/ref/models/fields/
  name = models.CharField(max_length=100)
  ingredients = models.CharField(max_length=1000)
  con_egg = models.BooleanField()
  con_tree_nut = models.BooleanField()
  con_peanut = models.BooleanField()
  con_shellfish = models.BooleanField()
  con_soy = models.BooleanField()
  con_fish = models.BooleanField()
  con_wheat = models.BooleanField()
  con_sesame = models.BooleanField()
  con_gluten = models.BooleanField()
  con_dairy = models.BooleanField()
  is_vegan = models.BooleanField()
  is_vegetarian = models.BooleanField()
  owner = models.ForeignKey(
      get_user_model(),
      on_delete=models.CASCADE
  )

  def __str__(self):
    # This must return a string
    return f"The {self.name}'s ingredients are: {self.ingredients}. Contains egg: {self.con_egg}, Contains tree nuts: {self.con_tree_nut}, Contains peanut: {self.con_peanut}, Contains shellfish: {self.con_shellfish}, Contains soy: {self.con_soy}, Contains fish: {self.con_fish}, Contains wheat: {self.con_wheat}, Contains sesame: {self.con_sesame}, Contains gluten: {self.con_gluten}, Contains dairy: {self.con_dairy}. Vegan: {self.is_vegan}, Vegetarian: {self.is_vegetarian}"

  def as_dict(self):
    """Returns dictionary version of Food models"""
    return {
        'id': self.id,
        'name': self.name,
        'ingredients': self.ingredients,
        'con_egg': self.con_egg,
        'con_tree_nut': self.con_tree_nut,
        'con_peanut': self.con_peanut,
        'con_shellfish': self.con_shellfish,
        'con_soy': self.con_soy,
        'con_fish': self.con_fish,
        'con_wheat': self.con_wheat,
        'con_sesame': self.con_sesame,
        'con_gluten': self.con_gluten,
        'con_dairy': self.con_dairy,
        'is_vegan': self.is_vegan,
        'is_vegetarian': self.is_vegetarian,
    }