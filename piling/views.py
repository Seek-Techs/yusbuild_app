from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from piles.services.calculations import calculate_pile

from .models import Pile, PilingProject, TremieSequence, SlurryCheck, SoilLayer
from .forms import (
    PileInfoForm,
    DrillingTimesForm,
    TremieFormSet,
    SlurryFormSet,
    SoilLayerFormSet,
    ConcretingForm,
)

# ------------------------------------------------------------------ #
# Formset prefixes — must match JS in templates exactly               #
# ------------------------------------------------------------------ #
TREMIE_PREFIX  = "tremie"
SLURRY_PREFIX  = "slurry"
SOIL_PREFIX    = "soil"

# ------------------------------------------------------------------ #
# Wizard step order                                                    #
# ------------------------------------------------------------------ #
STEPS = [
    "pile_info",
    "drilling_times",
    "tremie_entry",
    "slurry_check",
    "soil_log",
    "concreting",
    "review",
]

STEP_LABELS = {
    "pile_info":      "Pile Info",
    "drilling_times": "Drilling",
    "tremie_entry":   "Tremie",
    "slurry_check":   "Slurry",
    "soil_log":       "Soil Log",
    "concreting":     "Concreting",
    "review":         "Review",
}


# ------------------------------------------------------------------ #
# Dashboard                                                            #
# ------------------------------------------------------------------ #
@login_required
def dashboard(request):
    projects = PilingProject.objects.prefetch_related("piles").all()
    recent_piles = Pile.objects.select_related("project").order_by("-created_at")[:20]
    return render(request, "piling/dashboard.html", {
        "projects": projects,
        "recent_piles": recent_piles,
        "steps": STEPS,
        "step_labels": STEP_LABELS,
    })


# ------------------------------------------------------------------ #
# Pile detail (read-only)                                              #
# ------------------------------------------------------------------ #
@login_required
def pile_detail(request, pile_pk):
    pile = get_object_or_404(
        Pile.objects.select_related("project")
            .prefetch_related("tremie_sequences", "slurry_checks", "soil_layers"),
        pk=pile_pk,
    )
    return render(request, "piling/pile_detail.html", {
        "pile": pile,
        "slurry_checks": pile.slurry_checks.all(),
        "tremie_sequences": pile.tremie_sequences.all(),
        "soil_layers": pile.soil_layers.all(),
    })


# ------------------------------------------------------------------ #
# Step 1 — Pile Info                                                   #
# ------------------------------------------------------------------ #
@login_required
def step_pile_info(request, pile_pk=None):
    pile = get_object_or_404(Pile, pk=pile_pk) if pile_pk else None

    if request.method == "POST":
        form = PileInfoForm(request.POST, instance=pile)
        if form.is_valid():
            pile = form.save(commit=False)
            pile.recorded_by = request.user
            pile.save()
            # 🔥 RUN CALCULATION ENGINE
            result = calculate_pile(pile)

            pile.total_length = result["total_length"]
            pile.total_weight = result["total_weight"]
            pile.save()

            messages.success(request, "Pile info saved + calculated.")
            return redirect("piling:step_drilling_times", pile_pk=pile.pk)
    else:
        form = PileInfoForm(instance=pile)

    return render(request, "piling/step_pile_info.html", {
        "form": form,
        "pile": pile,
        "current_step": "pile_info",
        "steps": STEPS,
        "step_labels": STEP_LABELS,
    })


# ------------------------------------------------------------------ #
# Step 2 — Drilling Times                                              #
# ------------------------------------------------------------------ #
@login_required
def step_drilling_times(request, pile_pk):
    pile = get_object_or_404(Pile, pk=pile_pk)

    if request.method == "POST":
        form = DrillingTimesForm(request.POST, instance=pile)
        if form.is_valid():
            form.save()
            messages.success(request, "Drilling times saved.")
            return redirect("piling:step_tremie_entry", pile_pk=pile.pk)
    else:
        form = DrillingTimesForm(instance=pile)

    return render(request, "piling/step_drilling_times.html", {
        "form": form,
        "pile": pile,
        "current_step": "drilling_times",
        "steps": STEPS,
        "step_labels": STEP_LABELS,
    })


# ------------------------------------------------------------------ #
# Step 3 — Tremie Sequence                                             #
# ------------------------------------------------------------------ #
@login_required
def step_tremie_entry(request, pile_pk):

    pile = get_object_or_404(Pile, pk=pile_pk)

    if request.method == "POST":

        formset = TremieFormSet(
            request.POST,
            instance=pile,
            prefix=TREMIE_PREFIX
        )

        if formset.is_valid():

            instances = formset.save(commit=False)

            if hasattr(formset,'deleted_objects'):
                for obj in formset.deleted_objects:
                    obj.delete()

            for i,obj in enumerate(instances,start=1):

                obj.sequence_no=i
                obj.pile=pile
                obj.save()
            formset.save_m2m() 
            messages.success(request,"Tremie sequence saved")

            return redirect(
                "piling:step_slurry_check",
                pile_pk=pile.pk
            )

        else:

            for i,errors in enumerate(formset.errors):

                if errors:

                    messages.error(
                        request,
                        f"Row {i+1}: {errors}"
                    )

            if formset.non_form_errors():

                messages.error(
                    request,
                    formset.non_form_errors()
                )

    else:

        formset = TremieFormSet(
            instance=pile,
            prefix=TREMIE_PREFIX
        )

    return render(request,"piling/step_tremie_entry.html",{

        "formset":formset,
        "pile":pile,
        "tremie_prefix":TREMIE_PREFIX,
        "current_step":"tremie_entry",
        "steps":STEPS,
        "step_labels":STEP_LABELS

    })


