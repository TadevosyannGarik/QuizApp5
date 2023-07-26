# Generated by Django 4.2.3 on 2023-07-24 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0009_question_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizresult',
            name='total_points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='quizresult',
            name='date_completed',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='quizresult',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]