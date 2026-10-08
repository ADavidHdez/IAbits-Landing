from . import seo


def canonical(request):
    """Expone `canonical_url` a todas las plantillas (lo usa base.html)."""
    return {'canonical_url': seo.canonical_url(request)}
