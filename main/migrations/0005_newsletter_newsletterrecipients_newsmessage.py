# Generated by Django 3.2.11 on 2022-01-21 07:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20220120_0951'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterRecipients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_address', models.EmailField(max_length=254)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='NewsMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news_title', models.CharField(max_length=100)),
                ('news_message', models.TextField()),
                ('news_file', models.CharField(max_length=255)),
                ('news_time', models.DateTimeField(auto_now_add=True)),
                ('news_state', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('user_group', models.IntegerField(default=0)),
                ('plain_text', models.TextField()),
                ('news_file', models.CharField(max_length=255)),
                ('scheduled_time', models.DateTimeField()),
                ('state', models.IntegerField(default=0)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('responsible', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]