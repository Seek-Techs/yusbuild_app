from django.urls import path
from . import views

app_name = "piling"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Pile detail (read-only)
    path("pile/<int:pile_pk>/", views.pile_detail, name="pile_detail"),

    # Wizard — new pile (no pile_pk yet on step 1)
    path("pile/new/", views.step_pile_info, name="step_pile_info_new"),

    # Wizard — edit existing pile, step by step
    path("pile/<int:pile_pk>/step/info/", views.step_pile_info, name="step_pile_info"),
    path("pile/<int:pile_pk>/step/drilling/", views.step_drilling_times, name="step_drilling_times"),
    path("pile/<int:pile_pk>/step/tremie/", views.step_tremie_entry, name="step_tremie_entry"),
    path("pile/<int:pile_pk>/step/slurry/", views.step_slurry_check, name="step_slurry_check"),
    path("pile/<int:pile_pk>/step/soil/", views.step_soil_log, name="step_soil_log"),
    path("pile/<int:pile_pk>/step/concrete/", views.step_concreting, name="step_concreting"),
    path("pile/<int:pile_pk>/review/", views.review, name="review"),

    # AJAX
    path("api/tremie-sum/", views.api_tremie_sum, name="api_tremie_sum"),
]
