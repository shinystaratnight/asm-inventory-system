from django.forms import ModelForm
from .models import Customer, Hall, Sender, Product, Document


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class HallForm(ModelForm):
    class Meta:
        model = Hall
        fields = '__all__'


class SenderForm(ModelForm):
    class Meta:
        model = Sender
        fields = '__all__'


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = '__all__'