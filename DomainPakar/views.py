from django.shortcuts import render, redirect
from DomainPakar.models import Gejala, Pasien, CFPakar, Penyakit, GejalaPasien, HasilDiagnosa
from django.contrib.auth import login, authenticate, logout
from datetime import datetime
import random, string
import sweetify
import json


def dumpData(request):
    listGejala = []
    listPenyakit = []

    Gejalas = Gejala.objects.all()
    Penyakits = Penyakit.objects.all()

    for gejala in Gejalas:
        listGejala.append({
            'ID': gejala.IDGejala,
            'NamaGejala': gejala.NamaGejala,
            'Pertanyaan': gejala.Pertanyaan,
            'Penjelasan': gejala.SubPenjelasan
        })

    for penyakit in Penyakits:
        listPenyakit.append({
            'ID': penyakit.IDPenyakit,
            'NamaPenyakit': penyakit.NamaPenyakit,
            'Definisi': penyakit.Definisi,
            'Solusi': penyakit.Solusi,
            'Pencegahan': penyakit.Pencegahan
        })

    # the json file where the output must be stored
    out_file = open("gejala.json", "w")

    json.dump({'gejalas': listGejala}, out_file, indent=6)

    out_file.close()

    out_file = open("penyakit.json", "w")

    json.dump({'penyakit': listPenyakit}, out_file, indent=6)

    out_file.close()

    return redirect('/')


def restore(request):
    # Opening JSON file
    f = open('gejala.json')

    # returns JSON object as
    # a dictionary
    data = json.load(f)
    data = data['gejalas']
    for i in data:
        Gejala.objects.create(
            IDGejala=i['ID'],
            NamaGejala=i['NamaGejala'],
            Pertanyaan=i['Pertanyaan'],
            SubPenjelasan=i['Penjelasan']
        )
        print('GEJALA DIBUAT BERHASIL')

    f.close()
    f = open('penyakit.json')

    # returns JSON object as
    # a dictionary
    data = json.load(f)
    data = data['penyakit']
    for i in data:
        Penyakit.objects.create(
            IDPenyakit=i['ID'],
            NamaPenyakit=i['NamaPenyakit'],
            Definisi=i['Definisi'],
            Solusi=i['Solusi'],
            Pencegahan=i['Pencegahan']
        )
        print('PENYAKIT DIBUAT BERHASIL')
    f.close()

    return redirect('/')


# Create your views here.
def indexView(request):
    if request.user.username == 'admin':
        return redirect('/dashboard')

    userLogin = request.user.is_authenticated and request.user.is_superuser
    contexts = {
        'login': userLogin,
    }
    return render(request=request, context=contexts, template_name='index.html')


def indexAdmin(request):
    userLogin = request.user.is_authenticated and request.user.is_superuser

    class Rules:
        def __init__(self, rule: str, kaidah: str):
            self.Rule = rule,
            self.Kaidah = kaidah

    penyakits = Penyakit.objects.all()
    rules = []
    for idx, penyakit in enumerate(penyakits):
        dump = 'IF'
        for gejala in penyakit.GejalaPenyakit.all():
            dump += ' ' + gejala.IDGejala
        dump += f' THEN {penyakit.IDPenyakit}'
        obj = Rules(rule=f'R{idx+1}', kaidah=dump)
        obj.Rule = obj.Rule[0]
        rules.append(obj)

    contexts = {
        'totalPenyakit':len(penyakits),
        'totalGejala': len(Gejala.objects.all()),
        'totalCFPakar': len(CFPakar.objects.all()),
        'totalRekamMedis': len(Pasien.objects.all()),
        'login': userLogin,
        'rules': rules
    }
    return render(request=request, context=contexts, template_name='admin.html')

def rekamMedis(request):
    userLogin = request.user.is_authenticated and request.user.is_superuser
    pasiens = Pasien.objects.all()
    IdPasien = request.GET.get('IDPasien')
    namaPasien = request.GET.get('namaPasien')

    if IdPasien is not None:
        if IdPasien != '':
            pasiens = Pasien.objects.filter(IDPasien=IdPasien)

    if namaPasien is not None:
        if namaPasien != '':
            pasiens = Pasien.objects.filter(NamaLengkap__contains=namaPasien)

    if len(pasiens) == 0 and (IdPasien != None or namaPasien != None):
        sweetify.error(request, 'Pasien Tidak Ditemukan')

    contexts = {
        'login': userLogin,
        'pasiens': pasiens
    }
    return render(request=request, context=contexts, template_name='data-pasien.html')

