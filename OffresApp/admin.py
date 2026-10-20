
from django.contrib import admin
from django.utils.html import format_html
from .models import Offre


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "expedition",
        "transporteur",
        "vehicule",
        "prix",
        "delai_jours",
        "statut_colore",
        "date_proposition",
        "created_at",
        "updated_at",
    )

    list_filter = ("statut", "date_proposition")
    search_fields = (
        "expedition__reference",
        "transporteur__username",
        "transporteur__email",
        "vehicule__immatriculation",
    )

    ordering = ("-date_proposition",)
    date_hierarchy = "date_proposition"
    list_per_page = 25

    autocomplete_fields = ("expedition", "transporteur", "vehicule")

    readonly_fields = (
        "date_proposition",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Statut")
    def statut_colore(self, obj):
        couleurs = {
            "proposee": "#F0AD4E",
            "acceptee": "#5CB85C",
            "refusee": "#D9534F",
            "retiree": "#777777",
        }

        return format_html(
            '<span style="color:white; background:{}; '
            'padding:4px 8px; border-radius:4px;">{}</span>',
            couleurs.get(obj.statut, "#999999"),
            obj.get_statut_display(),
        )

