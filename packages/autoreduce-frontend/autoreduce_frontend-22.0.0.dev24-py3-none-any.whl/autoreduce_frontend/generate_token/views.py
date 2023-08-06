from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import DeleteView, FormView
from rest_framework.authtoken.models import Token

from autoreduce_frontend.autoreduce_webapp.view_utils import get_notifications
from autoreduce_frontend.generate_token.forms import GenerateTokenForm


class GenerateTokenFormView(FormView):
    template_name = "generate_token.html"
    form_class = GenerateTokenForm
    success_url = reverse_lazy("token:list")

    def form_valid(self, form) -> HttpResponse:
        _, created = Token.objects.get_or_create(user=form.cleaned_data["user"])
        if not created:
            self.request.session["error_message"] = "User token already exists. You can only have 1 token per user."
        return HttpResponseRedirect(self.get_success_url())


class ShowToken(ListView):
    template_name = "show_tokens.html"
    model = Token
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notifications"] = get_notifications(self.request)
        error_message = self.request.session.pop("error_message", "")
        context['error_message'] = error_message
        return context


class DeleteToken(DeleteView):
    template_name = "delete_token.html"
    model = Token
    success_url = reverse_lazy("token:list")
