# Generated by Django 4.0.2 on 2022-04-15 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_user_followed_num_remove_user_following_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='follow_state',
            field=models.BooleanField(default=False),
        ),
    ]