# Generated by Django 3.2.2 on 2022-01-02 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zapisy', '0003_alter_playeroldstats_player'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='localization',
            name='image',
        ),
        migrations.AddField(
            model_name='localization',
            name='image_file_name',
            field=models.CharField(default='a', max_length=32),
            preserve_default=False,
        ),
    ]