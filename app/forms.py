from datetime import datetime, timedelta
from django import forms

class FiltroDashboardForm(forms.Form):
    INTERVAL_CHOICES = [
        ('data_definida', 'Especifique a data'),        
        ('hoje', 'Hoje'),
        ('ontem', 'Ontem'),
        ('ultimo_final_semana', 'Último Final de Semana'),
        ('mes_passado', 'Mês Passado'),        
        ('ano_todo', 'Ano Todo'),
        ('mes_corrente', 'Mês Corrente'),
        ('ultimos_7_dias', 'Últimos 7 Dias'),
        ('ultimos_15_dias', 'Últimos 15 Dias'),
    ]
    
    intervalo = forms.ChoiceField(
        label="Intervalo",
        choices=INTERVAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    data_inicial = forms.DateField(
        label="Data Inicial",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    data_final = forms.DateField(
        label="Data Final",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_initial_dates()

    def set_initial_dates(self):
        now = datetime.now()
        intervalo = self.data.get('intervalo')
        
        if intervalo == 'mes_corrente' or intervalo is None:
            primeiro_dia_mes = now.replace(day=1)
            ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            self.fields['data_inicial'].initial = primeiro_dia_mes.date()
            self.fields['data_final'].initial = ultimo_dia_mes.date()
        elif intervalo == 'ultimos_7_dias':
            self.fields['data_inicial'].initial = now.date() - timedelta(days=7)
            self.fields['data_final'].initial = now.date()
        elif intervalo == 'ultimos_15_dias':
            self.fields['data_inicial'].initial = now.date() - timedelta(days=15)
            self.fields['data_final'].initial = now.date()
        elif intervalo == 'ano_todo':
            self.fields['data_inicial'].initial = now.replace(month=1, day=1).date()
            self.fields['data_final'].initial = now.replace(month=12, day=31).date()
        elif intervalo == 'hoje':
            self.fields['data_inicial'].initial = now.date()
            self.fields['data_final'].initial = now.date()
        elif intervalo == 'ontem':
            self.fields['data_inicial'].initial = (now - timedelta(days=1)).date()
            self.fields['data_final'].initial = (now - timedelta(days=1)).date()
        elif intervalo == 'ultimo_final_semana':
            data_final = now - timedelta(days=now.weekday() + 1)  # Último domingo
            data_inicial = data_final - timedelta(days=6)  # Último final de semana começa no sábado
            self.fields['data_inicial'].initial = data_inicial.date()
            self.fields['data_final'].initial = data_final.date()
        elif intervalo == 'mes_passado':
            primeiro_dia_mes_passado = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
            ultimo_dia_mes_passado = now.replace(day=1) - timedelta(days=1)
            self.fields['data_inicial'].initial = primeiro_dia_mes_passado.date()
            self.fields['data_final'].initial = ultimo_dia_mes_passado.date()

    def clean(self):
        cleaned_data = super().clean()
        intervalo = cleaned_data.get('intervalo')
        
        now = datetime.now()
        if intervalo == 'mes_corrente':
            primeiro_dia_mes = now.replace(day=1)
            ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            self.fields['data_inicial'].initial = primeiro_dia_mes.date()
            self.fields['data_final'].initial = ultimo_dia_mes.date()
        elif intervalo == 'ultimos_7_dias':
            self.fields['data_inicial'].initial = now.date() - timedelta(days=7)
            self.fields['data_final'].initial = now.date()
        elif intervalo == 'ultimos_15_dias':
            self.fields['data_inicial'].initial = now.date() - timedelta(days=15)
            self.fields['data_final'].initial = now.date()
        elif intervalo == 'ano_todo':
            self.fields['data_inicial'].initial = now.replace(month=1, day=1).date()
            self.fields['data_final'].initial = now.replace(month=12, day=31).date()
        elif intervalo == 'hoje':
            self.fields['data_inicial'].initial = now.date()
            self.fields['data_final'].initial = now.date()
        elif intervalo == 'ontem':
            self.fields['data_inicial'].initial = (now - timedelta(days=1)).date()
            self.fields['data_final'].initial = (now - timedelta(days=1)).date()
        elif intervalo == 'ultimo_final_semana':
            data_final = now - timedelta(days=now.weekday() + 1)  # Último domingo
            data_inicial = data_final - timedelta(days=6)  # Último final de semana começa no sábado
            self.fields['data_inicial'].initial = data_inicial.date()
            self.fields['data_final'].initial = data_final.date()
        elif intervalo == 'mes_passado':
            primeiro_dia_mes_passado = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
            ultimo_dia_mes_passado = now.replace(day=1) - timedelta(days=1)
            self.fields['data_inicial'].initial = primeiro_dia_mes_passado.date()
            self.fields['data_final'].initial = ultimo_dia_mes_passado.date()
        
        return cleaned_data
