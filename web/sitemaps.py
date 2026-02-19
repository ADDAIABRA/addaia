from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticSitemap(Sitemap):
    """
    Sitemap for static pages.
    """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['pagina_inicial', 'politica_privacidade', 'termos_condicoes']

    def location(self, item):
        return reverse(item)
