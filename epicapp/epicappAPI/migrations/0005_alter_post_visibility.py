# Generated by Django 4.1.6 on 2023-02-12 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epicappAPI', '0004_alter_post_contenttype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='visibility',
            field=models.CharField(choices=[('PUBLIC', 'Public'), ('PRIVATE', 'Private')], default='PUBLIC', max_length=7),
        ),
    ]
