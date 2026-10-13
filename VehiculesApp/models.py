
from django.db import models
from django.core.validators import MinValueValidator


class vehicule(models.Model):
    immatriculation = models.CharField(
        max_length=20,
        unique=True
    )

    capacite_kg = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    entreprise = models.ForeignKey(
        "EntreprisesApp.entreprise",
        on_delete=models.CASCADE,
        related_name='vehicules'
    )

    disponible = models.BooleanField(default=True)

    type_vehicule = models.CharField(
        max_length=20,
        choices=[
            ('camionnette', 'camionnette'),
            ('camion_porteur', 'camion_porteur'),
            ('semi_remorque', 'semi_remorque'),
            ('fourgon', 'fourgon')
        ]
    )

    def clean(self):
        super().clean()

        if self.capacite_kg == 0:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'capacite_kg': "La capacité doit être différente de zéro."
            })

    def __str__(self):
        return self.immatriculation
