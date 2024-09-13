from datetime import date
from django.db.models import Sum, F,ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce,Round
from django.db.models import Q
from django.utils.formats import number_format
from django.utils import timezone
from django_filters.views import FilterView
from django.views.generic import ListView
from django.db.models.aggregates import Avg,Sum,Count,Min,Max,StdDev,Variance

from grupo.models import Grupos
from tipo.models import Tipos
from produto.models import Produtos
from pedidos.models import Pedidos,PedidosItem


def get_analisemix_metricas():    
    itens = PedidosItem.objects.select_related('pedido', 'produto').all()

    for item in itens:
        quantidade = item.produto.count()

    #print(f'Pedido: {item.pedido.numero}, 
    #        Produto: {item.produto.descricao_reduzida}, 
    #        Quantidade: {item.qtd}')


    return

def get_pedidos_metrics():    
    dbc_tcs     = 0 
    dbc_vlr_ped = 0.0
    dbc_vlr_pro = 0.0
    dbc_vlr_te  = 0.0
    dbc_vlr_ts  = 0.0
    dbc_vlr_tax = 0.0
    dbc_vlr_cus = 0.0
    data_inicial=date(2024, 8, 1)
    data_final  =date(2024, 8, 31)
    for pedido in Pedidos.objects.filter(status='encerrado',estagio='baixado'):

        if pedido.numero is not None:
            dbc_tcs += 1

        if pedido.vlr_pedido is not None:
            dbc_vlr_ped += pedido.vlr_pedido

        if pedido.sub_total is not None:
            dbc_vlr_pro += pedido.sub_total    

        if pedido.taxa_servicos is not None:
            dbc_vlr_ts += pedido.taxa_servicos        

        if pedido.taxa_entrega is not None:
            dbc_vlr_te += pedido.taxa_entrega            

        if pedido.custo is not None:
            dbc_vlr_cus += pedido.custo

        
    dbc_tcm     = dbc_vlr_pro / dbc_tcs
    dbc_vlr_tax = dbc_vlr_te + dbc_vlr_ts

    
    
    return dict(
        dbc_tcs=dbc_tcs,
        dbc_vlr_ped=number_format(dbc_vlr_ped, decimal_pos=2, force_grouping=True),
        dbc_vlr_pro=number_format(dbc_vlr_pro, decimal_pos=2, force_grouping=True),        
        dbc_vlr_tax=number_format(dbc_vlr_tax, decimal_pos=2, force_grouping=True),  
        dbc_vlr_te=number_format(dbc_vlr_te, decimal_pos=2, force_grouping=True),                
        dbc_vlr_ts=number_format(dbc_vlr_ts,decimal_pos=2, force_grouping=True),
        dbc_vlr_cus=number_format(dbc_vlr_cus, decimal_pos=2, force_grouping=True),
        dbc_tcm=number_format(dbc_tcm, decimal_pos=2, force_grouping=True),
    )


def get_analise_mix_produtos_metrics():    
    

    
    
    return dict(
        dbc_tcs=dbc_tcs,
        dbc_vlr_ped=number_format(dbc_vlr_ped, decimal_pos=2, force_grouping=True),
        dbc_vlr_pro=number_format(dbc_vlr_pro, decimal_pos=2, force_grouping=True),        
        dbc_vlr_tax=number_format(dbc_vlr_tax, decimal_pos=2, force_grouping=True),  
        dbc_vlr_te=number_format(dbc_vlr_te, decimal_pos=2, force_grouping=True),                
        dbc_vlr_ts=number_format(dbc_vlr_ts,decimal_pos=2, force_grouping=True),
        dbc_vlr_cus=number_format(dbc_vlr_cus, decimal_pos=2, force_grouping=True),
        dbc_tcm=number_format(dbc_tcm, decimal_pos=2, force_grouping=True),
    )

