# Generated by Django 3.2.2 on 2021-10-06 07:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('zapisy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zapisy.localization'),
        ),
    ]
