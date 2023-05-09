from django.urls import path

from .MaishaAuthenticate import Register, Verify, ResetPass, Login

urlpatterns = [

    path("register",
         Register.as_view(),
         name="Register"
         ),

    path("login",
         Login.as_view(),
         name="Login"
         ),

    path("reset",
         ResetPass.as_view(),
         name="Reset Pass"
         ),

    path("verify",
         Verify.as_view(),
         name="verify"
         ),
]
