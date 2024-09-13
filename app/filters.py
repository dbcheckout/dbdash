import django_filters
from django import forms
from django.forms import SelectDateWidget
import datetime


from produto.models import Grupos, Tipos, Tamanhos, Produtos


        
class FiltroForm(forms.Form):    
    dtini = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data Inicial")
    dtfim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data Final")

    grupo = forms.ModelChoiceField(
        queryset=Grupos.objects.all(),
        label="Grupo",
        required=False
    )
    
    tipo = forms.ModelChoiceField(
        queryset=Tipos.objects.all(),
        label="Tipo",
        required=False
    )