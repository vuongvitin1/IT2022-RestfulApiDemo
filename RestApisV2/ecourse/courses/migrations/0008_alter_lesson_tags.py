# Generated by Django 4.0.2 on 2022-06-15 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_alter_like_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='lessons', to='courses.Tag'),
        ),
    ]
