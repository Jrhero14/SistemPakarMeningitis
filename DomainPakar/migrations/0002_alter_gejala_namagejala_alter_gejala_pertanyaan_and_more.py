# Generated by Django 4.2.7 on 2023-11-14 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DomainPakar', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gejala',
            name='NamaGejala',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gejala',
            name='Pertanyaan',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gejala',
            name='SubPenjelasan',
            field=models.TextField(blank=True, null=True),
        ),
    ]