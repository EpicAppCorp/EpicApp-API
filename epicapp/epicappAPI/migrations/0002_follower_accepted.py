# Generated by Django 4.1.6 on 2023-03-28 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epicappAPI', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='follower',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
    ]
