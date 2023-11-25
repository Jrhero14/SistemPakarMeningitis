from django.contrib import admin
from DomainPakar.models import Gejala, GejalaPasien, Penyakit, HasilDiagnosa, CFPakar, Pasien
# Register your models here.
admin.site.register(Gejala)
admin.site.register(GejalaPasien)
admin.site.register(Penyakit)
admin.site.register(HasilDiagnosa)
admin.site.register(CFPakar)
admin.site.register(Pasien)
