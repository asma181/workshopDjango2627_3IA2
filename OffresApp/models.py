
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Offre(models.Model):
    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    delai_jours = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    statut = models.CharField(
        max_length=20,
        choices=[
            ('proposee', 'proposee'),
            ('acceptee', 'acceptee'),
            ('refusee', 'refusee'),
            ('retiree', 'retiree')
        ],
        default='proposee'
    )

    date_proposition = models.DateField(auto_now_add=True)

    expedition = models.ForeignKey(
        "ExpeditionsApp.Expedition",
        on_delete=models.CASCADE,
        related_name='offres'
    )

    transporteur = models.ForeignKey(
        "EntreprisesApp.Utilsateur",
        on_delete=models.CASCADE,
        related_name='offres_proposees'
    )

    vehicule = models.ForeignKey(
        "VehiculesApp.vehicules",
        on_delete=models.CASCADE,
        related_name='offres_vehicules'
    )

    def clean(self):
        super().clean()

        if self.transporteur_id:
            entreprise_transporteur = getattr(
                self.transporteur, 'entreprise', None
            )

            if (
                entreprise_transporteur is None
                or entreprise_transporteur.type_entreprise != 'transporteur'
            ):
                raise ValidationError({
                    'transporteur':
                    "Le transporteur doit appartenir à une entreprise de type transporteur."
                })

        if self.expedition_id and self.expedition.statut != 'publiee':
            raise ValidationError({
                'expedition':
                "Une offre ne peut être créée que pour une expédition publiée."
            })

        if self.vehicule_id:
            if not self.vehicule.disponible:
                raise ValidationError({
                    'vehicule': "Ce véhicule n'est pas disponible."
                })

            entreprise_transporteur = getattr(
                self.transporteur, 'entreprise', None
            )
            if (
                entreprise_transporteur is not None
                and self.vehicule.entreprise_id != entreprise_transporteur.pk
            ):
                raise ValidationError({
                    'vehicule':
                    "Le véhicule doit appartenir à la même entreprise que le transporteur."
                })
