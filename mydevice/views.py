from django.shortcuts import render, redirect
from .forms import FormHeaderPinjam
from django.contrib import messages
from .models import MasterDevice, UserProfile, MasterCustomer, HeaderPeminjaman, DetailPeminjaman
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
import datetime
from django.db.models import Q, Count

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
        if (user):
            login(request,user)
            messages.add_message(request,messages.SUCCESS,f"Selamat datang {user.userprofile.nama_lengkap}!")
            return redirect('/')
        else:
            messages.add_message(request,messages.SUCCESS,f"Username atau Password tidak sesuai. Silakan coba kembali.")
            return redirect('/login/')

    if request.user.is_authenticated:
        return redirect('/')    
    return render(request,'login.html')

def DaftarPengguna(request):
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super":
            users = User.objects.all()
            context = {
                'menu':'Daftar Pengguna',
                'id':5,
                'users':users
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

def HapusPengguna(request,id):    
    if request.user.is_authenticated:
        if request.user.userprofile.role == "super":    
            try:
                user = User.objects.get(id=id)
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
            'device':device
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
                device.updated_by = request.user.userprofile.nama_lengkap
                device.save()
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
                customer.delete()
                messages.add_message(request,messages.SUCCESS,'Hapus Customer Berhasil.')
            except:
                messages.add_message(request,messages.SUCCESS,'Hapus Customer Gagal, Customer yang sudah pernah dipinjam tidak bisa dihapus.')
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
        context = {
            'menu':'Daftar Customer',
            'id':2,
            'customers':customers
        }
        return render(request,'views/daftar_customer.html',context)
    else:
        messages.add_message(request,messages.SUCCESS,"Silakan Login Terlebih Dahulu.")
        return redirect('/')

def DaftarPinjam(request):
    if request.user.is_authenticated:
        pinjaman = HeaderPeminjaman.objects.all()
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
            messages.add_message(request,messages.SUCCESS,'Device Berhasil Ditambahkan')
            device.is_out=True
            device.last_used=datetime.datetime.now().date()
            device.save()

        pinjaman = HeaderPeminjaman.objects.get(id=id)   
        devices = MasterDevice.objects.all().filter(Q(is_out=False) & Q(is_ok=True))
        tanggal_akhir = pinjaman.tanggal_pinjam + datetime.timedelta(days=365)
        details = DetailPeminjaman.objects.all().filter(peminjaman=pinjaman)
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
                detail = DetailPeminjaman.objects.get(id=id)
                id_pinjam=detail.peminjaman.id
                detail.device.is_out=False
                detail.device.save()
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

def Logout(request):
    logout(request)
    messages.add_message(request,messages.SUCCESS,"Anda berhasil Keluar.")
    return redirect('/login/')