def detailPasienView(request):
    IDPasien = request.GET.get('IDPasien')
    userLogin = request.user.is_authenticated and request.user.is_superuser

    if IDPasien is not None:
        pasienObj = Pasien.objects.get(IDPasien=IDPasien)
        listTerbesar = list(pasienObj.Diagnosis.all().order_by('-Persentase').values_list('IDPenyakit'))

        class hasilDiagnosaObj:
            def __init__(self, penyakit: str, persen: float, definisi: str = '', solusi: str = '', pecegahan: str = ''):
                self.namaPenyakit = penyakit
                self.Persentase = round(persen, 2)
                self.Definisi = definisi,
                self.Solusi = solusi,
                self.Pencegahan = pecegahan

        gejalas = []
        obj = Penyakit.objects.get(IDPenyakit=listTerbesar[0][0])
        gejalas.append(
            hasilDiagnosaObj(
                penyakit=obj.NamaPenyakit,
                persen=HasilDiagnosa.objects.get(IDPenyakit=listTerbesar[0][0], IDPasien=IDPasien).Persentase,
                definisi=str(obj.Definisi),
                solusi=str(obj.Solusi),
                pecegahan=str(obj.Pencegahan)
            )
        )

        gejalas[0].Definisi = gejalas[0].Definisi[0]
        gejalas[0].Solusi = gejalas[0].Solusi[0]

        for i in listTerbesar[1:]:
            gejalas.append(
                hasilDiagnosaObj(
                    penyakit=Penyakit.objects.get(IDPenyakit=i[0]).NamaPenyakit,
                    persen=HasilDiagnosa.objects.get(IDPenyakit=i[0], IDPasien=IDPasien).Persentase
                )
            )

        contexts = {
            'pasien': pasienObj,
            'GejalaTerbesar': gejalas[0],
            'GejalaLain': gejalas[1:],
            'login': userLogin,
        }
        response = render(request=request, context=contexts, template_name='details-pasien.html')
        return response


def tambahDataPOST(request):
    if request.method == 'POST':
        tambahPenyakit = request.POST.get('TambahPenyakit')
        tambahGejala = request.POST.get('TambahGejala')
        if tambahPenyakit is not None:
            ID = request.POST.get('ID')
            nama = request.POST.get('nama')
            definisi = request.POST.get('definisi')
            solusi = request.POST.get('solusi')
            pencegahan = request.POST.get('pencegahan')

            obj = Penyakit.objects.create(
                IDPenyakit=ID,
                NamaPenyakit=nama,
                Definisi=definisi,
                Solusi=solusi,
                Pencegahan=pencegahan
            )

            # Gejala
            gejalaForms = []
            for i in range(1, 38):
                temp = request.POST.get(f'Gejala{i}')
                if temp is not None:
                    GejalaObj = Gejala.objects.get(IDGejala=temp)
                    obj.GejalaPenyakit.add(GejalaObj)
                else:
                    continue
            obj.save()

            sweetify.success(request, 'Tambah Data Penyakit Berhasil')
            return redirect('/penyakit')

        if tambahGejala is not None:
            ID = request.POST.get('ID')
            nama = request.POST.get('nama')
            pertanyaan = request.POST.get('pertanyaan')
            penjelasan = request.POST.get('penjelasan')
            obj = Gejala.objects.create(
                IDGejala=ID,
                NamaGejala=nama,
                Pertanyaan=pertanyaan,
                SubPenjelasan=penjelasan
            )

            sweetify.success(request, 'Tambah Data Gejala Berhasil')
            return redirect('/gejala')


