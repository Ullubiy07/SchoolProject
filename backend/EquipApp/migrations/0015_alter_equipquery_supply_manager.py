# Generated by Django 4.1.3 on 2023-02-02 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_remove_schrep_credential_id_supplymanager'),
        ('EquipApp', '0014_remove_equipquery_sch_rep_equipquery_supply_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipquery',
            name='supply_manager',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.supplymanager', verbose_name='Завхоз'),
        ),
    ]
