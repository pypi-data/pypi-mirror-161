from .models import Ref
from .utils import canonicalize_doi
import django_filters


class RefFilter(django_filters.FilterSet):

    doi = django_filters.CharFilter(
        field_name="doi", label="Publication DOI", method="filter_by_doi"
    )
    bibcode = django_filters.CharFilter(
        field_name="bibcode", label="Publication Bibcode", lookup_expr="exact"
    )
    title = django_filters.CharFilter(
        field_name="title", label="Title", lookup_expr="icontains"
    )
    author = django_filters.CharFilter(
        field_name="authors", label="Author", lookup_expr="icontains"
    )

    def filter_by_doi(self, queryset, name, value):
        return queryset.filter(doi=canonicalize_doi(value))

    class Meta:
        model = Ref
        fields = []
