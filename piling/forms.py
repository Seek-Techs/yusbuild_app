from django import forms
from django.forms import inlineformset_factory
from .models import PilingProject, Pile, TremieSequence, SlurryCheck, SoilLayer


# ------------------------------------------------------------------ #
# Shared widget helpers — large touch targets for field use           #
# ------------------------------------------------------------------ #

FIELD_CLASS = "field-input"
DATE_CLASS = "field-input field-datetime"


def field_attrs(placeholder="", extra_class=""):
    return {
        "class": f"{FIELD_CLASS} {extra_class}".strip(),
        "placeholder": placeholder,
        "autocomplete": "off",
    }


def datetime_attrs(placeholder=""):
    return {
        "class": DATE_CLASS,
        "placeholder": placeholder,
        "autocomplete": "off",
    }


# ------------------------------------------------------------------ #
# Step 1 — Pile Info                                                   #
# ------------------------------------------------------------------ #

class PileInfoForm(forms.ModelForm):
    class Meta:
        model = Pile
        fields = [
            "project",
            "pile_no",
            "pile_type",
            "pile_diameter_m",
            "design_depth_m",
            "location_description",
            "rig_no",
            "drawing_number",
            "pile_coordinate",
        ]
        widgets = {
            "project": forms.Select(attrs={"class": FIELD_CLASS}),
            "pile_no": forms.TextInput(
                attrs=field_attrs("e.g. Test Pile No. I")
            ),
            "pile_type": forms.Select(attrs={"class": FIELD_CLASS}),
            "pile_diameter_m": forms.NumberInput(
                attrs={**field_attrs("e.g. 1.2"), "step": "0.05", "min": "0.3"}
            ),
            "design_depth_m": forms.NumberInput(
                attrs={**field_attrs("e.g. 49"), "step": "0.5", "min": "1"}
            ),
            "location_description": forms.TextInput(
                attrs=field_attrs("e.g. B2 Area North, Grid C3")
            ),
            "rig_no": forms.TextInput(attrs=field_attrs("e.g. RIG-01")),
            "drawing_number": forms.TextInput(attrs=field_attrs()),
            "pile_coordinate": forms.TextInput(attrs=field_attrs("e.g. X453904")),
        }
        labels = {
            "pile_no": "Pile number",
            "pile_diameter_m": "Pile diameter (m)",
            "design_depth_m": "Design depth (m)",
            "location_description": "Location / grid ref",
            "rig_no": "Rig number",
        }


# ------------------------------------------------------------------ #
# Step 2 — Drilling Times                                              #
# ------------------------------------------------------------------ #

class DrillingTimesForm(forms.ModelForm):
    class Meta:
        model = Pile
        fields = [
            "casing_installation_start",
            "casing_installation_end",
            "top_of_casing_m",
            "drilling_start",
            "drilling_end",
            "actual_depth_from_casing_m",
        ]
        widgets = {
            "casing_installation_start": forms.DateTimeInput(
                attrs={**datetime_attrs("DD/MM/YYYY HH:MM"), "type": "datetime-local"}
            ),
            "casing_installation_end": forms.DateTimeInput(
                attrs={**datetime_attrs("DD/MM/YYYY HH:MM"), "type": "datetime-local"}
            ),
            "top_of_casing_m": forms.NumberInput(
                attrs={**field_attrs("e.g. 3.30"), "step": "0.01"}
            ),
            "drilling_start": forms.DateTimeInput(
                attrs={**datetime_attrs("DD/MM/YYYY HH:MM"), "type": "datetime-local"}
            ),
            "drilling_end": forms.DateTimeInput(
                attrs={**datetime_attrs("DD/MM/YYYY HH:MM"), "type": "datetime-local"}
            ),
            "actual_depth_from_casing_m": forms.NumberInput(
                attrs={**field_attrs("e.g. 49"), "step": "0.1"}
            ),
        }
        labels = {
            "casing_installation_start": "Casing install — start",
            "casing_installation_end": "Casing install — end",
            "top_of_casing_m": "Top of casing (m)",
            "drilling_start": "Drilling — start",
            "drilling_end": "Drilling — end",
            "actual_depth_from_casing_m": "Actual depth from casing (m)",
        }

    def clean(self):
        cleaned = super().clean()
        ds = cleaned.get("drilling_start")
        de = cleaned.get("drilling_end")
        if ds and de and de <= ds:
            self.add_error("drilling_end", "Drilling end must be after start.")
        cs = cleaned.get("casing_installation_start")
        ce = cleaned.get("casing_installation_end")
        if cs and ce and ce <= cs:
            self.add_error(
                "casing_installation_end", "Casing end must be after start."
            )
        return cleaned


