# Generated by Django 4.1.3 on 2023-01-24 22:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EquipApp', '0011_alter_equipment_schedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipbooking',
            name='contract',
            field=models.FileField(blank=True, null=True, upload_to='contracts', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='Договор'),
        ),
    ]