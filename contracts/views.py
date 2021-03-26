import time
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView, View
from django.http import JsonResponse
from users.views import AdminLoginRequiredMixin
from masterdata.models import Document
from .models import *
from .forms import *


def generate_contract_id():
    return int(time.time())


class TraderSalesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/trader_sales.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        product_formset = ProductFormSet(self.request.POST)
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_id'] = generate_contract_id()
        context['documents'] = Document.objects.all().values('name')
        context['productformset'] = ProductFormSet()
        return context


class TraderSalesValidatorView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            print("Ajax")
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)


@login_required(login_url='login')
def trader_purchases(request):
    context = {}
    return render(request, 'contracts/trader_purchases.html', context)

@login_required(login_url='login')
def hall_sales(request):
    context = {}
    return render(request, 'contracts/hall_sales.html', context)

@login_required(login_url='login')
def hall_purchases(request):
    context = {}
    return render(request, 'contracts/hall_purchases.html', context)

