# Generated by Django 4.0.2 on 2022-02-04 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_school_sign_alter_schrep_sign'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='sign_image',
            field=models.ImageField(blank=True, null=True, upload_to='school_sign_images'),
        ),
        migrations.AddField(
            model_name='schrep',
            name='sign_image',
            field=models.ImageField(blank=True, null=True, upload_to='sch_rep_sign_images'),
        ),
    ]
