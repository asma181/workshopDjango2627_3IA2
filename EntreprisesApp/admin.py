from django.contrib import admin
from .models import entreprise, Utilsateur
from django.contrib.auth.admin import UserAdmin
# Register your models here.
@admin.register(Utilsateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('user_id', 'username', 'email', 'role', 'telephone', 'created_at', 'updated_at')
    list_filter = ('user_id', 'created_at',)
admin.site.register(entreprise)
