
from django.contrib import admin
from django.utils.html import format_html
from .models import Expedition


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "entreprise",
        "poids_kg",
        "statut",
        "created_at",
        "updated_at",
    )

    list_filter = ("statut",)
    search_fields = ("reference", "entreprise__raison_sociale")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25

    readonly_fields = ("reference", "created_at", "updated_at")

    @admin.display(description="Statut")
    def statut_colore(self, obj):
        couleurs = {
            "publiee": "#3498DB",
            "attribuee": "#9B59B6",
            "en_cours": "#F39C12",
            "livree": "#27AE60",
            "annulee": "#E74C3C",
        }

        return format_html(
            '<span style="color:white; background:{}; '
            'padding:4px 8px; border-radius:4px;">{}</span>',
            couleurs.get(obj.statut, "#777777"),
            obj.get_statut_display(),
        )

