from django.shortcuts import render
from .forms import FormHeaderPinjam

# Create your views here.
def Dashboard(request):
    context = {
        'menu':'Dasbhoard'
    }
    return render(request,'base.html',context)

def Login(request):

    return render(request,'login.html')

def DaftarPengguna(request):
    context = {
        'menu':'Daftar Pengguna'
    }
    return render(request,'views/daftar_pengguna.html',context)

def TambahPengguna(request):
    context = {
        'menu':'Tambah Pengguna'
    }
    return render(request,'views/tambah_pengguna.html',context)

def TambahDevice(request):
    context = {
        'menu':'Tambah Device'
    }
    return render(request,'views/tambah_device.html',context)

def DaftarDevice(request):
    context = {
        'menu':'Daftar Device'
    }
    return render(request,'views/daftar_device.html',context)


def TambahCustomer(request):
    context = {
        'menu':'Tambah Customer'
    }
    return render(request,'views/tambah_customer.html',context)

def DaftarCustomer(request):
    context = {
        'menu':'Daftar Customer'
    }
    return render(request,'views/daftar_customer.html',context)

def DaftarPinjam(request):
    context = {
        'menu':'Daftar Pinjaman',        
    }
    return render(request,'views/daftar_pinjam.html',context)


def HeaderPinjam(request):
    context = {
        'menu':'Tambah Pinjam',
        'forms':FormHeaderPinjam()
    }
    return render(request,'views/header_pinjam.html',context)

def DetailPinjam(request):
    context = {
        'menu':'Detail Pinjam'        
    }
    return render(request,'views/detail_pinjam.html',context)