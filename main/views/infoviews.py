from django.shortcuts import render
from django.views.generic import TemplateView

# TODO This is a normal template view, no?

class StartView(TemplateView):
    template_name = "info/start.html"
