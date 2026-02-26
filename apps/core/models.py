from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Route(models.Model):
    source = models.ForeignKey(City, on_delete=models.CASCADE, related_name="routes_from")
    destination = models.ForeignKey(City, on_delete=models.CASCADE, related_name="routes_to")
    distance_km = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("source", "destination")

    def __str__(self):
        return f"{self.source} → {self.destination}"