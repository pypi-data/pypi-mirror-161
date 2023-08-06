from django.urls import path
from autoreduce_frontend.autoreduce_webapp.view_utils import login_and_uows_valid

from autoreduce_frontend.generate_token import views

app_name = "token"

urlpatterns = [
    path("", login_and_uows_valid(views.ShowToken.as_view()), name="list"),
    path("generate", login_and_uows_valid(views.GenerateTokenFormView.as_view()), name="generate"),
    path("delete/<str:pk>", login_and_uows_valid(views.DeleteToken.as_view()), name="delete"),
]
