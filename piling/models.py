import math
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class PilingProject(models.Model):
    """
    One project = one site contract (e.g. Dangote Fertiliser FZE).
    Spec thresholds and reinforcement defaults are configured here.
    """
    name = models.CharField(max_length=200)
    client = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    concrete_grade = models.CharField(max_length=20, default="C35/45")

    # Slurry spec limits
    sand_content_limit_pct = models.FloatField(
        default=5.0,
        help_text="Max sand content % allowed before concreting"
    )
    viscosity_min_secs = models.FloatField(default=30.0)
    viscosity_max_secs = models.FloatField(default=90.0)
    density_min = models.FloatField(default=1.01)
    density_max = models.FloatField(default=1.25)

    # Volume deviation alert
    volume_deviation_alert_pct = models.FloatField(
        default=15.0,
        help_text="Flag if actual concrete deviates from theoretical by this %"
    )

    # Reinforcement defaults — can be overridden per pile
    default_lap_length_m = models.FloatField(
        default=1.6,
        help_text="Lap length above cutoff level (m). Default 1.6m."
    )
    default_concrete_cover_mm = models.FloatField(
        default=75.0,
        help_text="Concrete cover to reinforcement (mm). Typical 75mm for piles."
    )

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.client}"

    class Meta:
        ordering = ["-created_at"]


