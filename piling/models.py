import math
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class PilingProject(models.Model):
    """
    One project = one site contract (e.g. Dangote Fertiliser FZE).
    Spec thresholds are configured here, not hardcoded.
    """
    name = models.CharField(max_length=200)
    client = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    concrete_grade = models.CharField(max_length=20, default="C35/45")
    # Slurry spec limits (project-specific)
    sand_content_limit_pct = models.FloatField(
        default=5.0,
        help_text="Max sand content % allowed before concreting"
    )
    viscosity_min_secs = models.FloatField(default=30.0)
    viscosity_max_secs = models.FloatField(default=90.0)
    density_min = models.FloatField(default=1.01)
    density_max = models.FloatField(default=1.25)
    # Volume deviation alert threshold
    volume_deviation_alert_pct = models.FloatField(
        default=15.0,
        help_text="Flag if actual concrete deviates from theoretical by this %"
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.client}"

    class Meta:
        ordering = ["-created_at"]


class Pile(models.Model):
    """
    One record per bored pile. Timestamps drive audit trail.
    Calculated fields (theoretical volume, deviation) are properties,
    never stored — single source of truth is the inputs.
    """
    PILE_TYPE_CHOICES = [
        ("test", "Test Pile"),
        ("working", "Working Pile"),
        ("reaction", "Reaction Pile"),
    ]

    project = models.ForeignKey(
        PilingProject, on_delete=models.PROTECT, related_name="piles"
    )
    pile_no = models.CharField(max_length=50)           # e.g. "Test Pile No. I"
    pile_type = models.CharField(
        max_length=20, choices=PILE_TYPE_CHOICES, default="working"
    )
    pile_diameter_m = models.FloatField(
        validators=[MinValueValidator(0.3), MaxValueValidator(3.0)]
    )
    design_depth_m = models.FloatField(
        validators=[MinValueValidator(1.0)],
        help_text="Design total depth from ground level (m)"
    )
    location_description = models.CharField(
        max_length=200, blank=True,
        help_text="e.g. B2 Area North, Grid C3"
    )
    rig_no = models.CharField(max_length=20, blank=True)
    drawing_number = models.CharField(max_length=100, blank=True)
    pile_coordinate = models.CharField(max_length=100, blank=True)

    # Casing
    top_of_casing_m = models.FloatField(null=True, blank=True)
    casing_installation_start = models.DateTimeField(null=True, blank=True)
    casing_installation_end = models.DateTimeField(null=True, blank=True)

    # Drilling
    drilling_start = models.DateTimeField(null=True, blank=True)
    drilling_end = models.DateTimeField(null=True, blank=True)
    actual_depth_from_casing_m = models.FloatField(null=True, blank=True)

    # Rebar cage
    rebar_lowering_start = models.DateTimeField(null=True, blank=True)
    rebar_lowering_end = models.DateTimeField(null=True, blank=True)
    cover_blocks_fixed = models.BooleanField(default=False)
    main_bars_spec = models.CharField(
        max_length=50, blank=True, help_text="e.g. 32mm"
    )
    stiffener_spec = models.CharField(
        max_length=50, blank=True, help_text="e.g. 2.25m spacing"
    )
    spiral_bars_spec = models.CharField(
        max_length=50, blank=True, help_text="e.g. 260mm @ 1/c"
    )

    # Flushing (cleaning before concreting)
    flushing_start = models.DateTimeField(null=True, blank=True)
    flushing_end = models.DateTimeField(null=True, blank=True)
    inspection_collapse = models.BooleanField(
        null=True, blank=True,
        help_text="True=Collapse detected, False=No collapse"
    )

    # Concreting
    casting_start = models.DateTimeField(null=True, blank=True)
    casting_end = models.DateTimeField(null=True, blank=True)
    actual_concrete_m3 = models.FloatField(null=True, blank=True)
    concrete_slump_mm = models.IntegerField(null=True, blank=True)

    # Audit
    rough_sheet_photo = models.ImageField(
        upload_to="rough_sheets/%Y/%m/", null=True, blank=True,
        help_text="Photo of handwritten rough sheet — audit proof"
    )
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="piles_recorded"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------ #
    # Calculated properties — never stored, always derived from inputs    #
    # ------------------------------------------------------------------ #

    @property
    def tremie_total_depth_m(self):
        lengths = list(
            self.tremie_sequences.values_list("length_m", flat=True)
        )
        return round(sum(lengths), 3) if lengths else None

    @property
    def theoretical_volume_m3(self):
        depth = self.tremie_total_depth_m
        if depth is None:
            return None
        radius = self.pile_diameter_m / 2
        return round(math.pi * radius ** 2 * depth, 2)

    @property
    def volume_deviation_pct(self):
        if self.actual_concrete_m3 and self.theoretical_volume_m3:
            theo = self.theoretical_volume_m3
            return round(
                ((self.actual_concrete_m3 - theo) / theo) * 100, 1
            )
        return None

    @property
    def volume_flag(self):
        dev = self.volume_deviation_pct
        if dev is None:
            return "unknown"
        threshold = self.project.volume_deviation_alert_pct
        if abs(dev) > threshold:
            return "alert"
        return "ok"

    @property
    def drilling_duration_hours(self):
        if self.drilling_start and self.drilling_end:
            delta = self.drilling_end - self.drilling_start
            return round(delta.total_seconds() / 3600, 2)
        return None

    def __str__(self):
        return f"{self.pile_no} — {self.project.name}"

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["project", "pile_no"]]