def penyakitView(request):
    if request.method == 'POST':
        if request.POST.get('tambahGejalaKePenyakit') is not None:
            GejalaTambahID = request.POST.get('GejalaTambah')
            IDPenyakit = request.POST.get('IDPenyakit')
            penyakitObj = Penyakit.objects.get(IDPenyakit=IDPenyakit)
            gejalaObj = Gejala.objects.get(IDGejala=GejalaTambahID)
            penyakitObj.GejalaPenyakit.add(gejalaObj)
            penyakitObj.save()

            sweetify.success(request,
                             f'Tambah Gejala {gejalaObj.NamaGejala} ke Penyakit {penyakitObj.NamaPenyakit} Berhasil')
            return redirect('/penyakit')

        if request.POST.get('hapusGejalaDariPenyakit') is not None:
            print(request.POST)
            GejalaID = request.POST.get('GejalaID')
            IDPenyakit = request.POST.get('IDPenyakit')
            penyakitObj = Penyakit.objects.get(IDPenyakit=IDPenyakit)
            gejalaObj = Gejala.objects.get(IDGejala=GejalaID)
            penyakitObj.GejalaPenyakit.remove(gejalaObj)
            print(penyakitObj.GejalaPenyakit.all())
            penyakitObj.save()

            sweetify.success(request,
                             f'Hapus Gejala {gejalaObj.NamaGejala} dari Penyakit {penyakitObj.NamaPenyakit} Berhasil')
            return redirect('/penyakit')

        ID = request.POST.get('ID')
        nama = request.POST.get('nama')
        definisi = request.POST.get('definisi')
        solusi = request.POST.get('solusi')
        pencegahan = request.POST.get('pencegahan')

        obj = Penyakit.objects.get(IDPenyakit=ID)
        obj.NamaPenyakit = nama
        obj.Definisi = definisi
        obj.Solusi = solusi
        obj.Pencegahan = pencegahan
        obj.save()

        sweetify.success(request, f'Perubahan data penyakit berhasil')
        return redirect('/penyakit')

    userLogin = request.user.is_authenticated and request.user.is_superuser
    penyakitObj = Penyakit.objects.all()
    gejalaObj = Gejala.objects.all()
    contexts = {
        'login': userLogin,
        'penyakits': penyakitObj,
        'gejalas': gejalaObj
    }
    return render(request=request, context=contexts, template_name='penyakit.html')


def gejalaView(request):
    userLogin = request.user.is_authenticated and request.user.is_superuser

    hapusGejalaID = request.GET.get('IDGejalaHapus')
    if hapusGejalaID is not None:
        gejalaObj = Gejala.objects.get(IDGejala=hapusGejalaID)
        gejalaObj.delete()
        sweetify.success(request, 'Hapus Data Gejala Berhasil')
        return redirect('/gejala')

    if request.method == 'POST':
        ID = request.POST.get('ID')
        nama = request.POST.get('nama')
        pertanyaan = request.POST.get('pertanyaan')
        penjelasan = request.POST.get('penjelasan')

        sv = Gejala.objects.get(IDGejala=ID)
        sv.NamaGejala = nama
        sv.Pertanyaan = pertanyaan
        sv.SubPenjelasan = penjelasan
        sv.save()
        sweetify.success(request, 'Perubahan Data Berhasil Disimpan')
        return redirect('/gejala')

    gejalatObj = Gejala.objects.all()
    contexts = {
        'login': userLogin,
        'gejalas': gejalatObj
    }
    return render(request=request, context=contexts, template_name='gejala.html')


