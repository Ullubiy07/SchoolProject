# Generated by Django 4.0.2 on 2022-02-06 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EquipApp', '0009_alter_equipment_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='equip_photos', verbose_name='Картинка'),
        ),
    ]
