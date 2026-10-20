
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Offre(models.Model):

    STATUT_CHOICES = [
        ("proposee", "Proposée"),
        ("acceptee", "Acceptée"),
        ("refusee", "Refusée"),
        ("retiree", "Retirée"),
    ]

    # Capacités indicatives maximales par type de véhicule (en kg)
    CAPACITES_TYPES = {
        "camionnette": 1500,
        "fourgon": 3500,
        "camion_porteur": 19000,
        "semi_remorque": 26000,
    }

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )

    delai_jours = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="proposee",
    )

    date_proposition = models.DateField(auto_now_add=True)

    expedition = models.ForeignKey(
        "ExpeditionsApp.Expedition",
        on_delete=models.CASCADE,
        related_name="offres",
    )

    transporteur = models.ForeignKey(
        "EntreprisesApp.Utilsateur",
        on_delete=models.CASCADE,
        related_name="offres_proposees",
    )

    vehicule = models.ForeignKey(
        "VehiculesApp.vehicules",
        on_delete=models.CASCADE,
        related_name="offres_vehicules",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        entreprise_transporteur = None

        # 1. Le transporteur doit appartenir à une entreprise
        #    de type transporteur.
        if self.transporteur_id:
            entreprise_transporteur = getattr(
                self.transporteur, "entreprise", None
            )

            if (
                entreprise_transporteur is None
                or entreprise_transporteur.type_entreprise
                != "transporteur"
            ):
                raise ValidationError({
                    "transporteur": (
                        "Le transporteur doit être associé à "
                        "une entreprise de type transporteur."
                    )
                })

        # 2. Une nouvelle offre proposée exige une expédition publiée.
        if (
            self._state.adding
            and self.statut == "proposee"
            and self.expedition_id
            and self.expedition.statut != "publiee"
        ):
            raise ValidationError({
                "expedition": (
                    "Une nouvelle offre ne peut être créée que "
                    "pour une expédition publiée."
                )
            })

        # 3. Pas de deux offres proposées par la même entreprise
        #    pour la même expédition.
        if (
            self.statut == "proposee"
            and self.expedition_id
            and entreprise_transporteur is not None
        ):
            doublons = Offre.objects.filter(
                expedition_id=self.expedition_id,
                statut="proposee",
                transporteur__entreprise__pk=(
                    entreprise_transporteur.pk
                ),
            )

            if self.pk:
                doublons = doublons.exclude(pk=self.pk)

            if doublons.exists():
                raise ValidationError({
                    "expedition": (
                        "Cette entreprise possède déjà une offre "
                        "proposée pour cette expédition."
                    )
                })

        # 4. Vérifier le véhicule associé.
        if self.vehicule_id:

            # Un véhicule indisponible ne peut pas être utilisé
            # pour créer une nouvelle offre proposée.
            if (
                self._state.adding
                and self.statut == "proposee"
                and not self.vehicule.disponible
            ):
                raise ValidationError({
                    "vehicule": "Ce véhicule n'est pas disponible."
                })

            # Le véhicule doit appartenir à la même entreprise.
            if (
                entreprise_transporteur is not None
                and self.vehicule.entreprise_id
                != entreprise_transporteur.pk
            ):
                raise ValidationError({
                    "vehicule": (
                        "Le véhicule doit appartenir à la même "
                        "entreprise que le transporteur."
                    )
                })

            # 5. Vérifier la capacité réelle et la compatibilité
            #    avec le type de véhicule.
            if self.expedition_id:
                poids = self.expedition.poids_kg
                capacite = self.vehicule.capacite_kg
                type_vehicule = self.vehicule.type_vehicule

                if poids > capacite:
                    raise ValidationError({
                        "vehicule": (
                            "Le poids de l'expédition dépasse "
                            "la capacité du véhicule."
                        )
                    })

                capacite_type = self.CAPACITES_TYPES.get(
                    type_vehicule
                )

                if (
                    capacite_type is not None
                    and poids > capacite_type
                ):
                    raise ValidationError({
                        "vehicule": (
                            "Le poids de l'expédition n'est pas "
                            "compatible avec ce type de véhicule."
                        )
                    })

    def save(self, *args, **kwargs):
        with transaction.atomic():

            ancien_statut = None

            if self.pk:
                ancien_statut = (
                    Offre.objects
                    .filter(pk=self.pk)
                    .values_list("statut", flat=True)
                    .first()
                )

            # Exécuter les validations métier avant l'enregistrement.
            self.full_clean()

            super().save(*args, **kwargs)

            # 6. Cascade lors de l'acceptation d'une offre.
            if (
                self.statut == "acceptee"
                and ancien_statut != "acceptee"
            ):
                # L'expédition devient attribuée.
                self.expedition.__class__.objects.filter(
                    pk=self.expedition_id
                ).update(statut="attribuee")

                # Toutes les autres offres proposées sont refusées.
                Offre.objects.filter(
                    expedition_id=self.expedition_id,
                    statut="proposee",
                ).exclude(
                    pk=self.pk
                ).update(
                    statut="refusee"
                )

    def __str__(self):
        return (
            f"Offre {self.pk} - "
            f"{self.prix} - {self.statut}"
        )
