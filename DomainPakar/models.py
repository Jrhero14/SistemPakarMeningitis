from django.db import models

# Create your models here.
class Gejala(models.Model):
    IDGejala = models.CharField(max_length=4, null=True, blank=True)
    NamaGejala = models.CharField(max_length=100, null=True, blank=True)
    Pertanyaan = models.CharField(max_length=255, null=True, blank=True)
    SubPenjelasan = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.id}. {self.NamaGejala}'

class Penyakit(models.Model):
    IDPenyakit = models.CharField(max_length=4, null=True, blank=True)
    NamaPenyakit = models.CharField(max_length=100, null=True, blank=True)
    Definisi = models.TextField(null=True, blank=True)
    Solusi = models.TextField(null=True, blank=True)
    Pencegahan = models.TextField(null=True, blank=True)

    GejalaPenyakit = models.ManyToManyField(Gejala, blank=True)

    def __str__(self):
        return f'{self.id}. {self.NamaPenyakit}'

class HasilDiagnosa(models.Model):
    IDPasien = models.CharField(max_length=5, null=True, blank=True)
    IDPenyakit = models.CharField(max_length=4, null=True, blank=True)
    Persentase = models.FloatField()

    def __str__(self):
        return f'{self.id}. {self.IDPasien}|{self.IDPenyakit}|{self.Persentase}'


class Pasien(models.Model):
    IDPasien = models.CharField(max_length=5, null=True, blank=True)
    NamaLengkap = models.CharField(max_length=255)
    TanggalLahir = models.DateField()
    Alamat = models.CharField(max_length=255)
    NomorTelp = models.CharField(max_length=15)

    OPTIONS = [
        ('Laki-Laki', 'Laki-Laki'),
        ('Perempuan', 'Perempuan'),
    ]

    JenisKelamin = models.CharField(max_length=15, choices=OPTIONS, default='Laki-Laki')

    GejalaPasien = models.ManyToManyField(Gejala, blank=True)

    Diagnosis = models.ManyToManyField(
        HasilDiagnosa,
        blank=True
    )

    TglDiagnosa = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.id}. {self.NamaLengkap}'


class CFPakar(models.Model):
    RelasiPenyakit = models.ForeignKey(Penyakit, on_delete=models.CASCADE, null=True, blank=True)
    RelasiGejala = models.ForeignKey(Gejala, on_delete=models.CASCADE, null=True, blank=True)
    MB = models.FloatField(default=0.0)
    MD = models.FloatField(default=0.0)
    CF = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.id}. {self.RelasiPenyakit} | {self.RelasiGejala} = CF {self.CF}'

class GejalaPasien(models.Model):
    KeyPasien = models.ForeignKey(Pasien,on_delete=models.SET_NULL, null=True, blank=True)
    KeyGejala = models.ForeignKey(Gejala,on_delete=models.SET_NULL, null=True, blank=True)

    CFPasien = models.FloatField(default=0)

    def __str__(self):
        return f'{self.KeyPasien.IDPasien}.{self.KeyGejala.NamaGejala} | {self.KeyGejala} = CF {self.CFPasien}'