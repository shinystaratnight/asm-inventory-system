from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormMixin, FormView
from users.views import AdminLoginRequiredMixin
from .forms import *

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
    

class CustomerView(MasterView):
    template_name = 'master_data/customers.html'
    form_class = CustomerForm


class HallView(MasterView):
    template_name = 'master_data/halls.html'
    form_class = HallForm


class ReceiverView(MasterView):
    template_name = 'master_data/receivers.html'
    form_class = ReceiverForm


class ProductView(MasterView):
    template_name = 'master_data/products.html'
    form_class = ProductForm


class OtherView(MasterView):
    template_name = 'master_data/others.html'
    form_class = OtherForm