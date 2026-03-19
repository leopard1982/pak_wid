from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
ROLE = [
    ('super','super'),
    ('admin','admin'),
    ('viewer','viewer')
]

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    nama_lengkap = models.CharField(max_length=200,blank=True,null=True)
    role = models.CharField(max_length=10,choices=ROLE,default="viewer")
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + f" [{self.nama_lengkap}]"

class MasterDevice(models.Model):    
    id_device = models.CharField(max_length=100,blank=True,null=True)
    nama_device = models.CharField(max_length=100,blank=True,null=True)
    keterangan = models.CharField(max_length=200,blank=True,null=True)
    is_out = models.BooleanField(default=False)
    is_ok = models.BooleanField(default=True)
    tanggal_buat = models.DateField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=200,blank=True,null=True)
    created_by = models.CharField(max_length=200,blank=True,null=True)
    last_used = models.DateField(blank=True,null=True)

    def __str__(self):
        return self.nama_device
    
    class Meta:
        unique_together = ['id_device']

class MasterCustomer(models.Model):
    nama = models.CharField(max_length=100)
    alamat = models.CharField(max_length=100)
    telpon = models.CharField(max_length=20)
    kontak_person = models.CharField(max_length=200)
    catatan = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=150)

    def __str__(self):
        return self.nama
    
    class Meta:
        unique_together = ['slug']

class HeaderPeminjaman(models.Model):
    id = models.UUIDField(auto_created=True,editable=False,default=uuid.uuid4,primary_key=True)
    tanggal_pinjam = models.DateField(blank=True)
    customer = models.ForeignKey(MasterCustomer,on_delete=models.RESTRICT,blank=True,null=True)
    keterangan = models.CharField(max_length=200,blank=True,null=True)
    penerima_customer = models.CharField(max_length=200,blank=True,null=True)
    is_closed = models.BooleanField(default=False)
    is_process = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=200,blank=True,null=True)
    created_by = models.CharField(max_length=200,blank=True,null=True)

    def __str__(self):
        return f"{self.customer} | {self.tanggal_pinjam} | {self.is_closed} | {self.keterangan}"

class DetailPeminjaman(models.Model):    
    peminjaman = models.ForeignKey(HeaderPeminjaman,on_delete=models.RESTRICT,blank=True,null=True,related_name="Detail_Peminjam")
    device = models.ForeignKey(MasterDevice,on_delete=models.RESTRICT,blank=True,null=True,related_name="Detail_Device")
    tanggal_akhir = models.DateField(blank=True,null=True)
    lokasi = models.CharField(blank=True,null=True,max_length=100)
    lokasi_koordinat = models.CharField(blank=True,null=True,max_length=100)
    tanggal_dikembalikan = models.DateField(blank=True,null=True)
    keterangan = models.CharField(max_length=200)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return f"{self.peminjaman.customer} | {self.penerima_customer} | {self.device.nama_device} | {self.tanggal_akhir} | {self.tanggal_dikembalikan} "


class LogLogin(models.Model):
    tanggal = models.DateTimeField(auto_now_add=True)
    pengguna = models.CharField(max_length=100,null=True,blank=True)
    keterangan = models.CharField(max_length=100,null=True,blank=True)