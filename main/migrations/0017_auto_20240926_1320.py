# Generated by Django 3.2.11 on 2024-09-26 11:20

from django.db import migrations, models
import partial_date.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_alter_user_ui_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='author_name',
            field=models.CharField(help_text='Name of the scribe of the original document.', max_length=150, verbose_name='Name of Scribe'),
        ),
        migrations.AlterField(
            model_name='document',
            name='comments',
            field=models.TextField(blank=True, help_text='Add editorial comments or remarks on the contents of the document', verbose_name='Editorial Comments'),
        ),
        migrations.AlterField(
            model_name='document',
            name='doc_end_date',
            field=partial_date.fields.PartialDateField(blank=True, help_text="If the document was created over a time span, please indicate the end time. <br/>Valid fromats: YYYY ('1792'), MM.YYYY ('01.1980'), DD.MM.YYYY ('23.07.1643')", null=True, verbose_name='Creation Period End'),
        ),
        migrations.AlterField(
            model_name='document',
            name='doc_start_date',
            field=partial_date.fields.PartialDateField(help_text="When was the document written? Be as specific as possible. <br/>Valid fromats: YYYY ('1792'), MM.YYYY ('01.1980'), DD.MM.YYYY ('23.07.1643')", verbose_name='Creation Period Start'),
        ),
        migrations.AlterField(
            model_name='document',
            name='document_utc_add',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Upload Date'),
        ),
        migrations.AlterField(
            model_name='document',
            name='document_utc_update',
            field=models.DateTimeField(auto_now=True, verbose_name='Update Date'),
        ),
        migrations.AlterField(
            model_name='document',
            name='material',
            field=models.IntegerField(blank=True, choices=[(None, '(Unknown)'), (1, 'Paper'), (2, 'Parchment'), (3, 'Papyrus'), (4, 'Metal'), (5, 'Textile'), (6, 'Stone'), (7, 'Wood')], help_text='Which material is the Document written on?', null=True, verbose_name='Writing Material'),
        ),
        migrations.AlterField(
            model_name='document',
            name='pages',
            field=models.PositiveSmallIntegerField(blank=True, help_text='The number of pages of the whole source', null=True, verbose_name='Number of Pages'),
        ),
        migrations.AlterField(
            model_name='document',
            name='publish_user',
            field=models.BooleanField(default=False, help_text='Select this, if you want to publish this document anonymously', verbose_name='Publish Anonymously'),
        ),
        migrations.AlterField(
            model_name='document',
            name='transcription_scope',
            field=models.TextField(help_text='List of the transcribed pages/chapters, etc.', verbose_name='Transcribed Parts of the Document'),
        ),
        migrations.AlterField(
            model_name='document',
            name='version_number',
            field=models.IntegerField(default=1, help_text='Version number', verbose_name='Version Number'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='site_url',
            field=models.URLField(blank=True, help_text='URL of the website', verbose_name='Website'),
        ),
        migrations.AlterField(
            model_name='institution',
            name='zip_code',
            field=models.CharField(help_text='Zip code', max_length=10, verbose_name='Zip Code'),
        ),
        migrations.AlterField(
            model_name='refnumber',
            name='ref_number_name',
            field=models.CharField(help_text='Reference number of the collection containing a document', max_length=100, verbose_name='Reference Number'),
        ),
    ]