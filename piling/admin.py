from django.contrib import admin
from django.utils.html import format_html
from .models import PilingProject, Pile, TremieSequence, SlurryCheck, SoilLayer


@admin.register(PilingProject)
class PilingProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "client", "location", "concrete_grade", "sand_content_limit_pct"]
    search_fields = ["name", "client"]


class TremieInline(admin.TabularInline):
    model = TremieSequence
    extra = 1
    ordering = ["sequence_no"]


class SlurryInline(admin.TabularInline):
    model = SlurryCheck
    extra = 0
    readonly_fields = ["sand_content_ok", "viscosity_ok", "density_ok"]

    def sand_content_ok(self, obj):
        ok = obj.sand_content_ok
        return format_html(
            '<span style="color:{}">●</span> {}',
            "green" if ok else "red",
            "OK" if ok else "FAIL",
        )

    def viscosity_ok(self, obj):
        ok = obj.viscosity_ok
        return format_html(
            '<span style="color:{}">●</span> {}',
            "green" if ok else "red",
            "OK" if ok else "FAIL",
        )

    def density_ok(self, obj):
        ok = obj.density_ok
        return format_html(
            '<span style="color:{}">●</span> {}',
            "green" if ok else "red",
            "OK" if ok else "FAIL",
        )


class SoilInline(admin.TabularInline):
    model = SoilLayer
    extra = 0
    ordering = ["depth_from_m"]


@admin.register(Pile)
class PileAdmin(admin.ModelAdmin):
    list_display = [
        "pile_no",
        "project",
        "pile_diameter_m",
        "design_depth_m",
        "location_description",
        "volume_flag_display",
        "actual_concrete_m3",
        "theoretical_vol_display",
        "recorded_by",
        "created_at",
    ]
    list_filter = ["project", "pile_type", "recorded_by"]
    search_fields = ["pile_no", "location_description"]
    readonly_fields = [
        "theoretical_volume_m3",
        "tremie_total_depth_m",
        "volume_deviation_pct",
        "volume_flag",
        "drilling_duration_hours",
        "created_at",
        "updated_at",
    ]
    inlines = [TremieInline, SlurryInline, SoilInline]

    fieldsets = (
        ("Identity", {
            "fields": (
                "project", "pile_no", "pile_type", "pile_diameter_m",
                "design_depth_m", "location_description", "rig_no",
                "drawing_number", "pile_coordinate",
            )
        }),
        ("Casing", {
            "fields": (
                "top_of_casing_m",
                "casing_installation_start",
                "casing_installation_end",
            ),
            "classes": ("collapse",),
        }),
        ("Drilling", {
            "fields": (
                "drilling_start", "drilling_end",
                "actual_depth_from_casing_m",
                "drilling_duration_hours",
            )
        }),
        ("Rebar", {
            "fields": (
                "rebar_lowering_start", "rebar_lowering_end",
                "cover_blocks_fixed", "main_bars_spec",
                "stiffener_spec", "spiral_bars_spec",
            ),
            "classes": ("collapse",),
        }),
        ("Flushing & Inspection", {
            "fields": (
                "flushing_start", "flushing_end", "inspection_collapse",
            ),
            "classes": ("collapse",),
        }),
        ("Concreting", {
            "fields": (
                "casting_start", "casting_end",
                "actual_concrete_m3", "concrete_slump_mm",
                "theoretical_volume_m3", "tremie_total_depth_m",
                "volume_deviation_pct", "volume_flag",
            )
        }),
        ("Audit", {
            "fields": (
                "rough_sheet_photo", "recorded_by",
                "created_at", "updated_at",
            )
        }),
    )

    def theoretical_vol_display(self, obj):
        v = obj.theoretical_volume_m3
        return f"{v} m³" if v else "—"
    theoretical_vol_display.short_description = "Theoretical vol."

    def volume_flag_display(self, obj):
        flag = obj.volume_flag
        color = {"ok": "green", "alert": "red", "unknown": "gray"}.get(flag, "gray")
        dev = obj.volume_deviation_pct
        label = f"{dev:+.1f}%" if dev is not None else "—"
        return format_html('<span style="color:{}">● {}</span>', color, label)
    volume_flag_display.short_description = "Vol. deviation"
