
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class vehicules(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def clean(self):
        super().clean()
        if (
            self.entreprise_id
            and self.entreprise.type_entreprise != "transporteur"
        ):
            raise ValidationError({
                "entreprise": (
                    "Le véhicule doit appartenir à une entreprise "
                    "de type transporteur."
                )
            })

    def __str__(self):
        return self.immatriculation
