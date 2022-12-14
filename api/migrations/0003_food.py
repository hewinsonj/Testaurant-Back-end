# Generated by Django 4.1 on 2022-11-22 19:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_question'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('ingredients', models.CharField(max_length=1000)),
                ('con_egg', models.BooleanField()),
                ('con_tree_nut', models.BooleanField()),
                ('con_peanut', models.BooleanField()),
                ('con_shellfish', models.BooleanField()),
                ('con_soy', models.BooleanField()),
                ('con_fish', models.BooleanField()),
                ('con_wheat', models.BooleanField()),
                ('con_sesame', models.BooleanField()),
                ('con_gluten', models.BooleanField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
