from django.urls import path

from . import views

app_name = "Interview"

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "interview/<int:interview_id>",
        views.interview_details,
        name="interview_details",
    ),
    path(
        "interview/<int:interview_id>/edit", views.edit_interview, name="edit_interview"
    ),
    path("interview/create", views.create_interview, name="create_interview"),
    path("interview/list", views.interview_list, name="interview_list"),
]
