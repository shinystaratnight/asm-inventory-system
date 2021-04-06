from django.shortcuts import render, redirect
from django.views.generic.base import View, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormMixin, FormView, CreateView
from django.http import JsonResponse
from django.db.models import Q
from users.views import AdminLoginRequiredMixin
from .forms import *
from .filters import *
from .models import *


class CustomerView(AdminLoginRequiredMixin, ListView):
    template_name = 'master_data/customers.html'
    queryset = Customer.objects.all()
    context_object_name = 'master_data'
    paginate_by = 10
    
    def get_queryset(self):
        return CustomerFilter(self.request.GET, queryset=self.queryset).qs.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer_filter'] = CustomerFilter(self.request.GET)
        return context
    
    def post(self, request, *args, **kwargs):
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('masterdata:customer')


class HallView(AdminLoginRequiredMixin, ListView):
    template_name = 'master_data/halls.html'
    queryset = Hall.objects.all()
    context_object_name = 'master_data'
    paginate_by = 10
    
    def get_queryset(self):
        return HallFilter(self.request.GET, queryset=self.queryset).qs.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hall_filter'] = HallFilter(self.request.GET)
        return context
    
    def post(self, request, *args, **kwargs):
        form = HallForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('masterdata:hall')


class SenderView(AdminLoginRequiredMixin, ListView):
    template_name = 'master_data/senders.html'
    queryset = Sender.objects.all()
    context_object_name = 'master_data'
    paginate_by = 10
    
    def get_queryset(self):
        return SenderFilter(self.request.GET, queryset=self.queryset).qs.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sender_filter'] = SenderFilter(self.request.GET)
        return context
    
    def post(self, request, *args, **kwargs):
        form = SenderForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('masterdata:sender')


class ProductView(AdminLoginRequiredMixin, ListView):
    template_name = 'master_data/products.html'
    queryset = Product.objects.all()
    context_object_name = 'master_data'
    paginate_by = 10
    
    def get_queryset(self):
        return ProductFilter(self.request.GET, queryset=self.queryset).qs.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_filter'] = ProductFilter(self.request.GET)
        return context
    
    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('masterdata:product')


class DocumentView(AdminLoginRequiredMixin, ListView):
    template_name = 'master_data/documents.html'
    queryset = Document.objects.all()
    context_object_name = 'master_data'
    
    def post(self, request, *args, **kwargs):
        form = DocumentForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('masterdata:document')


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
            hall_qs = hall_qs.order_by('id')[start:end].values('id', 'name', 'frigana', 'tel', 'fax', 'address')
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


class SenderDetailAjaxView(AdminLoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.is_ajax():
            id = self.request.POST.get('id')
            sender = Sender.objects.get(id=id)
            return JsonResponse(
                {'address': sender.address, 'tel': sender.tel, 'fax': sender.fax},
                status=200
            )
        return JsonResponse({'success': False}, status=400)
