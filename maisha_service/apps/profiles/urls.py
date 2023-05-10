from django.urls import path
from .views import (
    Profiles as DocProfiles, CodeVerify,
    SearchDoctor, SpecialityView, SpecialitySearch, DoctorValidation, DoctorProfileSpecificView, DoctorAllProfileView,
    Profiles, PatientAllProfileView, PatientProfileSpecificView, AllergiesView, AllergiesSpecificView,
    RecurrentIssuesView, RecurrentIssuesSpecificView, DependantsView, DependantSpecificView, NotifierView,
    NotifierSpecificView, RelativeSearch, Specialities, DoctorActiveProfiles
)


urlpatterns = [

    path('code/',
         CodeVerify.as_view(),
         name="profiles"
         ),

    # doctors
    path('doc/',
         DocProfiles.as_view(),
         name="profiles"
         ),

    path('doc/<userId>',
         DoctorProfileSpecificView.as_view(),
         name="specific profiles"
         ),

    path('doc/all/',
         DoctorAllProfileView.as_view(),
         name="all profiles"
         ),

    path('doc/active/',
         DoctorActiveProfiles.as_view(),
         name="all Active doctor profiles"
         ),

    path('doc/search/',
         SearchDoctor.as_view(),
         name="Search Doctor"
         ),

    path('doc/speciality/',
         SpecialityView.as_view(),
         name="Doctor SpecialityView"
         ),

    path('doc/speciality/all/',
         Specialities.as_view(),
         name="Doctor All Specialities"
         ),

    path('doc/speciality/search/',
         SpecialitySearch.as_view(),
         name="Doctor Speciality Search"
         ),

    path('doc/activation/',
         DoctorValidation.as_view(),
         name="Doctor Validation"
         ),

    # Patients
    path('',
         Profiles.as_view(),
         name="profiles"
         ),

    path('<userId>',
         PatientProfileSpecificView.as_view(),
         name="specific profiles"
         ),

    path('all/',
         PatientAllProfileView.as_view(),
         name="all profiles"
         ),

    path('allergies/',
         AllergiesView.as_view(),
         name="Allergies"
         ),

    path('allergies/<patient_id>',
         AllergiesSpecificView.as_view(),
         name="Specific Allergies"
         ),

    path('recurrent/',
         RecurrentIssuesView.as_view(),
         name="RecurrentIssues View"
         ),

    path('recurrent/<patient_id>',
         RecurrentIssuesSpecificView.as_view(),
         name="Specific Recurrent Issues"
         ),

    path('dependants/',
         DependantsView.as_view(),
         name="Dependants View"
         ),

    path('dependants/<patient_id>',
         DependantSpecificView.as_view(),
         name="Specific Dependants"
         ),

    path('notifiers/',
         NotifierView.as_view(),
         name="Notifier View"
         ),

    path('notifiers/<patient_id>',
         NotifierSpecificView.as_view(),
         name="Specific Notifiers"
         ),

    path('relatives/search/',
         RelativeSearch.as_view(),
         name="Relative Search"
         )
]
