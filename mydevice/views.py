from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import FormHeaderPinjam
from django.contrib import messages
from .models import MasterDevice, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout

'''
untuk menu tambahkan ke konteks
1=devices
2=peminjaman
3=pengguna
'''

# Create your views here.
def Dashboard(request):
    context = {
        'menu':'Dashboard'
    }
    return render(request,'base.html',context)

def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        if (user):
            login(request,user)
            messages.add_message(request,messages.SUCCESS,f"Selamat datang {user.userprofile.nama_lengkap}!")
            return HttpResponseRedirect('/')
        else:
            messages.add_message(request,messages.SUCCESS,f"Username atau Password tidak sesuai. Silakan coba kembali.")
            return HttpResponseRedirect('/login/')

    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    else:
        return render(request,'login.html')

def DaftarPengguna(request):
    users = User.objects.all()
    context = {
        'menu':'Daftar Pengguna',
        'id':5,
        'users':users
    }
    return render(request,'views/daftar_pengguna.html',context)

def EditPengguna(request,id):   
    try: 
        if request.method == "POST":
            user = User.objects.get(id=id)
            userprofile = UserProfile.objects.get(user=user)
            userprofile.nama_lengkap=request.POST['nama']
            userprofile.role = request.POST['role']
            userprofile.save()
            messages.add_message(request,messages.SUCCESS,'Update Pengguna Berhasil Dilakukan.')
            return HttpResponseRedirect('/user/list/')
    except:
        messages.add_message(request,messages.SUCCESS,'Update Pengguna Gagal, Silakan Coba Kembali.')
        return HttpResponseRedirect('/user/list/')
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
        return HttpResponseRedirect('/user/list/')
    

def HapusPengguna(request,id):        
    try:
        user = User.objects.get(id=id)
        user.delete()
        messages.add_message(request,messages.SUCCESS,'Hapus Pengguna Berhasil.')
    except Exception as ex:
        print(ex)
        messages.add_message(request,messages.SUCCESS,'Hapus Pengguna Gagal, Silakan Coba Kembali')
    return HttpResponseRedirect('/user/list/')

def TambahPengguna(request):
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

def TambahDevice(request):
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

def DaftarDevice(request):
    device = MasterDevice.objects.all()
    context = {
        'menu':'Daftar Device',
        'id':1,
        'device':device
    }
    return render(request,'views/daftar_device.html',context)

def EditDevice(request,id):    
    if request.method == "POST":
        device = MasterDevice.objects.get(id=id)
        device.nama_device = request.POST['nama_device']
        device.keterangan = request.POST['keterangan']
        device.updated_by = request.user.userprofile.nama_lengkap
        device.save()
        messages.add_message(request,messages.SUCCESS,'Update Device Berhasil Dilakukan.')
        return HttpResponseRedirect('/device/list/')
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
        return HttpResponseRedirect('/device/list/')


def HapusDevice(request,id):        
    try:
        device = MasterDevice.objects.get(id=id)
        device.delete()
        messages.add_message(request,messages.SUCCESS,'Hapus Device Berhasil.')
    except:
        messages.add_message(request,messages.SUCCESS,'Hapus Device Gagal, Device yang sudah pernah dipinjam tidak bisa dihapus.')
    return HttpResponseRedirect('/device/list/')


def TambahCustomer(request):
    context = {
        'menu':'Tambah Customer',
        'id':2
    }
    return render(request,'views/tambah_customer.html',context)

def DaftarCustomer(request):
    context = {
        'menu':'Daftar Customer',
        'id':2
    }
    return render(request,'views/daftar_customer.html',context)

def DaftarPinjam(request):
    context = {
        'menu':'Daftar Pinjaman',
        'id':3        
    }
    return render(request,'views/daftar_pinjam.html',context)


def HeaderPinjam(request):
    context = {
        'menu':'Tambah Pinjam',
        'forms':FormHeaderPinjam(),
        'id':3
    }
    return render(request,'views/header_pinjam.html',context)

def DetailPinjam(request):
    context = {
        'menu':'Detail Pinjam',
        'id':3
    }
    return render(request,'views/detail_pinjam.html',context)

def Logout(request):
    logout(request)
    messages.add_message(request,messages.SUCCESS,"Anda berhasil Keluar.")
    return HttpResponseRedirect('/login/')