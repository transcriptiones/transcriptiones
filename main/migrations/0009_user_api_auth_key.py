# Generated by Django 3.2.11 on 2022-01-27 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20220121_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='api_auth_key',
            field=models.CharField(default=None, help_text='Use this key for API requests. Do not share!', max_length=100, null=True, verbose_name='Secret API Key'),
        ),
    ]