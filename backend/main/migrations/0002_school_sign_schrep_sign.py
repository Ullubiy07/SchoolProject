# Generated by Django 4.0.2 on 2022-02-04 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='sign',
            field=models.FileField(blank=True, null=True, upload_to='school_signs'),
        ),
        migrations.AddField(
            model_name='schrep',
            name='sign',
            field=models.FileField(blank=True, null=True, upload_to='sch_rep_signs'),
        ),
    ]
