from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

# SPA for react
index = never_cache(TemplateView.as_view(template_name="index.html"))
