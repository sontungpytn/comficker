# Generated by Django 2.0.3 on 2018-03-30 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thing', '0003_auto_20180329_0733'),
    ]

    operations = [
        migrations.AddField(
            model_name='thing',
            name='description',
            field=models.CharField(blank=True, max_length=160),
        ),
    ]
