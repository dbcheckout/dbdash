import json
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import date, timedelta
#from ai.models import AIResult
from . import metrics
from .forms import FiltroDashboardForm


@login_required(login_url='login')
def home(request):
    form = FiltroDashboardForm(request.GET or None)
    pedidos_metrics          = {}
    pedidos_sal_metrics      = {}
    pedidos_exp_metrics      = {}
    pedidos_del_metrics      = {}
    pedidos_tog_metrics      = {}
    atendimentos_metrics     = {}
    venda_grupo_metrics      = {}
    venda_pgtos_metrics      = {}
    apuracao_caixa_metrics   = {}
    apuracao_icms_metrics    = {}
    venda_diaria_metrics     = {}
    fluxo_financeiro_metrics = {}
    concilia_recebiveis_metrics = {}
    movimento_caixa_metrics     = {}
    venda_bairro_metrics        = {}
    venda_entregador_metrics    = {}    
    venda_atendente_metrics     = {}    
    venda_combo_metrics         = {}    
    venda_desconto_metrics      = {} 

    dem_fluxoproduto_metrics    = {} 
    

    kpi_delivery_metrics        = {}

    data_inicial = None  # Definir um valor padrão
    data_final   = None  # Definir para data_final também, se necessário



    if form.is_valid():
        intervalo    = form.cleaned_data.get('intervalo')
        data_inicial = form.cleaned_data.get('data_inicial')
        data_final   = form.cleaned_data.get('data_final')


        # Imprimir valores recebidos
        print("Intervalo:", intervalo)
        print("Data inicial (antes da lógica):", data_inicial)
        print("Data final (antes da lógica):", data_final)

        # Definindo o intervalo de datas com base no formulário
        if intervalo == 'mes_corrente':
            now = timezone.now()
            data_inicial = now.replace(day=1).date()
            ultimo_dia_mes = (now.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            data_final = ultimo_dia_mes
        elif intervalo == 'ultimos_7_dias':
            data_inicial = timezone.now().date() - timedelta(days=7)
            data_final = timezone.now().date()
        elif intervalo == 'ultimos_15_dias':
            data_inicial = timezone.now().date() - timedelta(days=15)
            data_final = timezone.now().date()
        elif intervalo == 'ano_todo':
            now = timezone.now()
            data_inicial = now.replace(month=1, day=1).date()
            data_final = now.replace(month=12, day=31).date()
        else:
            # Caso não haja intervalo definido, use as datas fornecidas no formulário
            if data_inicial and data_final:
                try:
                    data_inicial = form.cleaned_data.get('data_inicial')
                    data_final   = form.cleaned_data.get('data_final')
                except ValueError:
                    # Em caso de erro na conversão, defina as datas como None
                    data_inicial = None
                    data_final = None


        # Imprimir valores após ajuste
        print("Data inicial (após lógica):", data_inicial)
        print("Data final (após lógica):", data_final)


        # Filtro de ano e mês
        if data_inicial and data_final:
            pedidos_metrics             = metrics.get_pedidos_metrics(data_inicial, data_final)
            pedidos_sal_metrics         = metrics.get_pedidos_ori_metrics(data_inicial, data_final,'salao')
            pedidos_exp_metrics         = metrics.get_pedidos_ori_metrics(data_inicial, data_final,'express')
            pedidos_del_metrics         = metrics.get_pedidos_ori_metrics(data_inicial, data_final,'delivery')
            pedidos_tog_metrics         = metrics.get_pedidos_ori_metrics(data_inicial, data_final,'togo')
            atendimentos_metrics        = metrics.get_consulta_vendas_atendimento(data_inicial, data_final)
            venda_grupo_metrics         = metrics.get_consulta_vendas_grupo(data_inicial, data_final)
            venda_pgtos_metrics         = metrics.get_consulta_formas_pagamento(data_inicial, data_final)
            apuracao_caixa_metrics      = metrics.get_apuracao_caixa(data_inicial, data_final)
            apuracao_icms_metrics       = metrics.get_apuracao_icms(data_inicial, data_final)
            venda_diaria_metrics        = metrics.get_media_diaria_venda(data_inicial, data_final)
            fluxo_financeiro_metrics    = metrics.get_fluxo_financeiro(data_inicial, data_final)
            concilia_recebiveis_metrics = metrics.get_conciliacao_recebiveis(data_inicial, data_final)
            movimento_caixa_metrics     = metrics.get_movimento_caixa(data_inicial, data_final)
            venda_bairro_metrics        = metrics.get_venda_bairro(data_inicial, data_final)
            venda_entregador_metrics    = metrics.get_venda_entregador(data_inicial, data_final)
            venda_atendente_metrics     = metrics.get_venda_atendente(data_inicial, data_final)
            venda_combo_metrics         = metrics.get_venda_combo(data_inicial, data_final)
            venda_desconto_metrics      = metrics.get_venda_desconto(data_inicial, data_final)
            dem_fluxoproduto_metrics    = metrics.get_fluxo_produto_receita(data_inicial, data_final)

            kpi_delivery_metrics        = metrics.get_kpi_delivery(data_inicial, data_final)

    context = {
            'form'                        :form,        
            'data_inicial'                :data_inicial,                    
            'data_final'                  :data_final,                    
                    
            'pedidos_metrics'             :pedidos_metrics,            
            'pedidos_sal_metrics'         :pedidos_sal_metrics,            
            'pedidos_exp_metrics'         :pedidos_exp_metrics,                    
            'pedidos_del_metrics'         :pedidos_del_metrics,                    
            'pedidos_tog_metrics'         :pedidos_tog_metrics,    
            'pedidos_atendimentos'        :atendimentos_metrics,
            'venda_grupo_metrics'         :venda_grupo_metrics,
            'venda_pgtos_metrics'         :venda_pgtos_metrics,
            'apuracao_caixa_metrics'      :apuracao_caixa_metrics,
            'apuracao_icms_metrics'       :apuracao_icms_metrics,
            'venda_diaria_metrics'        :venda_diaria_metrics,  
            'fluxo_financeiro_metrics'    :fluxo_financeiro_metrics,  
            'concilia_recebiveis_metrics' :concilia_recebiveis_metrics,
            'movimento_caixa_metrics'     :movimento_caixa_metrics, 
            'venda_bairro_metrics'        :venda_bairro_metrics,
            'venda_entregador_metrics'    :venda_entregador_metrics,
            'venda_atendente_metrics'     :venda_atendente_metrics,
            'venda_combo_metrics'         :venda_combo_metrics,
            'venda_desconto_metrics'      :venda_desconto_metrics,            
            'dem_fluxoproduto_metrics'    :dem_fluxoproduto_metrics,

            'kpi_delivery_metrics'        :kpi_delivery_metrics,             
        }

    return render(request, 'home.html', context)



