
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import entreprise, Utilsateur


class UtilsateurCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Utilsateur
        fields = ("username", "email", "role", "telephone")


@admin.register(Utilsateur)
class UtilsateurAdmin(UserAdmin):
    add_form = UtilsateurCreationForm

    list_display = (
        "user_id", "username", "email", "role",
        "telephone", "created_at", "updated_at",
    )

    list_filter = ("role", "is_active", "created_at")
    search_fields = ("user_id", "username", "email", "telephone")
    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        ("Informations supplémentaires", {
            "fields": ("role", "telephone", "created_at", "updated_at"),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "email",
                "role",
                "telephone",
                "password1",
                "password2",
            ),
        }),
    )

    readonly_fields = ("user_id", "created_at", "updated_at")


@admin.register(entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = (
        "raison_sociale",
        "matricule_fiscale",
        "type_entreprise",
        "gerant",
        "created_at",
        "updated_at",
    )
    list_filter = ("type_entreprise",)
    search_fields = ("raison_sociale", "matricule_fiscale")
    ordering = ("raison_sociale",)
    list_per_page = 25
    readonly_fields = ("created_at", "updated_at")