# ------------------------------------------------------------------ #
# Step 4 — Slurry Check                                                #
# ------------------------------------------------------------------ #
@login_required
def step_slurry_check(request, pile_pk):

    pile = get_object_or_404(
        Pile.objects.select_related("project"),
        pk=pile_pk
    )

    if request.method == "POST":

        formset = SlurryFormSet(

            request.POST,
            instance=pile,
            prefix=SLURRY_PREFIX

        )

        if formset.is_valid():

            instances = formset.save(commit=False)

            if hasattr(formset,'deleted_objects'):

                for obj in formset.deleted_objects:

                    obj.delete()

            for i,obj in enumerate(instances,start=1):

                obj.sequence_no = i
                obj.pile = pile
                obj.save()

            formset.save_m2m() 

            messages.success(
                request,
                "Slurry readings saved"
            )

            return redirect(

                "piling:step_soil_log",
                pile_pk=pile.pk

            )

        else:

            for i,errors in enumerate(formset.errors):

                if errors:

                    messages.error(

                        request,
                        f"Slurry row {i+1}: {errors}"

                    )

            if formset.non_form_errors():

                messages.error(

                    request,
                    formset.non_form_errors()

                )

    else:

        formset = SlurryFormSet(
            instance=pile,
            prefix=SLURRY_PREFIX

        )

    spec = {

        "viscosity_min": pile.project.viscosity_min_secs,
        "viscosity_max": pile.project.viscosity_max_secs,
        "density_min": pile.project.density_min,
        "density_max": pile.project.density_max,
        "sand_limit": pile.project.sand_content_limit_pct,

    }

    return render(

        request,
        "piling/step_slurry_check.html",

        {

            "formset":formset,
            "pile":pile,
            "spec":spec,
            "slurry_prefix":SLURRY_PREFIX,
            "current_step":"slurry_check",
            "steps":STEPS,
            "step_labels":STEP_LABELS

        }

    )


# ------------------------------------------------------------------ #
# Step 5 — Soil Log                                                    #
# ------------------------------------------------------------------ #
@login_required
def step_soil_log(request,pile_pk):

    pile=get_object_or_404(Pile,pk=pile_pk)

    if request.method=="POST":

        formset=SoilLayerFormSet(

            request.POST,
            instance=pile,
            prefix=SOIL_PREFIX

        )

        if formset.is_valid():

            instances=formset.save(commit=False)

            if hasattr(formset,'deleted_objects'):

                for obj in formset.deleted_objects:

                    obj.delete()

            for i,obj in enumerate(instances,start=1):

                obj.sequence_no=i
                obj.pile=pile
                obj.save()

            formset.save_m2m() 

            messages.success(request,"Soil log saved")

            return redirect(

                "piling:step_concreting",
                pile_pk=pile.pk

            )

        else:

            for i,errors in enumerate(formset.errors):

                if errors:

                    messages.error(

                        request,
                        f"Soil row {i+1}: {errors}"

                    )

            if formset.non_form_errors():

                messages.error(

                    request,
                    formset.non_form_errors()

                )

    else:

        formset=SoilLayerFormSet(

            instance=pile,
            prefix=SOIL_PREFIX

        )

    return render(request,"piling/step_soil_log.html",{

        "formset":formset,
        "pile":pile,
        "soil_prefix":SOIL_PREFIX,
        "current_step":"soil_log",
        "steps":STEPS,
        "step_labels":STEP_LABELS

    })

# ------------------------------------------------------------------ #
# Step 6 — Concreting                                                  #
# ------------------------------------------------------------------ #
@login_required
def step_concreting(request, pile_pk):
    pile = get_object_or_404(
        Pile.objects.select_related("project").prefetch_related("tremie_sequences"),
        pk=pile_pk,
    )

    if request.method == "POST":
        form = ConcretingForm(request.POST, request.FILES, instance=pile)
        if form.is_valid():
            form.save()
            messages.success(request, "Concreting data saved.")
            return redirect("piling:review", pile_pk=pile.pk)
    else:
        form = ConcretingForm(instance=pile)

    return render(request, "piling/step_concreting.html", {
        "form": form,
        "pile": pile,
        "theoretical_volume": pile.theoretical_volume_m3,
        "tremie_total": pile.tremie_total_depth_m,
        "current_step": "concreting",
        "steps": STEPS,
        "step_labels": STEP_LABELS,
    })


# ------------------------------------------------------------------ #
# Review                                                               #
# ------------------------------------------------------------------ #
@login_required
def review(request, pile_pk):
    pile = get_object_or_404(
        Pile.objects.select_related("project").prefetch_related(
            "tremie_sequences", "slurry_checks", "soil_layers"
        ),
        pk=pile_pk,
    )
    return render(request, "piling/review.html", {
        "pile": pile,
        "slurry_checks": pile.slurry_checks.all(),
        "tremie_sequences": pile.tremie_sequences.all(),
        "soil_layers": pile.soil_layers.all(),
        "current_step": "review",
        "steps": STEPS,
        "step_labels": STEP_LABELS,
    })


# ------------------------------------------------------------------ #
# AJAX — live tremie sum                                               #
# ------------------------------------------------------------------ #
@require_POST
@login_required
def api_tremie_sum(request):
    import json, math
    try:
        data = json.loads(request.body)
        lengths = [float(x) for x in data.get("lengths", []) if x]
        diameter = float(data.get("diameter", 0))
        total = round(sum(lengths), 3)
        volume = round(math.pi * (diameter / 2) ** 2 * total, 2) if diameter > 0 else None
        return JsonResponse({"total_depth_m": total, "theoretical_volume_m3": volume})
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        return JsonResponse({"error": str(e)}, status=400)
