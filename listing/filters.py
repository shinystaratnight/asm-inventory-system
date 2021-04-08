import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from contracts.models import *


class SalesFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ContractProduct
        fields = ('id',)

