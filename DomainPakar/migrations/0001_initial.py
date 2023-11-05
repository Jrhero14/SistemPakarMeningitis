# Generated by Django 4.2.7 on 2023-11-05 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gejala',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('IDGejala', models.CharField(blank=True, max_length=4, null=True)),
                ('NamaGejala', models.CharField(blank=True, max_length=100, null=True)),
                ('Pertanyaan', models.CharField(blank=True, max_length=255, null=True)),
                ('SubPenjelasan', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HasilDiagnosa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('IDPasien', models.CharField(blank=True, max_length=5, null=True)),
                ('IDPenyakit', models.CharField(blank=True, max_length=4, null=True)),
                ('Persentase', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Penyakit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('IDPenyakit', models.CharField(blank=True, max_length=4, null=True)),
                ('NamaPenyakit', models.CharField(blank=True, max_length=100, null=True)),
                ('Definisi', models.TextField(blank=True, null=True)),
                ('Solusi', models.TextField(blank=True, null=True)),
                ('Pencegahan', models.TextField(blank=True, null=True)),
                ('GejalaPenyakit', models.ManyToManyField(blank=True, to='DomainPakar.gejala')),
            ],
        ),
        migrations.CreateModel(
            name='Pasien',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('IDPasien', models.CharField(blank=True, max_length=5, null=True)),
                ('NamaLengkap', models.CharField(max_length=255)),
                ('TanggalLahir', models.DateField()),
                ('Alamat', models.CharField(max_length=255)),
                ('NomorTelp', models.CharField(max_length=15)),
                ('JenisKelamin', models.CharField(choices=[('Laki-Laki', 'Laki-Laki'), ('Perempuan', 'Perempuan')], default='Laki-Laki', max_length=15)),
                ('TglDiagnosa', models.DateField(blank=True, null=True)),
                ('Diagnosis', models.ManyToManyField(blank=True, to='DomainPakar.hasildiagnosa')),
                ('GejalaPasien', models.ManyToManyField(blank=True, to='DomainPakar.gejala')),
            ],
        ),
        migrations.CreateModel(
            name='GejalaPasien',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CFPasien', models.FloatField(default=0)),
                ('KeyGejala', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='DomainPakar.gejala')),
                ('KeyPasien', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='DomainPakar.pasien')),
            ],
        ),
        migrations.CreateModel(
            name='CFPakar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('MB', models.FloatField(default=0.0)),
                ('MD', models.FloatField(default=0.0)),
                ('CF', models.FloatField(default=0.0)),
                ('RelasiGejala', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='DomainPakar.gejala')),
                ('RelasiPenyakit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='DomainPakar.penyakit')),
            ],
        ),
    ]