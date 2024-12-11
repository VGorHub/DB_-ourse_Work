# Generated by Django 4.2.16 on 2024-12-11 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_employee_is_fired_alter_testresult_test'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='image',
            field=models.ImageField(blank=True, db_column='Image for the Answer', null=True, upload_to='answer_images/'),
        ),
        migrations.AlterField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, db_column='Image for the Question', null=True, upload_to='question_images/'),
        ),
    ]
