from django.shortcuts import render, redirect
from .forms import FormHeaderPinjam
from django.contrib import messages
from .models import MasterDevice, UserProfile, MasterCustomer, HeaderPeminjaman, DetailPeminjaman, LogLogin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.core.paginator import Paginator
from django.http import HttpResponse
import datetime
import openpyxl
from django.db.models import Q, Count

def write_log(pengguna, keterangan):
    LogLogin.objects.create(pengguna=pengguna, keterangan=keterangan)

'''
untuk menu tambahkan ke konteks
1=devices
2=peminjaman
3=pengguna
'''

# Create your views here.
def Dashboard(request):    
    if request.user.is_authenticated:
        devices = MasterDevice.objects.all()
        jml_ok = devices.filter(is_ok=True).aggregate(jumlah=Count('id_device'))
        jml_available = devices.filter(Q(is_ok=True) & Q(is_out=False)).aggregate(jumlah=Count('id_device'))
        jml_customer = MasterCustomer.objects.all().aggregate(jumlah=Count('nama'))
        context = {
            'menu':'Dashboard',
            'jml_ok':jml_ok['jumlah'],
            'jml_available':jml_available['jumlah'],
            'jml_customer':jml_customer['jumlah'],
            'device':devices
        }
        return render(request,'base.html',context)
    else:
        return redirect('/login/')
    
def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
            write_log(user.username, f"Login")
            messages.add_message(request,messages.SUCCESS,f"Selamat datang {user.userprofile.nama_lengkap}!")
            return redirect('/')
        else:
            # Cek apakah user ada tapi nonaktif
            try:
                cek_user = User.objects.get(username=username)
                if not cek_user.is_active:
                    messages.add_message(request,messages.SUCCESS,f"Akun Anda dinonaktifkan. Hubungi administrator.")
                else:
                    messages.add_message(request,messages.SUCCESS,f"Username atau Password tidak sesuai. Silakan coba kembali.")
            except User.DoesNotExist:
                messages.add_message(request,messages.SUCCESS,f"Username atau Password tidak sesuai. Silakan coba kembali.")
            return redirect('/login/')

    if request.user.is_authenticated:
        return redirect('/')    
    return render(request,'login.html')

