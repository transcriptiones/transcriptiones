# Generated by Django 3.2.4 on 2021-07-15 16:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_alter_usermessage_viewing_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermessage',
            name='sending_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]