class Pile(models.Model):
    """
    One record per bored pile.
    All calculated quantities are @property — never stored.
    Single source of truth is always the raw inputs.
    """
    PILE_TYPE_CHOICES = [
        ("test", "Test Pile"),
        ("working", "Working Pile"),
        ("reaction", "Reaction Pile"),
    ]

    project = models.ForeignKey(
        PilingProject, on_delete=models.PROTECT, related_name="piles"
    )
    pile_no = models.CharField(max_length=50)
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
    location_description = models.CharField(max_length=200, blank=True)
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
    actual_depth_from_casing_m = models.FloatField(
        null=True, blank=True,
        help_text="Measured actual pile depth from casing top (m)"
    )

    # ------------------------------------------------------------------ #
    # Reinforcement cage inputs                                            #
    # ------------------------------------------------------------------ #
    rebar_lowering_start = models.DateTimeField(null=True, blank=True)
    rebar_lowering_end = models.DateTimeField(null=True, blank=True)
    cover_blocks_fixed = models.BooleanField(default=False)

    # Main bars
    main_bar_count = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Number of main longitudinal bars (e.g. 12)"
    )
    main_bar_dia_mm = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(6.0), MaxValueValidator(50.0)],
        help_text="Main bar diameter in mm (e.g. 32)"
    )

    # Stiffener rings
    stiffener_dia_mm = models.FloatField(
        null=True, blank=True,
        help_text="Stiffener ring bar diameter in mm (e.g. 16)"
    )
    stiffener_spacing_m = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.1)],
        help_text="Stiffener ring centre-to-centre spacing (m)"
    )

    # Spiral / helix
    spiral_dia_mm = models.FloatField(
        null=True, blank=True,
        help_text="Spiral bar diameter in mm (e.g. 10)"
    )
    spiral_pitch_m = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.05)],
        help_text="Spiral ring centre-to-centre pitch (m)"
    )

    # Lap length — defaults to project setting, can be overridden per pile
    lap_length_m = models.FloatField(
        null=True, blank=True,
        help_text="Lap length above cutoff level (m). Leave blank to use project default (1.6m)."
    )

    # Concrete cover — defaults to project setting
    concrete_cover_mm = models.FloatField(
        null=True, blank=True,
        help_text="Concrete cover to reinforcement (mm). Leave blank for project default."
    )

    # ------------------------------------------------------------------ #
    # Flushing & inspection                                                #
    # ------------------------------------------------------------------ #
    flushing_start = models.DateTimeField(null=True, blank=True)
    flushing_end = models.DateTimeField(null=True, blank=True)
    inspection_collapse = models.BooleanField(
        null=True, blank=True,
        help_text="True=Collapse detected, False=No collapse"
    )

    # ------------------------------------------------------------------ #
    # Concreting                                                           #
    # ------------------------------------------------------------------ #
    casting_start = models.DateTimeField(null=True, blank=True)
    casting_end = models.DateTimeField(null=True, blank=True)
    actual_concrete_m3 = models.FloatField(null=True, blank=True)
    concrete_slump_mm = models.IntegerField(null=True, blank=True)

    # Projection above ground — optional, added to volume calc
    projection_above_ground_m = models.FloatField(
        null=True, blank=True, default=0.0,
        help_text="Length cast above ground / cutoff level (m). Default 0."
    )

    # Audit
    rough_sheet_photo = models.ImageField(
        upload_to="rough_sheets/%Y/%m/", null=True, blank=True,
        help_text="Photo of handwritten rough sheet — audit proof"
    )
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="piles_recorded"
    )
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ================================================================== #
    # CALCULATED PROPERTIES — derived only, never stored                  #
    # ================================================================== #

    # -- Helpers -------------------------------------------------------- #

    @property
    def _effective_depth(self):
        """Actual pile depth used for all calculations."""
        return self.actual_depth_from_casing_m or self.design_depth_m

    @property
    def _lap(self):
        """Resolved lap length — pile override or project default."""
        if self.lap_length_m is not None:
            return self.lap_length_m
        return self.project.default_lap_length_m

    @property
    def _cover(self):
        """Resolved concrete cover in mm."""
        if self.concrete_cover_mm is not None:
            return self.concrete_cover_mm
        return self.project.default_concrete_cover_mm

    @property
    def _projection(self):
        return self.projection_above_ground_m or 0.0

    # -- Concrete volume ------------------------------------------------ #

    @property
    def theoretical_volume_m3(self):
        """
        V = π × r² × (pile_depth + projection)
        Uses actual depth if recorded, falls back to design depth.
        """
        depth = self._effective_depth + self._projection
        radius = self.pile_diameter_m / 2
        return round(math.pi * radius ** 2 * depth, 2)

    @property
    def volume_deviation_pct(self):
        if self.actual_concrete_m3 and self.theoretical_volume_m3:
            theo = self.theoretical_volume_m3
            return round(((self.actual_concrete_m3 - theo) / theo) * 100, 1)
        return None

    @property
    def volume_flag(self):
        dev = self.volume_deviation_pct
        if dev is None:
            return "unknown"
        return "alert" if abs(dev) > self.project.volume_deviation_alert_pct else "ok"

    # -- Tremie tracking (assembly reference only) ---------------------- #

    @property
    def tremie_total_depth_m(self):
        lengths = list(self.tremie_sequences.values_list("length_m", flat=True))
        return round(sum(lengths), 3) if lengths else None

    # -- Rebar cage ----------------------------------------------------- #

    @property
    def cage_length_m(self):
        """
        cage_length = pile_depth + lap_length_above_cutoff
        The cage extends from the pile toe to lap_length above cutoff level.
        """
        return round(self._effective_depth + self._lap, 2)

    @property
    def n_stiffener_rings(self):
        """
        Number of stiffener rings = floor(pile_depth / spacing) + 1
        +1 because you have one at the top and one at the bottom.
        """
        if not self.stiffener_spacing_m:
            return None
        return math.floor(self._effective_depth / self.stiffener_spacing_m) + 1

    @property
    def n_spiral_rings(self):
        """Number of spiral ring turns = floor(pile_depth / pitch) + 1"""
        if not self.spiral_pitch_m:
            return None
        return math.floor(self._effective_depth / self.spiral_pitch_m) + 1

    @property
    def spiral_ring_circumference_m(self):
        """
        Mean circumference of one spiral turn:
        C = π × (pile_dia - 2×cover - spiral_bar_dia)
        Cover and bar dia in metres for consistency.
        """
        if not self.spiral_dia_mm:
            return None
        inner_dia = (
            self.pile_diameter_m
            - 2 * (self._cover / 1000)
            - (self.spiral_dia_mm / 1000)
        )
        return round(math.pi * inner_dia, 3)

    @property
    def total_spiral_length_m(self):
        n = self.n_spiral_rings
        circ = self.spiral_ring_circumference_m
        if n is None or circ is None:
            return None
        return round(n * circ, 2)

    @property
    def rebar_unit_weight_kg_per_m(self):
        """
        Standard steel weight formula:
        w (kg/m) = d² × 0.00617   where d is diameter in mm
        Applies to main bars — spiral uses same formula with spiral_dia.
        """
        if not self.main_bar_dia_mm:
            return None
        return round(self.main_bar_dia_mm ** 2 * 0.00617, 4)

    @property
    def spiral_unit_weight_kg_per_m(self):
        if not self.spiral_dia_mm:
            return None
        return round(self.spiral_dia_mm ** 2 * 0.00617, 4)

    @property
    def total_main_bar_length_m(self):
        if not self.main_bar_count:
            return None
        return round(self.main_bar_count * self.cage_length_m, 2)

    @property
    def total_rebar_weight_kg(self):
        """
        Total steel weight = (main bars + spirals) in kg.
        Stiffener rings use stiffener_dia for unit weight.
        """
        weight = 0.0
        missing = []

        # Main bars
        main_len = self.total_main_bar_length_m
        main_uw = self.rebar_unit_weight_kg_per_m
        if main_len and main_uw:
            weight += main_len * main_uw
        else:
            missing.append("main bars")

        # Spiral
        spiral_len = self.total_spiral_length_m
        spiral_uw = self.spiral_unit_weight_kg_per_m
        if spiral_len and spiral_uw:
            weight += spiral_len * spiral_uw
        else:
            missing.append("spiral")

        # Stiffener rings (circumference same formula as spiral)
        if self.stiffener_dia_mm and self.n_stiffener_rings:
            stiff_circ = math.pi * (
                self.pile_diameter_m
                - 2 * (self._cover / 1000)
                - (self.stiffener_dia_mm / 1000)
            )
            stiff_uw = self.stiffener_dia_mm ** 2 * 0.00617
            weight += self.n_stiffener_rings * stiff_circ * stiff_uw

        if not weight:
            return None
        return round(weight, 1)

    # -- Time tracking -------------------------------------------------- #

    @property
    def drilling_duration_hours(self):
        if self.drilling_start and self.drilling_end:
            return round(
                (self.drilling_end - self.drilling_start).total_seconds() / 3600, 2
            )
        return None

    def __str__(self):
        return f"{self.pile_no} — {self.project.name}"

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["project", "pile_no"]]