def DaftarPengguna(request):
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super":
            users = User.objects.select_related('userprofile').all()
            context = {
                'menu':'Daftar Pengguna',
                'id':5,
                'users':users,
                'total_pengguna': users.count(),
                'total_aktif': users.filter(is_active=True).count(),
                'total_nonaktif': users.filter(is_active=False).count(),
            }
            return render(request,'views/daftar_pengguna.html',context)
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def EditPengguna(request,id):   
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super":
            try: 
                if request.method == "POST":
                    user = User.objects.get(id=id)
                    userprofile = UserProfile.objects.get(user=user)
                    userprofile.nama_lengkap=request.POST['nama']
                    userprofile.role = request.POST['role']
                    userprofile.save()
                    status_lama = "Aktif" if user.is_active else "Nonaktif"
                    user.is_active = request.POST.get('is_active') == 'true'
                    status_baru = "Aktif" if user.is_active else "Nonaktif"
                    user.save()
                    log_msg = f"Edit Pengguna: {user.username}"
                    if status_lama != status_baru:
                        log_msg += f" | Status: {status_lama} → {status_baru}"
                    write_log(request.user.username, log_msg)
                    messages.add_message(request,messages.SUCCESS,'Update Pengguna Berhasil Dilakukan.')
                    return redirect('/user/list/')
            except:
                messages.add_message(request,messages.SUCCESS,'Update Pengguna Gagal, Silakan Coba Kembali.')
                return redirect('/user/list/')
            try:
                usernya = User.objects.get(id=int(id))
                context = {
                    'menu':'Edit Pengguna',
                    'id':1,
                    'usernya':usernya

                }
                return render(request,'views/edit_pengguna.html',context)
            except Exception as ex:
                print(ex)
                messages.add_message(request,messages.SUCCESS,'Pengguna Tidak Diketemukan, Silakan Coba Kembali.')
                return redirect('/user/list/')
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def ToggleStatusPengguna(request, id):
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super":
            try:
                user = User.objects.get(id=id)
                user.is_active = not user.is_active
                user.save()
                status = "Aktif" if user.is_active else "Nonaktif"
                write_log(request.user.username, f"Toggle Status Pengguna: {user.username} → {status}")
                messages.add_message(request, messages.SUCCESS, f'Status {user.username} berhasil diubah menjadi {status}.')
            except:
                messages.add_message(request, messages.SUCCESS, 'Gagal mengubah status pengguna.')
            return redirect('/user/list/')
        else:
            messages.add_message(request, messages.SUCCESS, "Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        return redirect('/login/')

def HapusPengguna(request,id):    
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super":    
            try:
                user = User.objects.get(id=id)
                write_log(request.user.username, f"Hapus Pengguna: {user.username}")
                user.delete()
                messages.add_message(request,messages.SUCCESS,'Hapus Pengguna Berhasil.')
            except Exception as ex:
                print(ex)
                messages.add_message(request,messages.SUCCESS,'Hapus Pengguna Gagal, Silakan Coba Kembali')
            return redirect('/user/list/')
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def TambahPengguna(request):
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super":
            try:
                if request.method=="POST":
                    user = User()
                    user.username="-".join(str(request.POST['user']).lower().split(' '))
                    user.password = "global12345"
                    user.save()
                    user.set_password('global12345')
                    user.save()
                    userprofile = UserProfile()
                    userprofile.user = user
                    userprofile.nama_lengkap = request.POST['nama']
                    userprofile.role = request.POST['role']
                    userprofile.save()
                    write_log(request.user.username, f"Tambah Pengguna: {user.username} [{userprofile.role}]")
                    messages.add_message(request,messages.SUCCESS,f'Pengguna {user.username} berhasil ditambahkan sebagai {userprofile.role} dengan password sementara global12345')
            except:
                messages.add_message(request,messages.SUCCESS,'Pengguna gagal ditambahkan, silakan coba kembali.')
            context = {
                'menu':'Tambah Pengguna',
                'id':5
            }
            return render(request,'views/tambah_pengguna.html',context)
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def TambahDevice(request):
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super" or request.user.userprofile.role == "admin":
            if request.method == "POST":
                try:
                    device = MasterDevice()
                    device.id_device = str(request.POST['id_device']).lower()
                    device.nama_device = request.POST['nama_device']
                    device.keterangan = request.POST['keterangan']
                    device.created_by = request.user.userprofile.nama_lengkap
                    device.save()
                    write_log(request.user.username, f"Tambah Device: {device.nama_device}")
                    messages.add_message(request,messages.SUCCESS,'Perangkat Berhasil Ditambahkan.')
                except:
                    messages.add_message(request,messages.SUCCESS,'Perangkat Gagal Ditambahkan, Silakan Coba Kembali.')

            context = {
                'menu':'Tambah Device',
                'id':1
            }
            return render(request,'views/tambah_device.html',context)
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def DaftarDevice(request):
    if request.user.is_authenticated:
        device = MasterDevice.objects.all()
        context = {
            'menu':'Daftar Device',
            'id':1,
            'device':device,
            'total_device': device.count(),
            'total_available': device.filter(is_ok=True, is_out=False).count(),
            'total_dipinjam': device.filter(is_out=True).count(),
            'total_rusak': device.filter(is_ok=False).count(),
        }
        return render(request,'views/daftar_device.html',context)
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def EditDevice(request,id):    
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super" or request.user.userprofile.role == "admin":
            if request.method == "POST":
                device = MasterDevice.objects.get(id=id)
                device.nama_device = request.POST['nama_device']
                device.keterangan = request.POST['keterangan']
                kondisi_lama = "OK" if device.is_ok else "Rusak"
                device.is_ok = request.POST.get('is_ok') == 'true'
                kondisi_baru = "OK" if device.is_ok else "Rusak"
                device.updated_by = request.user.userprofile.nama_lengkap
                device.save()
                log_msg = f"Edit Device: {device.nama_device}"
                if kondisi_lama != kondisi_baru:
                    log_msg += f" | Kondisi: {kondisi_lama} → {kondisi_baru}"
                write_log(request.user.username, log_msg)
                messages.add_message(request,messages.SUCCESS,'Update Device Berhasil Dilakukan.')
                return redirect('/device/list/')
            try:
                device = MasterDevice.objects.get(id=id)
                context = {
                    'menu':'Edit Device',
                    'id':1,
                    'device':device       

                }
                return render(request,'views/edit_device.html',context)
            except:
                messages.add_message(request,messages.SUCCESS,'Update Device Gagal, Silakan Coba Kembali.')
                return redirect('/device/list/')
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')


def HapusDevice(request,id):   
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super" or request.user.userprofile.role == "admin":     
            try:
                device = MasterDevice.objects.get(id=id)
                if device.last_used:
                    messages.add_message(request,messages.SUCCESS,'Hapus Device Gagal, Device pernah dipakai.')
                else:
                    write_log(request.user.username, f"Hapus Device: {device.nama_device}")
                    device.delete()
                    messages.add_message(request,messages.SUCCESS,'Hapus Device Berhasil.')
            except:
                messages.add_message(request,messages.SUCCESS,'Hapus Device Gagal, Device yang sudah pernah dipinjam tidak bisa dihapus.')
            return redirect('/device/list/')
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')


def TambahCustomer(request):
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super" or request.user.userprofile.role == "admin":
            if request.method == "POST":
                try:
                    customer = MasterCustomer()
                    customer.nama = request.POST['nama']
                    customer.alamat = request.POST['alamat']
                    customer.kontak_person = request.POST['kontak_person']
                    customer.telpon = request.POST['telpon']
                    customer.slug = "-".join(str(request.POST['nama']).lower().split(' '))                
                    customer.save()
                    write_log(request.user.username, f"Tambah Customer: {customer.nama}")
                    messages.add_message(request,messages.SUCCESS,"Customer berhasil ditambahkan")
                except:
                    messages.add_message(request,messages.SUCCESS,"Customer gagal ditambahkan, apakah nama pt pernah dibuat?")
            context = {
                'menu':'Tambah Customer',
                'id':2
            }
            return render(request,'views/tambah_customer.html',context)
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def EditCustomer(request,id):    
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super" or request.user.userprofile.role == "admin":
            try:
                if request.method == "POST":
                    customer = MasterCustomer.objects.get(id=id)                    
                    customer.alamat = request.POST['alamat']
                    customer.telpon = request.POST['telpon']
                    customer.kontak_person = request.POST['kontak_person']                    
                    customer.save()
                    write_log(request.user.username, f"Edit Customer: {customer.nama}")
                    messages.add_message(request,messages.SUCCESS,'Update Customer Berhasil Dilakukan.')
                    return redirect('/customer/list/')
            except:
                messages.add_message(request,messages.SUCCESS,'Update Customer Gagal, nama PT pernah Ada.')
                    
            try:
                customer = MasterCustomer.objects.get(id=int(id))
                context = {
                    'menu':'Edit Customer',
                    'id':1,
                    'customer':customer

                }
                return render(request,'views/edit_customer.html',context)
            except:
                messages.add_message(request,messages.SUCCESS,'Data Customer tidak ditemukan, Silakan Coba Kembali.')
                return redirect('/device/list/')
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def HapusCustomer(request,id):
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super" or request.user.userprofile.role == "admin":
            try:
                customer = MasterCustomer.objects.get(id=int(id))
                punya_transaksi = HeaderPeminjaman.objects.filter(customer=customer).exists()
                if punya_transaksi:
                    messages.add_message(request,messages.SUCCESS,'Hapus Customer Gagal, customer yang sudah pernah bertransaksi tidak dapat dihapus.')
                else:
                    write_log(request.user.username, f"Hapus Customer: {customer.nama}")
                    customer.delete()
                    messages.add_message(request,messages.SUCCESS,'Hapus Customer Berhasil.')
            except:
                messages.add_message(request,messages.SUCCESS,'Hapus Customer Gagal, silakan coba kembali.')
            return redirect('/customer/list/')
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def DaftarCustomer(request):
    if request.user.is_authenticated:
        customers = MasterCustomer.objects.all()

        # Customer dengan transaksi aktif (is_process=True, is_closed=False)
        id_aktif = HeaderPeminjaman.objects.filter(
            is_process=True, is_closed=False
        ).values_list('customer_id', flat=True).distinct()

        # Customer yang pernah ada transaksi
        id_pernah = HeaderPeminjaman.objects.values_list('customer_id', flat=True).distinct()

        total_customer   = customers.count()
        total_aktif      = customers.filter(id__in=id_aktif).count()
        total_tidak_aktif = customers.exclude(id__in=id_aktif).filter(id__in=id_pernah).count()
        total_belum_transaksi = customers.exclude(id__in=id_pernah).count()

        context = {
            'menu':'Daftar Customer',
            'id':2,
            'customers':customers,
            'total_customer': total_customer,
            'total_aktif': total_aktif,
            'total_tidak_aktif': total_tidak_aktif,
            'total_belum_transaksi': total_belum_transaksi,
        }
        return render(request,'views/daftar_customer.html',context)
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def DaftarPinjam(request):
    if request.user.is_authenticated:
        pinjaman = HeaderPeminjaman.objects.select_related('customer').all()
        context = {
            'menu':'Daftar Pinjaman',
            'id':3,
            'pinjaman':pinjaman
        }
        return render(request,'views/daftar_pinjam.html',context)
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/login/')


def HeaderPinjam(request):    
    if request.user.is_authenticated:
        if request.method=="POST":
            try:
                tanggal_pinjam = datetime.date(year=int(str(request.POST['tanggal_pinjam']).split('-')[0]),month=int(str(request.POST['tanggal_pinjam']).split('-')[1]),day=int(str(request.POST['tanggal_pinjam']).split('-')[2]))
                if tanggal_pinjam > datetime.datetime.now().date():
                    messages.add_message(request,messages.SUCCESS,'Penambahan Peminjaman Gagal, Tanggal tidak boleh lebih dari tanggal hari ini.')
                    return redirect('/pinjam/header/')    
                customer = MasterCustomer.objects.get(id=int(request.POST['customer']))
                penerima = request.POST['penerima_customer']
                keterangan = request.POST['keterangan']

                headerpinjam = HeaderPeminjaman()
                headerpinjam.tanggal_pinjam=tanggal_pinjam
                headerpinjam.customer=customer
                headerpinjam.penerima_customer = penerima
                headerpinjam.keterangan=keterangan
                headerpinjam.created_by=request.user.userprofile.nama_lengkap
                headerpinjam.is_closed=False
                headerpinjam.is_process=False
                headerpinjam.save()
                write_log(request.user.username, f"Tambah Peminjaman: {customer.nama} | {tanggal_pinjam}")
                messages.add_message(request,messages.SUCCESS,'Penambahan transaksi peminjaman berhasil. Silakan tambahkan detail barang.')
                return redirect(f'/pinjam/detail/{headerpinjam.id}/')
            except Exception as ex:
                print(ex)
                messages.add_message(request,messages.SUCCESS,'Penambahan transaksi gagal, silakan coba kembali.')
                return redirect('/pinjam/header/')
            
        context = {
            'menu':'Tambah Pinjam',
            'forms':FormHeaderPinjam(),
            'id':3
        }
        return render(request,'views/header_pinjam.html',context)
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def DetailPinjam(request,id):
    if request.user.is_authenticated:   
        if request.method == "POST" :
            pinjaman = HeaderPeminjaman.objects.get(id=id)   
            device = MasterDevice.objects.get(id=int(request.POST['device']))
            detail = DetailPeminjaman()
            detail.peminjaman = pinjaman
            detail.device = device
            detail.keterangan = request.POST['keterangan']
            detail.lokasi = request.POST['lokasi']
            detail.tanggal_akhir = pinjaman.tanggal_pinjam + datetime.timedelta(days=365)
            detail.save()
            write_log(request.user.username, f"Tambah Device ke Peminjaman: {device.nama_device} | ID {id}")
            messages.add_message(request,messages.SUCCESS,'Device Berhasil Ditambahkan')
            device.is_out=True
            device.last_used=datetime.datetime.now().date()
            device.save()

        pinjaman = HeaderPeminjaman.objects.get(id=id)   
        devices = MasterDevice.objects.all().filter(Q(is_out=False) & Q(is_ok=True))
        tanggal_akhir = pinjaman.tanggal_pinjam + datetime.timedelta(days=365)
        details = DetailPeminjaman.objects.select_related('device').filter(peminjaman=pinjaman)
        context = {
            'menu':'Detail Pinjam',
            'id':3,
            'peminjaman':pinjaman,
            'devices':devices,
            'tgl_akhir':tanggal_akhir,
            'details':details
        }
        return render(request,'views/detail_pinjam.html',context)
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")

def HapusItemDevice(request,id):   
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super" or request.user.userprofile.role == "admin":     
            try:
                detail = DetailPeminjaman.objects.select_related('device', 'peminjaman').get(id=id)
                id_pinjam=detail.peminjaman.id
                detail.device.is_out=False
                detail.device.save()
                write_log(request.user.username, f"Hapus Device dari Peminjaman: {detail.device.nama_device} | ID Pinjam {id_pinjam}")
                detail.delete()
                messages.add_message(request,messages.SUCCESS,'Hapus Device Berhasil.')
                return redirect(f'/pinjam/detail/{id_pinjam}/')    
            except:
                messages.add_message(request,messages.SUCCESS,'Hapus Device Gagal, Silakan coba kembali.')
            return redirect('/pinjam/list/')
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')
    
def ProsesPinjaman(request,id):   
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super" or request.user.userprofile.role == "admin":     
            try:
                pinjaman = HeaderPeminjaman.objects.get(id=id)
                pinjaman.is_process=True
                pinjaman.save()
                write_log(request.user.username, f"Proses Peminjaman: {pinjaman.customer} | {pinjaman.tanggal_pinjam}")
                messages.add_message(request,messages.SUCCESS,'Peminjaman berhasil diproses.')
            except:
                messages.add_message(request,messages.SUCCESS,'Peminjaman gagal diproses, silakan coba kembali...')
            return redirect('/pinjam/list/')
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')
    
def HapusDraftPinjaman(request,id):   
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super" or request.user.userprofile.role == "admin":     
            try:
                pinjaman = HeaderPeminjaman.objects.get(id=id)
                
                if pinjaman.is_process != True:
                    write_log(request.user.username, f"Hapus Draft Peminjaman: {pinjaman.customer} | {pinjaman.tanggal_pinjam}")
                    pinjaman.delete()
                    messages.add_message(request,messages.SUCCESS,'Peminjaman berhasil dihapus.')
                else:
                    messages.add_message(request,messages.SUCCESS,'Peminjaman gagal dihapus.')
            except:
                messages.add_message(request,messages.SUCCESS,'Peminjaman gagal dihapus, silakan coba kembali...')
            return redirect('/pinjam/list/')
        else:
            messages.add_message(request,messages.SUCCESS,"Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')
    
def Ubahpassword(request):
    if request.method=="POST":
        password_lama=request.POST['old_password']
        password_baru1 = request.POST['new_password1']
        password_baru2 = request.POST['new_password2']

        if password_baru1 == password_baru2:
            user = authenticate(username=request.user,password=password_baru1)
            if user:
                user.set_password(password_baru1)
                messages.add_message(request,messages.SUCCESS,'Password Berhasil Diubah Silakan login ulang.')
                logout(request)
                return redirect('/login/')
        messages.add_message(request,messages.SUCCESS,'Password Belum berhasil diubah, silakan coba kembali.')
    return redirect('/')

def DaftarLog(request):
    if request.user.is_authenticated:
        if request.user.userprofile.role in ['super', 'admin']:
            date_from = request.GET.get('date_from', '')
            date_to   = request.GET.get('date_to', '')

            # Card: fixed summary 2 tahun terakhir
            dua_tahun_lalu = datetime.date.today() - datetime.timedelta(days=730)
            logs_card = LogLogin.objects.filter(tanggal__date__gte=dua_tahun_lalu)
            tahun_ini  = datetime.date.today().year
            tahun_lalu = tahun_ini - 1

            card_tahun_ini  = logs_card.filter(tanggal__year=tahun_ini).count()
            card_tahun_lalu = logs_card.filter(tanggal__year=tahun_lalu).count()
            card_total      = logs_card.count()

            # Tabel: pakai filter range
            logs = LogLogin.objects.all().order_by('-tanggal')
            if date_from:
                logs = logs.filter(tanggal__date__gte=date_from)
            if date_to:
                logs = logs.filter(tanggal__date__lte=date_to)

            total_log       = logs.count()

            paginator = Paginator(logs, 25)
            page = request.GET.get('page', 1)
            logs_page = paginator.get_page(page)

            context = {
                'menu': 'Log Transaksi',
                'id': 6,
                'logs': logs_page,
                'total_log': total_log,
                'card_total': card_total,
                'card_tahun_ini': card_tahun_ini,
                'card_tahun_lalu': card_tahun_lalu,
                'tahun_ini': tahun_ini,
                'tahun_lalu': tahun_lalu,
                'date_from': date_from,
                'date_to': date_to,
            }
            return render(request, 'views/daftar_log.html', context)
        else:
            messages.add_message(request, messages.SUCCESS, "Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        messages.add_message(request, messages.SUCCESS, "Silakan Login Terlebih Dahulu.")
        return redirect('/login/')

def ExportLogExcel(request):
    if request.user.is_authenticated:
        if request.user.userprofile.role in ['super', 'admin']:
            date_from = request.GET.get('date_from', '')
            date_to   = request.GET.get('date_to', '')

            logs = LogLogin.objects.all().order_by('-tanggal')
            if date_from:
                logs = logs.filter(tanggal__date__gte=date_from)
            if date_to:
                logs = logs.filter(tanggal__date__lte=date_to)

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Log Transaksi"

            if date_from or date_to:
                label = f"{date_from or 'awal'} s/d {date_to or 'akhir'}"
                ws.append([f'Periode: {label}'])
                ws.append([])

            ws.append(['No', 'Tanggal & Waktu', 'Pengguna', 'Keterangan'])
            for i, log in enumerate(logs, 1):
                ws.append([
                    i,
                    log.tanggal.strftime('%d-%m-%Y %H:%M:%S'),
                    log.pengguna,
                    log.keterangan,
                ])

            ws.column_dimensions['A'].width = 6
            ws.column_dimensions['B'].width = 22
            ws.column_dimensions['C'].width = 20
            ws.column_dimensions['D'].width = 60

            filename = f"log_transaksi_{date_from or 'all'}_{date_to or datetime.date.today()}.xlsx"
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            wb.save(response)
            return response
        else:
            messages.add_message(request, messages.SUCCESS, "Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        return redirect('/login/')

def KembalikanDevice(request, id):
    if request.user.is_authenticated:
        if request.user.userprofile.role in ['super', 'admin']:
            try:
                detail = DetailPeminjaman.objects.select_related('device', 'peminjaman').get(id=id)
                id_pinjam = detail.peminjaman.id
                detail.tanggal_dikembalikan = datetime.date.today()
                detail.save()
                detail.device.is_out = False
                detail.device.save()
                write_log(request.user.username, f"Kembalikan Device: {detail.device.nama_device} | Pinjaman {id_pinjam}")
                # Cek apakah semua device sudah dikembalikan
                semua_kembali = not DetailPeminjaman.objects.filter(
                    peminjaman=detail.peminjaman,
                    tanggal_dikembalikan__isnull=True
                ).exists()
                if semua_kembali:
                    detail.peminjaman.is_closed = True
                    detail.peminjaman.save()
                    write_log(request.user.username, f"Tutup Peminjaman: {detail.peminjaman.customer} | {detail.peminjaman.tanggal_pinjam}")
                messages.add_message(request, messages.SUCCESS, 'Device berhasil dikembalikan.')
            except Exception as ex:
                print(ex)
                messages.add_message(request, messages.SUCCESS, 'Pengembalian device gagal, silakan coba kembali.')
            return redirect(f'/pinjam/detail/{id_pinjam}/')
        else:
            messages.add_message(request, messages.SUCCESS, "Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        return redirect('/login/')

def PerpanjangDevice(request, id):
    if request.user.is_authenticated:
        if request.user.userprofile.role in ['super', 'admin']:
            if request.method == 'POST':
                try:
                    detail = DetailPeminjaman.objects.select_related('device', 'peminjaman').get(id=id)
                    id_pinjam = detail.peminjaman.id
                    tgl_baru_str = request.POST['tanggal_akhir_baru']
                    tgl_baru = datetime.date(
                        year=int(tgl_baru_str.split('-')[0]),
                        month=int(tgl_baru_str.split('-')[1]),
                        day=int(tgl_baru_str.split('-')[2])
                    )
                    detail.tanggal_akhir = tgl_baru
                    detail.save()
                    write_log(request.user.username, f"Perpanjang Device: {detail.device.nama_device} | s/d {tgl_baru}")
                    messages.add_message(request, messages.SUCCESS, f'Perpanjangan device berhasil hingga {tgl_baru.strftime("%d/%m/%Y")}.')
                except Exception as ex:
                    print(ex)
                    messages.add_message(request, messages.SUCCESS, 'Perpanjangan device gagal, silakan coba kembali.')
                return redirect(f'/pinjam/detail/{id_pinjam}/')
        else:
            messages.add_message(request, messages.SUCCESS, "Anda tidak memiliki ijin.")
            return redirect('/')
    else:
        return redirect('/login/')

def GetNotifikasi(request):
    from django.http import JsonResponse
    if request.user.is_authenticated:
        hari_ini = datetime.date.today()
        batas = hari_ini + datetime.timedelta(days=30)
        items = DetailPeminjaman.objects.select_related('device', 'peminjaman__customer').filter(
            tanggal_dikembalikan__isnull=True,
            peminjaman__is_process=True,
            peminjaman__is_closed=False,
            tanggal_akhir__lte=batas
        ).order_by('tanggal_akhir')
        data = []
        for item in items:
            selisih = (item.tanggal_akhir - hari_ini).days
            if selisih < 0:
                status = 'overdue'
            elif selisih <= 7:
                status = 'urgent'
            else:
                status = 'warning'
            data.append({
                'id': item.id,
                'device': item.device.nama_device,
                'customer': str(item.peminjaman.customer),
                'tanggal_akhir': item.tanggal_akhir.strftime('%d/%m/%Y'),
                'selisih': selisih,
                'id_pinjam': str(item.peminjaman.id),
                'status': status,
            })
        return JsonResponse({'count': len(data), 'items': data})
    return JsonResponse({'count': 0, 'items': []})

def Logout(request):
    write_log(request.user.username, f"Logout")
    logout(request)
    messages.add_message(request,messages.SUCCESS,"Anda berhasil Keluar.")
    return redirect('/login/')