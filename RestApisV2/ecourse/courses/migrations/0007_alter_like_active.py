# Generated by Django 4.0.2 on 2022-06-15 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_rating_like'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]