class TremieSequence(models.Model):
    """
    Each row = one pipe segment lowered during tremie pipe assembly.
    Sequence order matters — sequence_no drives the display order.
    """
    pile = models.ForeignKey(
        Pile, on_delete=models.CASCADE, related_name="tremie_sequences"
    )
    sequence_no = models.PositiveSmallIntegerField()
    length_m = models.FloatField(
        validators=[MinValueValidator(0.1), MaxValueValidator(20.0)]
    )

    class Meta:
        ordering = ["sequence_no"]
        unique_together = [["pile", "sequence_no"]]

    def __str__(self):
        return f"Pile {self.pile.pile_no} — Tremie #{self.sequence_no}: {self.length_m}m"


class SlurryCheck(models.Model):
    """
    Bentonite slurry QC readings. Min two per pile: initial + final pre-cast.
    QC flags are computed against project spec — no hardcoding.
    """
    STAGE_CHOICES = [
        ("initial", "Initial (pre-drilling)"),
        ("final", "Final (pre-concreting)"),
    ]

    pile = models.ForeignKey(
        Pile, on_delete=models.CASCADE, related_name="slurry_checks"
    )
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES)
    checked_at = models.DateTimeField()
    viscosity_secs = models.FloatField(
        help_text="Marsh funnel viscosity in seconds"
    )
    specific_gravity = models.FloatField(
        validators=[MinValueValidator(0.9), MaxValueValidator(2.0)],
        help_text="Density / specific gravity reading"
    )
    sand_content_pct = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    ph_value = models.FloatField(null=True, blank=True)

    # ------------------------------------------------------------------ #
    # QC flags — always checked against project spec                      #
    # ------------------------------------------------------------------ #

    @property
    def sand_content_ok(self):
        return self.sand_content_pct < self.pile.project.sand_content_limit_pct

    @property
    def viscosity_ok(self):
        spec = self.pile.project
        return spec.viscosity_min_secs <= self.viscosity_secs <= spec.viscosity_max_secs

    @property
    def density_ok(self):
        spec = self.pile.project
        return spec.density_min <= self.specific_gravity <= spec.density_max

    @property
    def all_ok(self):
        return self.sand_content_ok and self.viscosity_ok and self.density_ok

    @property
    def flags(self):
        issues = []
        if not self.viscosity_ok:
            issues.append(f"Viscosity {self.viscosity_secs}s out of spec")
        if not self.density_ok:
            issues.append(f"SG {self.specific_gravity} out of spec")
        if not self.sand_content_ok:
            issues.append(f"Sand content {self.sand_content_pct}% exceeds limit")
        return issues

    def __str__(self):
        return f"{self.pile.pile_no} — {self.get_stage_display()} slurry check"

    class Meta:
        ordering = ["pile", "stage"]


class SoilLayer(models.Model):
    """
    Soil texture log. Depth intervals from the rough sheet annotations.
    Used to render the borehole log visual.
    """
    TEXTURE_CHOICES = [
        ("normal_sand", "Normal sand"),
        ("slightly_mud", "Slightly mud"),
        ("soft_mud", "Soft mud"),
        ("strong_mud", "Strong mud"),
        ("brown_clay", "Brown clay"),
        ("brown_sharp_sand", "Brown sharp sand"),
        ("grey_sharp_sand", "Grey sharp sand"),
        ("strong_clay", "Strong clay"),
        ("rock", "Rock"),
        ("other", "Other"),
    ]

    pile = models.ForeignKey(
        Pile, on_delete=models.CASCADE, related_name="soil_layers"
    )
    depth_from_m = models.FloatField(validators=[MinValueValidator(0.0)])
    depth_to_m = models.FloatField(validators=[MinValueValidator(0.1)])
    texture = models.CharField(max_length=50, choices=TEXTURE_CHOICES)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["depth_from_m"]

    def __str__(self):
        return (
            f"{self.pile.pile_no} — "
            f"{self.depth_from_m}m to {self.depth_to_m}m: {self.texture}"
        )
