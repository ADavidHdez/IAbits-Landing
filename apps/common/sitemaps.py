from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Páginas públicas indexables.

    Sin django.contrib.sites, la vista del sitemap usa RequestSite: el dominio
    y el esquema salen de la propia petición.
    """

    def items(self):
        return ['home:home', 'home:contact', 'landing:home']

    def location(self, item):
        return reverse(item)


SITEMAPS = {'static': StaticViewSitemap}
