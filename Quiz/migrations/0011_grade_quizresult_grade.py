# Generated by Django 4.2.3 on 2023-07-24 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Quiz', '0010_quizresult_total_points_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('minimum_score', models.IntegerField()),
                ('maximum_score', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='quizresult',
            name='grade',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Quiz.grade'),
        ),
    ]