class TremieSequence(models.Model):
    """Tremie pipe assembly log — reference only, not used for volume."""
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
    STAGE_CHOICES = [
        ("initial", "Initial (pre-drilling)"),
        ("final", "Final (pre-concreting)"),
    ]

    pile = models.ForeignKey(
        Pile, on_delete=models.CASCADE, related_name="slurry_checks"
    )
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES)
    checked_at = models.DateTimeField(null=True, blank=True)
    viscosity_secs = models.FloatField()
    specific_gravity = models.FloatField(
        validators=[MinValueValidator(0.9), MaxValueValidator(2.0)]
    )
    sand_content_pct = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    ph_value = models.FloatField(null=True, blank=True)

    @property
    def sand_content_ok(self):
        return self.sand_content_pct < self.pile.project.sand_content_limit_pct

    @property
    def viscosity_ok(self):
        s = self.pile.project
        return s.viscosity_min_secs <= self.viscosity_secs <= s.viscosity_max_secs

    @property
    def density_ok(self):
        s = self.pile.project
        return s.density_min <= self.specific_gravity <= s.density_max

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
        stage_label = dict(self.STAGE_CHOICES).get(self.stage, self.stage)
        return f"{self.pile.pile_no} — {stage_label} slurry check"

    class Meta:
        ordering = ["pile", "stage"]


class SoilLayer(models.Model):
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

