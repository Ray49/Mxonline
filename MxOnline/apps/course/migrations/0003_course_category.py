# Generated by Django 2.0.2 on 2018-07-27 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_course_course_org'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.CharField(default='后端开发', max_length=30, verbose_name='课程类别'),
        ),
    ]