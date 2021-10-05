from django.urls import path
from .doctors_views import (
    Register as DocRegister,
    Login as DocLogin,
    ResetPass as DocReset,
    DoctorVerify)
from .patient_views import (
    Register as PatRegister,
    ResetPass as PatReset,
    PatientVerify as PatVerify,
    Login as PatLogin
)

urlpatterns = [
    # Doctors
    path("doc/register",
         DocRegister.as_view(),
         name="Doctor Register"
         ),
    path("doc/login",
         DocLogin.as_view(),
         name="Doctor Login"
         ),
    path("doc/reset",
         DocReset.as_view(),
         name="Doctor ResetPass"
         ),
    path("doc/verify",
         DoctorVerify.as_view(),
         name="Doctor verify"
         ),
    # Patients

    path("register",
         PatRegister.as_view(),
         name="Patients Register"
         ),

    path("login",
         PatLogin.as_view(),
         name="Patients Login"
         ),

    path("reset",
         PatReset.as_view(),
         name="Patients ResetPass"
         ),

    path("verify",
         PatVerify.as_view(),
         name="Patient verify"
         ),
]
