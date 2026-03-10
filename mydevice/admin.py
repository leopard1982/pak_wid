from django.contrib import admin
from .models import DetailPeminjaman,HeaderPeminjaman,MasterCustomer,MasterDevice,UserProfile

admin.site.register(DetailPeminjaman)
admin.site.register(HeaderPeminjaman)
admin.site.register(MasterCustomer)
admin.site.register(MasterDevice)
admin.site.register(UserProfile)