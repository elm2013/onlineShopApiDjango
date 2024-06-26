# Generated by Django 5.0.6 on 2024-05-28 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='create_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='article',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='store/images'),
        ),
        migrations.AddField(
            model_name='article',
            name='update_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
