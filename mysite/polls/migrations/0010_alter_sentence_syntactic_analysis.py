# Generated by Django 4.2.10 on 2024-02-27 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0009_alter_sentence_syntactic_analysis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentence',
            name='syntactic_analysis',
            field=models.CharField(default='', max_length=200, null=True),
        ),
    ]