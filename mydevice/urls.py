from django.contrib import admin
from django.urls import path
from .views import Dashboard, Login, TambahPengguna, TambahDevice, TambahCustomer, HeaderPinjam
from .views import DetailPinjam,DaftarDevice, DaftarCustomer,DaftarPengguna,DaftarPinjam
from .views import EditDevice, HapusDevice,Logout, EditPengguna, HapusPengguna, EditCustomer
from .views import HapusCustomer, HapusItemDevice, ProsesPinjaman, HapusDraftPinjaman,Ubahpassword
from .views import DaftarLog, ExportLogExcel, ToggleStatusPengguna
from .views import KembalikanDevice, PerpanjangDevice, GetNotifikasi


urlpatterns = [
    path('', Dashboard, name="dashboard"),
    path('paswd/',Ubahpassword,name="ubah_password"),
    path('login/', Login, name="login"),
    path('user/add/', TambahPengguna, name="tambah_pengguna"),
    path('user/edit/<str:id>/', EditPengguna, name="edit_pengguna"),
    path('user/del/<str:id>/', HapusPengguna, name="hapus_pengguna"),
    path('user/toggle/<str:id>/', ToggleStatusPengguna, name="toggle_status_pengguna"),
    path('user/list/', DaftarPengguna, name="daftar_pengguna"),
    path('device/add/', TambahDevice, name="tambah_device"),
    path('device/edit/<str:id>/', EditDevice, name="edit_device"),
    path('device/del/<str:id>/', HapusDevice, name="hapus_device"),
    path('device/list/', DaftarDevice, name="daftar_device"),
    path('customer/add/', TambahCustomer, name="tambah_customer"),
    path('customer/edit/<str:id>/', EditCustomer, name="edit_customer"),
    path('customer/del/<str:id>/', HapusCustomer, name="hapus_customer"),
    path('customer/list/', DaftarCustomer, name="daftar_customer"),
    path('pinjam/header/', HeaderPinjam, name="header_pinjam"),
    path('pinjam/detail/<str:id>/', DetailPinjam, name="detail_pinjam"),
    path('pinjam/list/', DaftarPinjam, name="daftar_pinjam"),
    path('pinjam/proses/<str:id>/', ProsesPinjaman, name="proses_pinjam"),
    path('pinjam/hapus/<str:id>/', HapusDraftPinjaman, name="hapus_draft_pinjam"),
    path('pinjam/detail/del/<str:id>/',HapusItemDevice,name="hapus_item_device"),
    path('logout/',Logout,name="logout"),
    path('log/list/', DaftarLog, name="daftar_log"),
    path('log/export/', ExportLogExcel, name="export_log"),
    path('pinjam/kembalikan/<str:id>/', KembalikanDevice, name="kembalikan_device"),
    path('pinjam/perpanjang/<str:id>/', PerpanjangDevice, name="perpanjang_device"),
    path('notifikasi/', GetNotifikasi, name="get_notifikasi"),
]
