from django.db import models

class Pile(models.Model):
    pile_id = models.CharField(max_length=50)
    pile_type = models.CharField(max_length=20)

    length = models.FloatField()
    cutoff = models.FloatField()
    cage_type = models.CharField(max_length=10)  # zoned / full

    # optional engineering inputs (expand later)
    stock_length = models.FloatField(default=12)
    anchorage = models.FloatField(default=0.75)

    # computed outputs
    total_length = models.FloatField(null=True, blank=True)
    total_weight = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pile_id