# ------------------------------------------------------------------ #
# Step 3 — Tremie Sequence (inline formset)                            #
# ------------------------------------------------------------------ #

class TremieSequenceForm(forms.ModelForm):
    class Meta:
        model = TremieSequence
        fields = ["sequence_no", "length_m"]
        widgets = {
            "sequence_no": forms.NumberInput(
                attrs={
                    "class": "field-input field-seq",
                    "min": "1",
                    "readonly": True,
                }
            ),
            "length_m": forms.NumberInput(
                attrs={
                    "class": "field-input field-tremie-length",
                    "step": "0.1",
                    "min": "0.1",
                    "placeholder": "e.g. 3.3",
                }
            ),
        }
        labels = {"sequence_no": "#", "length_m": "Length (m)"}


TremieFormSet = inlineformset_factory(
    Pile,
    TremieSequence,
    form=TremieSequenceForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


# ------------------------------------------------------------------ #
# Step 4 — Slurry Check                                                #
# ------------------------------------------------------------------ #

class SlurryCheckForm(forms.ModelForm):
    class Meta:
        model = SlurryCheck
        fields = [
            "stage",
            "checked_at",
            "viscosity_secs",
            "specific_gravity",
            "sand_content_pct",
            "ph_value",
        ]
        widgets = {
            "stage": forms.Select(attrs={"class": FIELD_CLASS}),
            "checked_at": forms.DateTimeInput(
                attrs={**datetime_attrs(), "type": "datetime-local"}
            ),
            "viscosity_secs": forms.NumberInput(
                attrs={
                    **field_attrs("e.g. 34.54"),
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "specific_gravity": forms.NumberInput(
                attrs={
                    **field_attrs("e.g. 1.09"),
                    "step": "0.01",
                    "min": "0.9",
                    "max": "2.0",
                }
            ),
            "sand_content_pct": forms.NumberInput(
                attrs={
                    **field_attrs("e.g. 2.5"),
                    "step": "0.1",
                    "min": "0",
                    "max": "100",
                }
            ),
            "ph_value": forms.NumberInput(
                attrs={
                    **field_attrs("e.g. 9.5 (optional)"),
                    "step": "0.1",
                    "min": "0",
                    "max": "14",
                }
            ),
        }
        labels = {
            "checked_at": "Time of check",
            "viscosity_secs": "Viscosity (Marsh funnel, secs)",
            "specific_gravity": "Specific gravity / density",
            "sand_content_pct": "Sand content (%)",
            "ph_value": "pH value (optional)",
        }


SlurryFormSet = inlineformset_factory(
    Pile,
    SlurryCheck,
    form=SlurryCheckForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=False,  # don't accidentally delete a QC record
)


# ------------------------------------------------------------------ #
# Step 5 — Soil Log                                                    #
# ------------------------------------------------------------------ #

class SoilLayerForm(forms.ModelForm):
    class Meta:
        model = SoilLayer
        fields = ["depth_from_m", "depth_to_m", "texture", "notes"]
        widgets = {
            "depth_from_m": forms.NumberInput(
                attrs={**field_attrs("From (m)"), "step": "0.5", "min": "0"}
            ),
            "depth_to_m": forms.NumberInput(
                attrs={**field_attrs("To (m)"), "step": "0.5", "min": "0.1"}
            ),
            "texture": forms.Select(attrs={"class": FIELD_CLASS}),
            "notes": forms.TextInput(attrs=field_attrs("Optional note")),
        }
        labels = {
            "depth_from_m": "From (m)",
            "depth_to_m": "To (m)",
            "texture": "Soil texture",
        }

    def clean(self):
        cleaned = super().clean()
        d_from = cleaned.get("depth_from_m")
        d_to = cleaned.get("depth_to_m")
        if d_from is not None and d_to is not None and d_to <= d_from:
            self.add_error("depth_to_m", "Depth 'To' must be greater than 'From'.")
        return cleaned


SoilLayerFormSet = inlineformset_factory(
    Pile,
    SoilLayer,
    form=SoilLayerForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


# ------------------------------------------------------------------ #
# Step 6 — Concreting & Rebar                                          #
# ------------------------------------------------------------------ #

class ConcretingForm(forms.ModelForm):
    class Meta:
        model = Pile
        fields = [
            "rebar_lowering_start",
            "rebar_lowering_end",
            "cover_blocks_fixed",
            "main_bars_spec",
            "stiffener_spec",
            "spiral_bars_spec",
            "flushing_start",
            "flushing_end",
            "inspection_collapse",
            "casting_start",
            "casting_end",
            "actual_concrete_m3",
            "concrete_slump_mm",
            "rough_sheet_photo",
        ]
        widgets = {
            "rebar_lowering_start": forms.DateTimeInput(
                attrs={**datetime_attrs(), "type": "datetime-local"}
            ),
            "rebar_lowering_end": forms.DateTimeInput(
                attrs={**datetime_attrs(), "type": "datetime-local"}
            ),
            "cover_blocks_fixed": forms.CheckboxInput(
                attrs={"class": "field-checkbox"}
            ),
            "main_bars_spec": forms.TextInput(attrs=field_attrs("e.g. 32mm")),
            "stiffener_spec": forms.TextInput(
                attrs=field_attrs("e.g. 2.25m spacing")
            ),
            "spiral_bars_spec": forms.TextInput(
                attrs=field_attrs("e.g. 260mm @ 1/c")
            ),
            "flushing_start": forms.DateTimeInput(
                attrs={**datetime_attrs(), "type": "datetime-local"}
            ),
            "flushing_end": forms.DateTimeInput(
                attrs={**datetime_attrs(), "type": "datetime-local"}
            ),
            "inspection_collapse": forms.NullBooleanSelect(
                attrs={"class": FIELD_CLASS}
            ),
            "casting_start": forms.DateTimeInput(
                attrs={**datetime_attrs(), "type": "datetime-local"}
            ),
            "casting_end": forms.DateTimeInput(
                attrs={**datetime_attrs(), "type": "datetime-local"}
            ),
            "actual_concrete_m3": forms.NumberInput(
                attrs={
                    **field_attrs("e.g. 40"),
                    "step": "0.5",
                    "min": "0",
                    "id": "id_actual_concrete_m3",
                }
            ),
            "concrete_slump_mm": forms.NumberInput(
                attrs={**field_attrs("mm"), "min": "0", "max": "300"}
            ),
            "rough_sheet_photo": forms.ClearableFileInput(
                attrs={"class": "field-file", "accept": "image/*", "capture": "environment"}
            ),
        }
        labels = {
            "rebar_lowering_start": "Rebar lowering — start",
            "rebar_lowering_end": "Rebar lowering — end",
            "cover_blocks_fixed": "Cover blocks fixed?",
            "flushing_start": "Flushing — start",
            "flushing_end": "Flushing — end",
            "inspection_collapse": "Borehole inspection",
            "casting_start": "Concreting — start",
            "casting_end": "Concreting — end",
            "actual_concrete_m3": "Actual concrete poured (m³)",
            "concrete_slump_mm": "Slump (mm)",
            "rough_sheet_photo": "Photo of rough sheet (audit)",
        }

    def clean(self):
        cleaned = super().clean()
        cs = cleaned.get("casting_start")
        ce = cleaned.get("casting_end")
        if cs and ce and ce <= cs:
            self.add_error("casting_end", "Casting end must be after start.")
        return cleaned
