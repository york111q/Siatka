# Generated by Django 3.2.2 on 2022-01-02 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zapisy', '0002_playeroldstats'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playeroldstats',
            name='player',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='zapisy.player'),
        ),
    ]