
import re
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_reference(value):
    pattern = r"^EXP-\d{2}-\d{5}$"

    if not re.fullmatch(pattern, value):
        raise ValidationError(
            "La référence doit respecter le format EXP-AA-NNNNN."
        )


class Expedition(models.Model):

    reference = models.CharField(
        max_length=12,
        unique=True,
        validators=[validate_reference],
        blank=True,
    )

    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )

    statut = models.CharField(
        max_length=20,
        choices=[
            ("publiee", "Publiée"),
            ("attribuee", "Attribuée"),
            ("en_cours", "En cours"),
            ("livree", "Livrée"),
            ("annulee", "Annulée"),
        ],
        default="publiee",
    )

    entreprise = models.ForeignKey(
        "EntreprisesApp.entreprise",
        on_delete=models.CASCADE,
        related_name="expeditions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        if (
            self.entreprise_id
            and self.entreprise.type_entreprise != "chargeur"
        ):
            raise ValidationError({
                "entreprise": (
                    "L'entreprise doit être de type chargeur."
                )
            })

    def save(self, *args, **kwargs):
        with transaction.atomic():

            # Générer la référence uniquement à la création
            if self._state.adding and not self.reference:
                annee = timezone.localdate().year % 100
                prefixe = f"EXP-{annee:02d}-"

                derniere_expedition = (
                    Expedition.objects
                    .select_for_update()
                    .filter(reference__startswith=prefixe)
                    .order_by("-reference")
                    .first()
                )

                if derniere_expedition:
                    dernier_numero = int(
                        derniere_expedition.reference[-5:]
                    )
                    prochain_numero = dernier_numero + 1
                else:
                    prochain_numero = 1

                if prochain_numero > 99999:
                    raise ValidationError(
                        "Le nombre maximal d'expéditions "
                        "pour cette année est atteint."
                    )

                self.reference = (
                    f"{prefixe}{prochain_numero:05d}"
                )

            # Valider les champs et les règles métier
            self.full_clean()

            super().save(*args, **kwargs)

    def __str__(self):
        return self.reference
