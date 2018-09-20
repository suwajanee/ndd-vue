from django.contrib import admin
from .models import Principal
from .models import Shipper
from django import forms

# Register your models here.
class ShipperForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea)

class PrincipalAdmin(admin.ModelAdmin):
    list_display = ('name', 'work_type', 'cancel')

class ShipperAdmin(admin.ModelAdmin):
    form = ShipperForm
    list_display = ('principal', 'name', 'address', 'cancel')

admin.site.register(Principal, PrincipalAdmin)
admin.site.register(Shipper, ShipperAdmin)