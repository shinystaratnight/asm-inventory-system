import unicodecsv as csv
from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from django.utils.translation import gettext as _
from users.views import AdminLoginRequiredMixin
from .models import *
from .forms import (
    TraderSalesContractForm, TraderPurchasesContractForm, HallSalesContractForm, HallPurchasesContractForm,
    ProductFormSet, DocumentFormSet, DocumentFeeFormSet, MilestoneFormSet, 
    TraderSalesSenderForm, TraderPurchasesSenderForm,
    ProductForm,
)
from .utilities import generate_contract_id, ordinal


class TraderSalesContractUpdateView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/trader_sales_update.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        contract_form = TraderSalesContractForm(self.request.POST)
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = kwargs.get('pk')
        contract = TraderSalesContract.objects.get(id=id)
        products = contract.products
        context['contract'] = contract
        
        context['documents'] = Document.objects.all().values('id', 'name')
        products = contract.products.all()
        dataset = []
        for product in products:
            data = {
                'id': product.product.id,
                'type': product.type,
                'quantity': product.quantity,
                'price': product.price
            }
            product_form = ProductForm(data)
            if product_form.is_valid():
                dataset.append(data)

        context['productformset'] = ProductFormSet(initial=dataset, prefix='product')
        context['senders'] = Sender.objects.all().values('id', 'name')
        
        product_sender = contract.senders.filter(type='P').first()
        product_sender_form = TraderSalesSenderForm({
            'sender_id': product_sender.sender_id,
            'expected_arrival_date': product_sender.expected_arrival_date
        })
        if product_sender_form.is_valid():
            context['product_sender'] = product_sender

        return context


class HallSalesContractUpdateView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/hall_sales_update.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
    def get_object(self, **kwargs):
        id = kwargs.get('pk')
        return HallSalesContract.objects.get(id=id)

    def post(self, request, *args, **kwargs):
        contract_form = HallSalesContractForm(self.request.POST)
        if contract_form.is_valid():
            contract = contract_form.save()
            
        product_formset = ProductFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallSalesContract'},
            prefix='product'
        )
        for form in product_formset.forms:
            if form.is_valid():
                form.save()

        document_formset = DocumentFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallSalesContract'},
            prefix='document'
        )
        for form in document_formset.forms:
            if form.is_valid():
                form.save()
        
        document_fee_formset = DocumentFeeFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallSalesContract'},
            prefix='document_fee'
        )
        for form in document_fee_formset.forms:
            if form.is_valid():
                form.save()
        
        milestone_formset = MilestoneFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallSalesContract'},
            prefix='milestone'
        )
        for form in milestone_formset.forms:
            if form.is_valid():
                if form.cleaned_data.get('date') and form.cleaned_data.get('amount'):
                    form.save()
        
        # return render(request, self.template_name, self.get_context_data(**kwargs))
        return redirect('list:sales')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contract = self.get_object(**kwargs)
        context['contract'] = contract
        context['documents'] = Document.objects.all().values('id', 'name')
        document_fee_lambda = lambda df: {'id': df.id, 'name': df.get_type_display()}
        document_fees = [document_fee_lambda(document_fee) for document_fee in DocumentFee.objects.all()]
        context['document_fees'] = document_fees
        products = contract.products.all()
        dataset = []
        for product in products:
            data = {
                'id': product.product.id,
                'type': product.type,
                'quantity': product.quantity,
                'price': product.price
            }
            product_form = ProductForm(data)
            if product_form.is_valid():
                dataset.append(data)


        context['productformset'] = ProductFormSet(initial=dataset, prefix='product')
        # documents = contract.documents.all()
        # context['documentformset'] = DocumentFormSet(documents, prefix='document')
        # document_fees = contract.document_fees
        # context['documentfeeformset'] = DocumentFeeFormSet(document_fees, prefix='document_fee')
        # milestones = contract.milestones.all()
        # extra = 5 - milestones.count()
        # MilestoneEditFormSet = formset_factory(MilestoneForm, formset=MilestoneValidationFormSet, extra=extra)
        # context['milestoneformset'] = MilestoneEditFormSet(milestones, prefix='milestone')
        return context
