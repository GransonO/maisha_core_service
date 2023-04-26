from django.urls import path

from .MaishaAuthenticate import Register, Verify, ResetPass, Login

urlpatterns = [
    # Doctors
    path("doc/register",
         Register.as_view(),
         name="Doctor Register"
         ),
    path("doc/login",
         Login.as_view(),
         name="Doctor Login"
         ),
    path("doc/reset",
         ResetPass.as_view(),
         name="Doctor ResetPass"
         ),
    path("doc/verify",
         Verify.as_view(),
         name="Doctor verify"
         ),
    # Patients

    path("register",
         Register.as_view(),
         name="Patients Register"
         ),

    path("login",
         Login.as_view(),
         name="Patients Login"
         ),

    path("reset",
         ResetPass.as_view(),
         name="Patients ResetPass"
         ),

    path("verify",
         Verify.as_view(),
         name="Patient verify"
         ),
]
