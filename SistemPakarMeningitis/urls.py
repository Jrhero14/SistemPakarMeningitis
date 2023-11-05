from django.contrib import admin
from django.urls import path
import DomainPakar.views as PakarViews

urlpatterns = [
    path('restore/', PakarViews.restore),
    path('backup/', PakarViews.dumpData),
    path('admin/', admin.site.urls),
    path('login/', PakarViews.loginView),
    path('logout/', PakarViews.logoutView),
    path('penyakit/', PakarViews.penyakitView),
    path('gejala/', PakarViews.gejalaView),
    path('tambahData/', PakarViews.tambahDataPOST),
    path('details/', PakarViews.detailsPenyakitView),
    path('konsultasi/', PakarViews.diagnosisView),
    path('pertanyaan/', PakarViews.pertanyaanView),
    path('tambah-gejala-pasien/', PakarViews.pilihGejalaPasien),

    path('kumpulkan/', PakarViews.kumpulkanGejala),
    path('inference/', PakarViews.inferenceEngine),
    path('hasil-diagnosa/', PakarViews.hasilDiagnosa),

    path('detail-pasien/', PakarViews.detailPasienView),
    path('certain-factor/', PakarViews.rulebase),
    path('certain-factor-edit/', PakarViews.editcf),
    path('dashboard/', PakarViews.indexAdmin),
    path('rekam-medis/', PakarViews.rekamMedis),
    path('', PakarViews.indexView),
]
