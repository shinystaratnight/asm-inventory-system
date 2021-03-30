import django_filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import Customer


class CustomerFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(method='filter_by_keyword')

    class Meta:
        model = Customer
        fields = '__all__'
        
    def filter_by_keyword(self, queryset, name, value):
        queryset = queryset.filter(
            Q(name__icontains=value) |
            Q(frigana__icontains=value) |
            Q(tel__icontains=value) |
            Q(fax__icontains=value) |
            Q(address__icontains=value) |
            Q(csv__icontains=value)
        )
        return queryset