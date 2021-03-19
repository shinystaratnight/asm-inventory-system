from django.shortcuts import render
from django.views.generic import TemplateView
from masterdata.models import Customer
from masterdata.forms import CustomerForm
from users.views import AdminLoginRequiredMixin

class CustomerView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'master_data/customer.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        form = CustomerForm(request.data)
        if form.is_valid():
            form.save()
        return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        return context
