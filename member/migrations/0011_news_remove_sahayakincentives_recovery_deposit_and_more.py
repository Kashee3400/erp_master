# Generated by Django 4.2 on 2024-11-19 12:02

from django.db import migrations, models
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0010_sahayakfeedback_files_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Enter the title of the news article.', max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(help_text='Unique identifier for the news article (auto-generated from the title).', max_length=255, unique=True, verbose_name='Slug')),
                ('summary', models.TextField(help_text='Enter a brief summary or introduction to the news article.', verbose_name='Summary')),
                ('content', django_ckeditor_5.fields.CKEditor5Field(help_text='Enter the full content of the news article using a rich text editor.', verbose_name='Content')),
                ('author', models.CharField(help_text='Name of the author of the article.', max_length=100, verbose_name='Author')),
                ('published_date', models.DateTimeField(auto_now_add=True, help_text='The date and time when the article was published.', verbose_name='Published Date')),
                ('updated_date', models.DateTimeField(auto_now=True, help_text='The date and time when the article was last updated.', verbose_name='Updated Date')),
                ('image', models.ImageField(blank=True, help_text='Upload an optional image for the news article.', null=True, upload_to='news/images/', verbose_name='Image')),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags for categorizing the article.', max_length=255, verbose_name='Tags')),
                ('is_published', models.BooleanField(default=False, help_text='Check this box to publish the article.', verbose_name='Is Published')),
            ],
            options={
                'verbose_name': 'News',
                'verbose_name_plural': 'News',
                'ordering': ['-published_date'],
            },
        ),
        migrations.RemoveField(
            model_name='sahayakincentives',
            name='recovery_deposit',
        ),
        migrations.AddField(
            model_name='sahayakincentives',
            name='milk_incentive_payable',
            field=models.FloatField(default=0.0, verbose_name='Milk Incentive Payable'),
        ),
        migrations.AlterField(
            model_name='sahayakincentives',
            name='milk_incentive',
            field=models.FloatField(default=0.0, verbose_name='Milk Incentive After TDS'),
        ),
        migrations.AlterField(
            model_name='sahayakincentives',
            name='sahayak_recovery',
            field=models.FloatField(default=0.0, verbose_name='Recovery Amount'),
        ),
    ]