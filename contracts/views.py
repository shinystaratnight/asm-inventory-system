from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.views.generic.base import TemplateView, View
from django.http import JsonResponse
from django.urls import reverse
from users.views import AdminLoginRequiredMixin
from masterdata.models import (
    Customer, Product, Document, Sender, DocumentFee
)
from .forms import (
    TraderSalesContractForm, TraderPurchasesContractForm, HallSalesContractForm, HallPurchasesContractForm,
    ProductFormSet, DocumentFormSet, DocumentFeeFormSet, MilestoneFormSet, 
    TraderSalesProductSenderForm, TraderSalesDocumentSenderForm, TraderPurchasesProductSenderForm, TraderPurchasesDocumentSenderForm,
)
from .utilities import generate_contract_id, get_shipping_date_label


# List of people in charge for common contract pages
class ContractManagerAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            contract = self.request.POST.get('contract')
            content_type = ContentType.objects.get(model=contract)
            contract_model = content_type.model_class()
            people = contract_model.objects.values('person_in_charge').distinct()
            return JsonResponse({'people': list(people)}, status=200)
        return JsonResponse({'success': False}, status=400)


# Shipping label for trader sales contract page
class ContractShippingLabelAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST.get('data')
            return JsonResponse({'data': get_shipping_date_label(data)}, status=200)
        return JsonResponse({'success': False}, status=400)


class ContractClassNameAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            object_id = self.request.POST.get('object_id')
            class_id = self.request.POST.get('class_id')
            model_name = ContentType.objects.get(id=class_id).model
            url_name = "contract:{}-update".format(model_name)
            url = reverse(url_name, kwargs={'pk': object_id})
            return JsonResponse({'url': url}, status=200)
        return JsonResponse({'success': False}, status=400)


class CheckTaxableAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            id = self.request.POST.get('id')
            document = Document.objects.get(id=id)
            return JsonResponse({'taxable': int(document.taxable)}, status=200)
        return JsonResponse({'success': False}, status=400)

#=============================== Contract Views ======================================#

## Trader Sales contract ##
class TraderSalesValidateAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST
            # Check if contract form is valid
            contract_form = TraderSalesContractForm(data)
            if not contract_form.is_valid():
                return JsonResponse({'success': False}, status=200)
            # If shipping method is receipt, salessenderform validation should be checked
            if contract_form.cleaned_data.get('shipping_method') == 'R':
                product_sender_form = TraderSalesProductSenderForm(self.request.POST)
                document_sender_form = TraderSalesDocumentSenderForm(self.request.POST)
                if product_sender_form.is_valid() and document_sender_form.is_valid():
                    pass
                else:
                    return JsonResponse({'success': False}, status=200)
            # Check the validity of product formset
            product_formset = ProductFormSet(data, prefix='product')
            if not product_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_formset = DocumentFormSet(data, prefix='document')
            if not document_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)


class TraderSalesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/trader_sales.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        contract_form = TraderSalesContractForm(self.request.POST)
        if contract_form.is_valid():
            contract = contract_form.save()
        
        shipping_method = contract_form.cleaned_data.get('shipping_method')
        if shipping_method == 'R':
            product_sender_form = TraderSalesProductSenderForm(self.request.POST, contract_id=contract.id)
            if product_sender_form.is_valid():
                product_sender_form.save()
            document_sender_form = TraderSalesDocumentSenderForm(self.request.POST, contract_id=contract.id)
            if document_sender_form.is_valid():
                document_sender_form.save()
        
        product_formset = ProductFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'TraderSalesContract'},
            prefix='product'
        )
        for form in product_formset.forms:
            if form.is_valid():
                form.save()
        
        document_formset = DocumentFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'TraderSalesContract'},
            prefix='document'
        )
        for form in document_formset.forms:
            if form.is_valid():
                form.save()
        
        return redirect('listing:sales-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_form'] = TraderSalesContractForm()
        context['documents'] = Document.objects.all().values('id', 'name')
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        context['product_sender_form'] = TraderSalesProductSenderForm()
        context['document_sender_form'] = TraderSalesDocumentSenderForm()
        return context
## End of trader sales contract ##


## Trader purchases contract ##
class TraderPurchasesValidateAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST
            # Check if contract form is valid
            contract_form = TraderPurchasesContractForm(data)
            if not contract_form.is_valid():
                return JsonResponse({'success': False}, status=200)
            product_sender_form = TraderPurchasesProductSenderForm(self.request.POST)
            document_sender_form = TraderPurchasesDocumentSenderForm(self.request.POST)
            if product_sender_form.is_valid() and document_sender_form.is_valid():
                pass
            else:
                return JsonResponse({'success': False}, status=200)
            
            # Check the validity of product formset
            product_formset = ProductFormSet(data, prefix='product')
            if not product_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_formset = DocumentFormSet(data, prefix='document')
            if not document_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)


class TraderPurchasesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/trader_purchases.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        contract_form = TraderPurchasesContractForm(self.request.POST)
        if contract_form.is_valid():
            contract = contract_form.save()
        
        product_sender_form = TraderPurchasesProductSenderForm(self.request.POST, contract_id=contract.id)
        if product_sender_form.is_valid():
            product_sender_form.save()
        
        document_sender_form = TraderPurchasesDocumentSenderForm(self.request.POST, contract_id=contract.id)
        if document_sender_form.is_valid():
            document_sender_form.save()
            
        product_formset = ProductFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'TraderPurchasesContract'},
            prefix='product'
        )
        for form in product_formset.forms:
            if form.is_valid():
                form.save()

        document_formset = DocumentFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'TraderPurchasesContract'},
            prefix='document'
        )
        for form in document_formset.forms:
            if form.is_valid():
                form.save()
        
        return redirect('listing:purchases-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_form'] = TraderPurchasesContractForm()
        context['documents'] = Document.objects.all().values('id', 'name')
        context['senders'] = Sender.objects.all().values('id', 'name')
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        context['product_sender_form'] = TraderPurchasesProductSenderForm()
        context['document_sender_form'] = TraderPurchasesDocumentSenderForm()
        return context
# End of trader purchases form


## Hall sales contract
class HallSalesValidateAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST
            contract_form = HallSalesContractForm(data)
            if not contract_form.is_valid():
                return JsonResponse({'success': False}, status=200)
            product_formset = ProductFormSet(data, prefix='product')
            if not product_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_formset = DocumentFormSet(data, prefix='document')
            if not document_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_fee_formset = DocumentFeeFormSet(data, prefix='document_fee')
            if not document_fee_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            milestone_formset = MilestoneFormSet(data, prefix='milestone')
            if not milestone_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)


class HallSalesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/hall_sales.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

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
        
        return redirect('listing:sales-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_form'] = HallSalesContractForm()
        context['documents'] = Document.objects.all().values('id', 'name')
        document_fee_lambda = lambda df: {'id': df.id, 'name': df.get_type_display()}
        document_fees = [document_fee_lambda(document_fee) for document_fee in DocumentFee.objects.all()]
        context['document_fees'] = document_fees
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        context['documentfeeformset'] = DocumentFeeFormSet(prefix='document_fee')
        context['milestoneformset'] = MilestoneFormSet(prefix='milestone')
        return context
# End of hall sales contract


# Hall purchases contract
class HallPurchasesValidateAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            data = self.request.POST
            contract_form = HallPurchasesContractForm(data)
            if not contract_form.is_valid():
                return JsonResponse({'success': False}, status=200)
            product_formset = ProductFormSet(data, prefix='product')
            if not product_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_formset = DocumentFormSet(data, prefix='document')
            if not document_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            document_fee_formset = DocumentFeeFormSet(data, prefix='document_fee')
            if not document_fee_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            milestone_formset = MilestoneFormSet(data, prefix='milestone')
            if not milestone_formset.is_valid():
                return JsonResponse({'success': False}, status=200)
            return JsonResponse({'success': True}, status=200)
        return JsonResponse({'success': False}, status=400)


class HallPurchasesContractView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'contracts/hall_purchases.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        contract_form = HallPurchasesContractForm(self.request.POST)
        if contract_form.is_valid():
            contract = contract_form.save()
            
        product_formset = ProductFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallPurchasesContract'},
            prefix='product'
        )
        for form in product_formset.forms:
            if form.is_valid():
                form.save()

        document_formset = DocumentFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallPurchasesContract'},
            prefix='document'
        )
        for form in document_formset.forms:
            if form.is_valid():
                form.save()
        
        document_fee_formset = DocumentFeeFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallPurchasesContract'},
            prefix='document_fee'
        )
        for form in document_fee_formset.forms:
            if form.is_valid():
                form.save()
        
        milestone_formset = MilestoneFormSet(
            self.request.POST,
            form_kwargs={'contract_id': contract.id, 'contract_class': 'HallPurchasesContract'},
            prefix='milestone'
        )
        for form in milestone_formset.forms:
            if form.is_valid():
                if form.cleaned_data.get('date') and form.cleaned_data.get('amount'):
                    form.save()
        
        return redirect('listing:purchases-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_form'] = HallPurchasesContractForm()
        context['documents'] = Document.objects.all().values('id', 'name')
        document_fee_lambda = lambda df: {'id': df.id, 'name': df.get_type_display()}
        document_fees = [document_fee_lambda(document_fee) for document_fee in DocumentFee.objects.all()]
        context['document_fees'] = document_fees
        context['productformset'] = ProductFormSet(prefix='product')
        context['documentformset'] = DocumentFormSet(prefix='document')
        context['documentfeeformset'] = DocumentFeeFormSet(prefix='document_fee')
        context['milestoneformset'] = MilestoneFormSet(prefix='milestone')
        return context
# End of hall purchases contract
