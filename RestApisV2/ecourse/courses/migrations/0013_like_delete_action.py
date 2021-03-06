# Generated by Django 4.0.2 on 2022-07-20 03:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_alter_lessonview_lesson'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=False)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.lesson')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'unique_together': {('user', 'lesson')},
            },
        ),
        migrations.DeleteModel(
            name='Action',
        ),
    ]