def loginView(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            sweetify.error(request, 'Salah username atau password')

    contexts = {}
    return render(request=request, context=contexts, template_name='login.html')


def detailsPenyakitView(request):
    userLogin = request.user.is_authenticated and request.user.is_superuser
    if request.method == 'GET':
        IDPenyakit = request.GET['IdPenyakit']
        if IDPenyakit is not None:
            penyakitObj = Penyakit.objects.get(pk=IDPenyakit)
        else:
            return redirect('/penyakit')
        contexts = {
            'login': userLogin,
            'PenyakitObj': penyakitObj,
            'Gejalas': penyakitObj.GejalaPenyakit.all()
        }
        return render(request=request, context=contexts, template_name='details.html')


def logoutView(request):
    logout(request)
    return redirect('/')


def diagnosisView(request):
    print(request.COOKIES)
    if request.user.username == 'admin':
        return redirect('/dashboard')
    userLogin = request.user.is_authenticated and request.user.is_superuser
    already = False
    name = None

    if request.COOKIES.get('IDPasien') is not None:
        already = True
        if Pasien.objects.filter(IDPasien=request.COOKIES.get('IDPasien')).exists():
            name = Pasien.objects.get(IDPasien=request.COOKIES.get('IDPasien')).NamaLengkap
        else:
            # Delete All Cookies
            for cookie in request.COOKIES:
                contexts = {
                    'already': False,
                    'name': name,
                    'login': userLogin,
                }
                response = render(request=request, context=contexts, template_name='diagnosis.html')
                response.delete_cookie(cookie)
                return response

    contexts = {
        'already': already,
        'name': name,
        'login': userLogin,
    }
    return render(request=request, context=contexts, template_name='diagnosis.html')


def pertanyaanView(request):
    print(request.COOKIES)
    if request.user.username == 'admin':
        return redirect('/dashboard')

    userLogin = request.user.is_authenticated and request.user.is_superuser
    if request.method == 'POST':
        isibiodata = request.POST.get('BiodataPasien')
        if isibiodata is not None:
            IDPasien = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            namalengkap = request.POST.get('namalengkap')
            tgllahir = request.POST.get('tgllahir')
            jeniskelamin = request.POST.get('jeniskelamin')
            alamat = request.POST.get('alamat')
            nomortelp = request.POST.get('nomortelp')

            Pasien.objects.create(
                IDPasien=IDPasien,
                NamaLengkap=namalengkap,
                TanggalLahir=datetime.strptime(tgllahir, '%Y-%m-%d'),
                JenisKelamin=jeniskelamin,
                Alamat=alamat,
                NomorTelp=nomortelp
            )
            contexts = {
                'gejalas': Gejala.objects.all(),
                'gejalaspasien': GejalaPasien.objects.filter(KeyPasien__IDPasien=IDPasien),
                'listGejalaPasien': list(
                    GejalaPasien.objects.filter(KeyPasien__IDPasien=request.COOKIES.get('IDPasien')).values_list(
                        'KeyGejala__NamaGejala', flat=True)),
                'login': userLogin,
            }
            response = render(request=request, context=contexts, template_name='pertanyaan.html')
            response.set_cookie('IDPasien', IDPasien)
            return response
    else:
        if request.COOKIES.get('IDPasien') is None:
            sweetify.warning(request, 'Maaf Anda belum melakukan pendaftaran Pasien, silakan mendaftar')
            return redirect('/konsultasi')

        if request.GET.get('NamaGejala') is not None:
            gejalas = Gejala.objects.filter(NamaGejala__contains=request.GET.get('NamaGejala'))
        else:
            gejalas = Gejala.objects.all()

        contexts = {
            'gejalas': gejalas,
            'gejalaspasien': GejalaPasien.objects.filter(KeyPasien__IDPasien=request.COOKIES.get('IDPasien')),
            'listGejalaPasien': list(
                GejalaPasien.objects.filter(KeyPasien__IDPasien=request.COOKIES.get('IDPasien')).values_list(
                    'KeyGejala__NamaGejala', flat=True)),
            'login': userLogin,
        }
        response = render(request=request, context=contexts, template_name='pertanyaan.html')
        return response
        # return redirect('/')


def pilihGejalaPasien(request):
    if request.method == 'POST':

        if request.POST.get('Delete') is not None:
            GejalaPasien.objects.get(
                KeyGejala__IDGejala=request.POST.get('IDGejala'),
                KeyPasien__IDPasien=request.COOKIES.get('IDPasien')
            ).delete()
            sweetify.success(request, 'Gejala berhasil dihapus')
            return redirect('/pertanyaan')

        PasienObj = Pasien.objects.get(IDPasien=request.COOKIES.get('IDPasien'))
        GejalaObj = Gejala.objects.get(IDGejala=request.POST.get('GejalaID'))
        tingkatCF = request.POST.get('tingkat')

        GejalaPasien.objects.create(
            KeyPasien=PasienObj,
            KeyGejala=GejalaObj,
            CFPasien=float(tingkatCF) / 100.0
        )
        sweetify.success(request, 'Gejala Berhasil Dipilih')
        return redirect('/pertanyaan')
    else:
        return redirect('/')


def kumpulkanGejala(request):
    idPasien = request.COOKIES.get('IDPasien')
    gejalaPasienObj = GejalaPasien.objects.filter(KeyPasien__IDPasien=idPasien)
    if len(gejalaPasienObj) == 0:
        sweetify.error('Anda belum memilih gejala apapun, silakan pilih')
        return redirect('/pertanyaan')
    pasienObj = Pasien.objects.get(IDPasien=idPasien)
    for gejala in gejalaPasienObj:
        pasienObj.GejalaPasien.add(gejala.KeyGejala)
        pasienObj.save()
    return redirect('/inference')


def inferenceEngine(request):
    def cfcombine(cf1: float, cf2: float) -> float:
        return cf1 + (cf2 * (1 - cf1))

    idPasien = request.COOKIES.get('IDPasien')
    rules = {}
    checkGejalainRules = {}
    penyakitAllObj = Penyakit.objects.all()

    for rule in penyakitAllObj:
        rules[f'{rule.IDPenyakit}'] = list(rule.GejalaPenyakit.all().values_list('IDGejala', flat=True))
        checkGejalainRules[f'{rule.IDPenyakit}'] = []

    print("\nRULES:")
    print(rules)

    gejalaPasienObj = GejalaPasien.objects.filter(KeyPasien__IDPasien=idPasien)

    for gejalaPasien in gejalaPasienObj:
        for R in checkGejalainRules.keys():
            if gejalaPasien.KeyGejala.IDGejala in rules[R]:
                checkGejalainRules[R].append(gejalaPasien.KeyGejala.IDGejala)

    print('\nRULES YANG AKTIF BERDASARKAN GEJALA YANG DIPILIH USER')
    print(checkGejalainRules, '\n')

    CFHitung = {}

    for R in checkGejalainRules.keys():
        if len(checkGejalainRules[R]) > 2:
            kaliCF = []
            for gpasien in checkGejalainRules[R]:
                kaliCF.append(
                    GejalaPasien.objects.get(KeyPasien__IDPasien=idPasien, KeyGejala__IDGejala=gpasien).CFPasien \
                    * CFPakar.objects.get(RelasiGejala__IDGejala=gpasien, RelasiPenyakit__IDPenyakit=R).CF
                )

            cfOld = cfcombine(cf1=kaliCF[0], cf2=kaliCF[1])
            for cf2 in kaliCF[2:]:
                cfOld = cfcombine(cf1=cfOld, cf2=cf2)

            CFHitung[R] = cfOld

        elif len(checkGejalainRules[R]) == 2:
            kaliCF = []
            for gpasien in checkGejalainRules[R]:
                kaliCF.append(
                    GejalaPasien.objects.get(KeyPasien__IDPasien=idPasien, KeyGejala__IDGejala=gpasien).CFPasien \
                    * CFPakar.objects.get(RelasiGejala__IDGejala=gpasien, RelasiPenyakit__IDPenyakit=R).CF
                )

            cfOld = cfcombine(cf1=kaliCF[0], cf2=kaliCF[1])
            CFHitung[R] = cfOld
        elif len(checkGejalainRules[R]) == 1:
            gpasien = checkGejalainRules[R][0]
            CFHitung[R] = GejalaPasien.objects.get(KeyPasien__IDPasien=idPasien, KeyGejala__IDGejala=gpasien).CFPasien \
                          * CFPakar.objects.get(RelasiGejala__IDGejala=gpasien, RelasiPenyakit__IDPenyakit=R).CF
        else:
            CFHitung[R] = 0.0

    # Konversi dalam bentuk persen
    for k in CFHitung.keys():
        CFHitung[k] = CFHitung.get(k) * 100

    print("Perhitungan CF Akhir")
    print(CFHitung, '\n')

    response = redirect('/hasil-diagnosa')
    response.set_cookie('CFDiagnosis', CFHitung)
    return response


def hasilDiagnosa(request):
    idPasien = request.COOKIES.get('IDPasien')
    CFAkhir = eval(request.COOKIES.get('CFDiagnosis'))
    pasienObj = Pasien.objects.get(IDPasien=idPasien)
    for k in CFAkhir.keys():
        if float(CFAkhir[k]) != 0.0:
            hasilObj = HasilDiagnosa.objects.create(
                IDPasien=idPasien,
                IDPenyakit=k,
                Persentase=float(CFAkhir[k])
            )
            pasienObj.Diagnosis.add(hasilObj)
            pasienObj.save()

    now = datetime.now()
    pasienObj.TglDiagnosa = now.date()
    pasienObj.save()

    listTerbesar = list(pasienObj.Diagnosis.all().order_by('-Persentase').values_list('IDPenyakit'))

    class hasilDiagnosaObj:
        def __init__(self, penyakit: str, persen: float, definisi: str = '', solusi: str = '', pecegahan: str = ''):
            self.namaPenyakit = penyakit
            self.Persentase = round(persen, 2)
            self.Definisi = definisi,
            self.Solusi = solusi,
            self.Pencegahan = pecegahan

    gejalas = []
    obj = Penyakit.objects.get(IDPenyakit=listTerbesar[0][0])
    gejalas.append(
        hasilDiagnosaObj(
            penyakit=obj.NamaPenyakit,
            persen=HasilDiagnosa.objects.get(IDPenyakit=listTerbesar[0][0], IDPasien=idPasien).Persentase,
            definisi=str(obj.Definisi),
            solusi=str(obj.Solusi),
            pecegahan=str(obj.Pencegahan)
        )
    )

    gejalas[0].Definisi = gejalas[0].Definisi[0]
    gejalas[0].Solusi = gejalas[0].Solusi[0]

    for i in listTerbesar[1:]:
        gejalas.append(
            hasilDiagnosaObj(
                penyakit=Penyakit.objects.get(IDPenyakit=i[0]).NamaPenyakit,
                persen=HasilDiagnosa.objects.get(IDPenyakit=i[0], IDPasien=idPasien).Persentase
            )
        )

    contexts = {
        'pasien': pasienObj,
        'GejalaTerbesar': gejalas[0],
        'GejalaLain': gejalas[1:],
        'login': False,
    }

    sweetify.success(request, 'Hasil Diagnosa berhasil didapatkan')
    response = render(request=request, context=contexts, template_name='hasil.html')

    # Delete All Cookies
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    return response


def editcf(request):
    if request.method != 'POST':
        return redirect('/certain-factor')

    print(request.POST)
    IDPenyakit = request.POST.get('Penyakit')
    IDGejala = request.POST.get('Gejala')
    MB = float(request.POST.get('MB'))
    MD = float(request.POST.get('MD'))
    CF = MB - MD
    cfobj = CFPakar.objects.get(RelasiPenyakit__IDPenyakit=IDPenyakit, RelasiGejala__IDGejala=IDGejala)
    cfobj.MB = MB
    cfobj.MD = MD
    cfobj.CF = CF
    cfobj.save()

    sweetify.success(request, 'Perubahan nilai CF Berhasil')
    return redirect('/certain-factor')


def rulebase(request):
    hapusCF = request.GET.get('IDCFHapus')
    if hapusCF is not None:
        if CFPakar.objects.filter(pk=hapusCF).exists():
            cfPObj = CFPakar.objects.get(pk=hapusCF)
            cfPObj.delete()
            sweetify.success(request, 'Hapus Nilai CF berhasil')
            return redirect('/certain-factor')

    if request.method == 'POST':
        IDPenyakit = request.POST.get('Penyakit')
        IDGejala = request.POST.get('Gejala')
        MB = float(request.POST.get('MB'))
        MD = float(request.POST.get('MD'))
        CF = MB - MD

        CFPakar.objects.create(
            RelasiPenyakit=Penyakit.objects.get(IDPenyakit=IDPenyakit),
            RelasiGejala=Gejala.objects.get(IDGejala=IDGejala),
            MB=MB,
            MD=MD,
            CF=CF
        )
        sweetify.success(request, 'Tambah Data CF Berhasil')
        return redirect('/certain-factor')

    userLogin = request.user.is_authenticated and request.user.is_superuser
    gejalas = Gejala.objects.all()
    penyakits = Penyakit.objects.all()
    cfpakar = CFPakar.objects.all()
    contexts = {
        'login': userLogin,
        'gejalas': gejalas,
        'penyakits': penyakits,
        'cfpakar': cfpakar
    }
    return render(request=request, context=contexts, template_name='cf.html')
