from django.urls import path
from .doctors_views import (
     Profiles as DocProfiles,  ProfilesAllView as DocProfilesAllView,
     ProfileSpecificView as DocProfileSpecificView, CodeVerify,
     SearchDoctor, SpecialityView, SpecialitySearch, DoctorValidation
     )
from .patients_views import (
     Profiles,  ProfilesAllView, Allergies, RecurrentIssuesView,
     ProfileSpecificView, AllergiesSpecificView, RecurrentIssuesSpecificView,
     RelativeSearch, DependantsView, DependantSpecificView, NotifierSpecificView,
     NotifierView
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
         DocProfileSpecificView.as_view(),
         name="specific profiles"
         ),

    path('doc/all/',
         DocProfilesAllView.as_view(),
         name="all profiles"
         ),

    path('doc/search/',
         SearchDoctor.as_view(),
         name="Search Doctor"
         ),

    path('doc/speciality/',
         SpecialityView.as_view(),
         name="Doctor SpecialityView"
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
         ProfileSpecificView.as_view(),
         name="specific profiles"
         ),

    path('all/',
         ProfilesAllView.as_view(),
         name="all profiles"
         ),

    path('allergies/',
         Allergies.as_view(),
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
