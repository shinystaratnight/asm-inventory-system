from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormMixin, FormView
from django.http import JsonResponse
from django.db.models import Q
from users.views import AdminLoginRequiredMixin
from .forms import *
from .filters import *
from .models import Customer, Receiver

class MasterView(AdminLoginRequiredMixin, TemplateView, FormMixin):
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            form.save()
        return render(request, self.template_name, self.get_context_data(**kwargs))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.form_class.Meta.model
        context['master_data'] = model.objects.all()
        return context
    

class CustomerView(ListView):
    template_name = 'master_data/customers.html'
    form_class = CustomerForm
    queryset = Customer.objects.all()
    context_object_name = 'master_data'
    paginate_by = 10
    
    def get_queryset(self):
        return CustomerFilter(self.request.GET, queryset=self.queryset).qs.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer_filter'] = CustomerFilter(self.request.GET)
        return context


class HallView(MasterView):
    template_name = 'master_data/halls.html'
    form_class = HallForm


class ReceiverView(MasterView):
    template_name = 'master_data/receivers.html'
    form_class = ReceiverForm


class ProductView(MasterView):
    template_name = 'master_data/products.html'
    form_class = ProductForm


class DocumentView(MasterView):
    template_name = 'master_data/documents.html'
    form_class = DocumentForm


class CustomerSearchAjaxView(AdminLoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if self.request.method == 'GET' and self.request.is_ajax():
            search = self.request.GET.get('q')
            page = int(self.request.GET.get('page', 1))
            start = 30 * (page - 1)
            end = 30 * page
            customer_qs = Customer.objects.filter(
                Q(name__icontains=search) |
                Q(frigana__icontains=search) |
                Q(tel__icontains=search) |
                Q(fax__icontains=search)
            )
            total_count = customer_qs.count()
            customer_qs = customer_qs.order_by('id')[start:end].values('id', 'name', 'frigana', 'tel', 'fax', 'postal_code', 'address')
            customers = list(customer_qs)
            return JsonResponse({"customers": customers, "total_count": total_count}, safe=False, status=200)
        return JsonResponse({'success': False}, status=400)


class HallSearchAjaxView(AdminLoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if self.request.method == 'GET' and self.request.is_ajax():
            search = self.request.GET.get('q')
            page = int(self.request.GET.get('page', 1))
            start = 30 * (page - 1)
            end = 30 * page
            hall_qs = Hall.objects.filter(
                Q(name__icontains=search) |
                Q(frigana__icontains=search) |
                Q(tel__icontains=search) |
                Q(fax__icontains=search)
            )
            total_count = hall_qs.count()
            hall_qs = hall_qs.order_by('id')[start:end].values('id', 'name', 'frigana', 'tel', 'fax', 'postal_code', 'address')
            halls = list(hall_qs)
            return JsonResponse({"halls": halls, "total_count": total_count}, safe=False, status=200)
        return JsonResponse({'success': False}, status=400)


class ProductSearchAjaxView(AdminLoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            search = self.request.GET.get('q')
            page = int(self.request.GET.get('page', 1))
            start = 30 * (page - 1)
            end = 30 * page
            product_qs = Product.objects.filter(name__icontains=search)
            total_count = product_qs.count()
            product_qs = product_qs.order_by('id')[start:end].values('id', 'name')
            products = list(product_qs)
            return JsonResponse({"products": products, "total_count": total_count}, safe=False, status=200)
        return JsonResponse({'success': False}, status=400)


class ReceiverDetailAjaxView(AdminLoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if self.request.method == 'GET' and self.request.is_ajax():
            id = self.request.GET.get('id')
            receiver = Receiver.objects.get(id=id)
            return JsonResponse(
                {'address': receiver.address, 'tel': receiver.tel, 'fax': receiver.fax},
                status=200
            )
        return JsonResponse({'success': False}, status=400)
