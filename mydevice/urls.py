from django.contrib import admin
from django.urls import path
from .views import Dashboard, Login, TambahPengguna, TambahDevice, TambahCustomer, HeaderPinjam
from .views import DetailPinjam,DaftarDevice, DaftarCustomer,DaftarPengguna,DaftarPinjam

urlpatterns = [
    path('', Dashboard, name="dashboard"),
    path('login/', Login, name="login"),
    path('user/add/', TambahPengguna, name="tambah_pengguna"),
    path('user/list/', DaftarPengguna, name="daftar_pengguna"),
    path('device/add/', TambahDevice, name="tambah_device"),
    path('device/list/', DaftarDevice, name="daftar_device"),
    path('customer/add/', TambahCustomer, name="tambah_customer"),
    path('customer/list/', DaftarCustomer, name="daftar_customer"),
    path('pinjam/header/', HeaderPinjam, name="header_pinjam"),
    path('pinjam/detail/', DetailPinjam, name="detail_pinjam"),
    path('pinjam/list/', DaftarPinjam, name="daftar_pinjam"),
]
