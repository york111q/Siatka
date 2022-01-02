# Generated by Django 3.2.2 on 2022-01-02 18:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Localization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=32)),
                ('image', models.ImageField(upload_to='localizations')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('multisport_number', models.CharField(blank=True, max_length=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('value', models.FloatField()),
                ('done_by_python', models.BooleanField(default=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zapisy.player')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('duration', models.DurationField()),
                ('price', models.FloatField()),
                ('price_multisport', models.FloatField(default=0)),
                ('player_slots', models.IntegerField(default=12)),
                ('coach', models.BooleanField(default=False)),
                ('cancelled', models.BooleanField(default=False)),
                ('location', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zapisy.localization')),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reserve', models.BooleanField(default=False)),
                ('multisport', models.BooleanField(default=False)),
                ('serves', models.IntegerField(default=0)),
                ('paid', models.BooleanField(default=False)),
                ('serves_paid', models.BooleanField(default=False)),
                ('resign', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zapisy.event')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zapisy.player')),
            ],
        ),
    ]
