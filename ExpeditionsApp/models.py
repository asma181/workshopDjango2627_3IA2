from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import re


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
        validators=[validate_reference]
    )

    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    statut = models.CharField(
        max_length=20,
        choices=[
            ('publiee', 'publiee'),
            ('attribuee', 'attribuee'),
            ('en_cours', 'en_cours'),
            ('livree', 'livree'),
            ('annulee', 'annulee')
        ],
        default='publiee'
    )

    entreprise = models.ForeignKey(
        "EntreprisesApp.entreprise",
        on_delete=models.CASCADE,
        related_name='expeditions'
    )

    def clean(self):
        super().clean()

        if (
            self.entreprise_id
            and self.entreprise.type_entreprise != 'chargeur'
        ):
            raise ValidationError({
                'entreprise': "L'entreprise doit être de type chargeur."
            })

    def __str__(self):
        return self.reference
