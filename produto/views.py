from rest_framework import generics
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from . import models, forms, serializers
from django.db.models.aggregates import Avg,Sum,Count,Min,Max,StdDev,Variance
from django.db.models.functions import Coalesce,TruncMonth
from django.db.models import Sum, Max, F, FloatField, DecimalField,ExpressionWrapper
from django.db.models import Case, When, Value
from django.db.models.functions import Round,Cast
from django.utils.timezone import now
from datetime import timedelta
import json
from decimal import Decimal, ROUND_HALF_UP

from . utils import export_data,export_to_excel,export_to_pdf

from app import metrics
from produto.models import Produtos, Grupos, Tipos, Tamanhos, Receitas
from pedidos.models import Pedidos,Itens
from . filters import FiltroForm



def obter_ficha_tecnica(pro_cod,pro_qtd):    
    receitas = Receitas.objects.filter(produto_id=pro_cod).annotate(
        consumo=F('qtd') * Decimal(pro_qtd),
        custo_calculado=F('custo') * Decimal(pro_qtd)
    ).values(
        'apelido', 
        'consumo', 
        'unidade', 
        'custo_calculado'
    )

    total_consumo = receitas.aggregate(
        total_consumo=Sum('consumo')
    )['total_consumo']

    return list(receitas), total_consumo



def calcular_vendas_total(date_range, pro_qtd,total_vendas):
    # Filtra os pedidos com os critérios especificados
    pedidos = Pedidos.objects.filter(
        data__range=date_range,
        status='encerrado',
        estagio='baixado'
    )

    # Faz a junção com os itens dos pedidos e filtra por grupo
    vendas_periodo = Itens.objects.filter(
        pedido__in=pedidos,  # Verifica se o campo 'pedido' está correto        
        cancelado=False  # Certifique-se de que este campo é um BooleanField
    ).aggregate(
        qtd_total=Sum('qtd'),
        valor_total=Sum('vlr_icm')
    )

    qtd_total   = vendas_periodo['qtd_total']   or Decimal('0.00')
    valor_total = vendas_periodo['valor_total'] or Decimal('0.00')

    # Calcula a participação de quantidade
    participacao_qtd = (pro_qtd / qtd_total * Decimal('100.00')) if pro_qtd > 0 else Decimal('0.00')

    # Calcula a participação de venda
    participacao_venda = (total_vendas/ valor_total * Decimal('100.00')) if total_vendas > 0 else Decimal('0.00')

    # Imprime os valores para debug    
    print(f"Quantidade Total: {qtd_total}")
    print(f"Quantidade Prod : {pro_qtd}")
    print(f"Participação em Quantidade: {participacao_qtd}%")
    print(f"Valor Total: {valor_total}")    
    print(f"Valor Prod : {total_vendas}")    
    print(f"Participação em Venda: {participacao_venda}%")

    return {
        'qtd_total': qtd_total,
        'valor_total': valor_total,
        'participacao_qtd': participacao_qtd,
        'participacao_venda': participacao_venda
    }


def calcular_vendas_por_grupo(date_range, grupo_id,pro_qtd,total_vendas):
    # Filtra os pedidos com os critérios especificados
    pedidos = Pedidos.objects.filter(
        data__range=date_range,
        status='encerrado',
        estagio='baixado'
    )

    # Faz a junção com os itens dos pedidos e filtra por grupo
    vendas_por_grupo = Itens.objects.filter(
        pedido__in=pedidos,  # Verifica se o campo 'pedido' está correto
        grupo=grupo_id,
        cancelado=False  # Certifique-se de que este campo é um BooleanField
    ).aggregate(
        qtd_total=Sum('qtd'),
        valor_total=Sum('vlr_icm')
    )

    qtd_total   = vendas_por_grupo['qtd_total']   or Decimal('0.00')
    valor_total = vendas_por_grupo['valor_total'] or Decimal('0.00')

    # Calcula a participação de quantidade
    participacao_qtd = (pro_qtd / qtd_total * Decimal('100.00')) if pro_qtd > 0 else Decimal('0.00')

    # Calcula a participação de venda
    participacao_venda = (total_vendas/ valor_total * Decimal('100.00')) if total_vendas > 0 else Decimal('0.00')

    # Imprime os valores para debug
    print(f"Grupo ID: {grupo_id}")
    print(f"Quantidade Total: {qtd_total}")
    print(f"Quantidade Prod : {pro_qtd}")
    print(f"Participação em Quantidade: {participacao_qtd}%")
    print(f"Valor Total: {valor_total}")    
    print(f"Valor Prod : {total_vendas}")    
    print(f"Participação em Venda: {participacao_venda}%")

    return {
        'qtd_total': qtd_total,
        'valor_total': valor_total,
        'participacao_qtd': participacao_qtd,
        'participacao_venda': participacao_venda
    }


def calcular_vendas_por_tipo(date_range, tipo_id,pro_qtd,total_vendas):
    # Filtra os pedidos com os critérios especificados
    pedidos = Pedidos.objects.filter(
        data__range=date_range,
        status='encerrado',
        estagio='baixado'
    )

    # Faz a junção com os itens dos pedidos e filtra por grupo
    vendas_por_tipo = Itens.objects.filter(
        pedido__in=pedidos,  # Verifica se o campo 'pedido' está correto
        tipo=tipo_id,
        cancelado=False  # Certifique-se de que este campo é um BooleanField
    ).aggregate(
        qtd_total=Sum('qtd'),
        valor_total=Sum('vlr_icm')
    )

    qtd_total   = vendas_por_tipo['qtd_total'] or Decimal('0.00')
    valor_total = vendas_por_tipo['valor_total'] or Decimal('0.00')

# Calcula a participação de quantidade
    participacao_qtd = (pro_qtd / qtd_total * Decimal('100.00')) if pro_qtd > 0 else Decimal('0.00')

    # Calcula a participação de venda
    participacao_venda = (total_vendas/ valor_total * Decimal('100.00')) if total_vendas > 0 else Decimal('0.00')

    return {
        'qtd_total': qtd_total,
        'valor_total': valor_total,
        'participacao_qtd': participacao_qtd,
        'participacao_venda': participacao_venda
    }



def calcular_vendas_por_tamanho(date_range, tamanho_id,pro_qtd,total_vendas):
    # Filtra os pedidos com os critérios especificados
    pedidos = Pedidos.objects.filter(
        data__range=date_range,
        status='encerrado',
        estagio='baixado'
    )

    # Faz a junção com os itens dos pedidos e filtra por grupo
    vendas_por_tamanho = Itens.objects.filter(
        pedido__in=pedidos,  # Verifica se o campo 'pedido' está correto
        tamanho=tamanho_id,
        cancelado=False  # Certifique-se de que este campo é um BooleanField
    ).aggregate(
        qtd_total=Sum('qtd'),
        valor_total=Sum('vlr_icm')
    )
    qtd_total   = vendas_por_tamanho['qtd_total'] or Decimal('0.00')
    valor_total = vendas_por_tamanho['valor_total'] or Decimal('0.00')

    # Calcula a participação de quantidade
    participacao_qtd = (pro_qtd / qtd_total * Decimal('100.00')) if pro_qtd > 0 else Decimal('0.00')

    # Calcula a participação de venda
    participacao_venda = (total_vendas/ valor_total * Decimal('100.00')) if total_vendas > 0 else Decimal('0.00')

    return {
        'qtd_total': qtd_total,
        'valor_total': valor_total,
        'participacao_qtd': participacao_qtd,
        'participacao_venda': participacao_venda
    }

def consulta_produtos(dtini, dtfim, grupo=None, tipo=None):
    # Obter o total de vendas
    total_vnd = 0
    
    queryset = Produtos.objects.filter(
        itens__pedido__data__range=(dtini, dtfim),
        itens__pedido__estagio='baixado',
        itens__pedido__status='encerrado',
        itens__cancelado=False
    )
    
    if grupo:
        queryset = queryset.filter(grupo=grupo)
    
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    
    # Calcular o percentual de participação
    queryset = queryset.annotate(
        cus_unit     = Round(ExpressionWrapper(F('itens__qtd') * F('custo_real'), output_field=DecimalField()), 2),
        tcs_vnd      = Count('itens__data'),
        ult_vnd      = Max('itens__data'),
        preco        = Round(Max('itens__prc_unitario'), 2),
        prc_med      = Round(Sum(F('itens__vlr_icm')) / Sum(F('itens__qtd')), 2),
        item_qtd     = Round(Sum(F('itens__qtd'), output_field=FloatField()), 2),
        item_prc     = Round(Sum(F('itens__prc_total'), output_field=DecimalField()), 2),
        item_des     = Round(Sum(F('itens__descto_par'), output_field=DecimalField()), 2),
        item_vnd     = Round(Sum(F('itens__vlr_icm'), output_field=DecimalField()), 2),
        item_cus     = Round(Sum(F('custo_real') * F('itens__qtd'), output_field=DecimalField()), 2),
        item_ts      = Round(Sum(F('itens__taxa_servico'), output_field=DecimalField()), 2),
        item_icms    = Round(Sum(F('itens__apura_icms'), output_field=DecimalField()), 2),
        item_pis     = Round(Sum(F('itens__apura_pis'), output_field=DecimalField()), 2),
        item_cof     = Round(Sum(F('itens__apura_cofins'), output_field=DecimalField()), 2),
        item_sim     = Round(Sum(F('itens__apura_simples'), output_field=DecimalField()), 2),
        item_tri     = Round(Sum(F('itens__apura_icms') + F('itens__apura_pis') + F('itens__apura_cofins'), output_field=DecimalField()), 2),
        item_liq     = Round(Sum(F('itens__vlr_icm') - F('itens__apura_icms') - F('itens__apura_pis') - F('itens__apura_cofins'), output_field=DecimalField()), 2),
        item_mrg     = Round(Sum(F('itens__vlr_icm') - F('itens__apura_icms') - F('itens__apura_pis') - F('itens__apura_cofins') - (F('custo_real') * F('itens__qtd')), output_field=DecimalField()), 2),
        item_par = Case(
            When(item_vnd__gt=0, then=ExpressionWrapper(100.0 * F('item_vnd') / total_vnd, output_field=FloatField())),
            default=0.0,
            output_field=FloatField()
        )
    ).order_by('-item_vnd', 'grupo', 'tipo')
    
    return queryset


class AMProdutoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):    
    model = Produtos
    template_name = 'am_produto_list.html'
    context_object_name = 'amprodutos'
    paginate_by = 50
    permission_required = 'produtos.view_produto'


    def get_queryset(self):
        dtini = self.request.GET.get('dtini')
        dtfim = self.request.GET.get('dtfim')
        grupo = self.request.GET.get('grupo')
        tipo  = self.request.GET.get('tipo')        
        
        return consulta_produtos(dtini, dtfim, grupo, tipo)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FiltroForm(self.request.GET or None)
        return context
    






class AMProdutoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Produtos
    template_name = 'produto_detail.html'
    context_object_name = 'amproduto'
    permission_required = 'produtos.view_produto'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        produto = self.get_object()

        pro_cod   = produto.codigo
        pro_des   = produto.descricao        
        pro_cus   = produto.custo_real
        pro_und   = produto.unidade_consumo
        pro_aicms = produto.icms_aliquota
        pro_ncm   = produto.ncm
        pro_cfop  = produto.cfop_saida_est        
        pro_gru   = produto.grupo.codigo
        pro_tip   = produto.tipo.codigo
        pro_tam   = produto.tamanho.codigo

        print('codigo:', pro_cod)
        print('grupo:', pro_gru)
        print('tipo:', pro_tip)
        
        # Obtendo os filtros da URL
        data_inicio = self.request.GET.get('dtini')
        data_fim    = self.request.GET.get('dtfim')

        # Validando as datas
        if data_inicio and data_fim:
            date_range = [data_inicio, data_fim]
        else:
            date_range = None

        # Filtrando os PedidoItems com base nos parâmetros
        queryset = Itens.objects.filter(
            produto=produto,
            pedido__data__range=date_range,
            pedido__estagio='baixado',
            pedido__status='encerrado',
            cancelado=False            
        )

        # Calculando total e média

        pro_qtd      = queryset.aggregate(total=Sum('qtd'))['total']        
        pro_prc_car  = queryset.aggregate(maximo=Max('prc_unitario'))['maximo']
        pro_prc_med  = queryset.aggregate(media=Sum('vlr_icm')/Sum('qtd'))['media']        
        pro_icms     = queryset.aggregate(total=Sum('apura_icms'))['total']        
        pro_pis      = queryset.aggregate(total=Sum('apura_pis'))['total']                
        pro_cofins   = queryset.aggregate(total=Sum('apura_cofins'))['total']                
        pro_tri      = queryset.aggregate(total=Sum('apura_icms')+Sum('apura_pis')+Sum('apura_cofins'))['total']        
        total_vendas = queryset.aggregate(total=Sum('vlr_icm'))['total']
        media_vendas = queryset.aggregate(media=Avg('qtd'))['media']


        vnd_pro_tot = calcular_vendas_total(date_range, pro_qtd,total_vendas)
        vnd_pro_gru = calcular_vendas_por_grupo(date_range, pro_gru,pro_qtd,total_vendas)
        vnd_pro_tip = calcular_vendas_por_tipo(date_range, pro_tip,pro_qtd,total_vendas)
        vnd_pro_tam = calcular_vendas_por_tamanho(date_range, pro_tam,pro_qtd,total_vendas)

        # Contando a quantidade de pedidos únicos
        pro_tcs = queryset.values('pedido').distinct().count()
        
        pro_cmv = queryset.aggregate(
        total_custo=Sum(
            ExpressionWrapper(
                F('qtd') * F('produto__custo_real'),
                output_field=DecimalField()  # Definindo explicitamente como DecimalField
                    )
                )
            )['total_custo']
        
        
        pro_liq = total_vendas - (pro_tri or 0) 
        
        pro_mrg_brt = total_vendas - (pro_tri or 0) - (pro_cmv or 0)

    
        # Obtendo a data de hoje
        today = now().date()
        last_year = today - timedelta(days=365)


        # Filtrando as vendas quantidade e valor dos ultimos 12 meses
        queryset = Itens.objects.filter(
            produto=produto,
            pedido__data__range=[last_year, today],
            pedido__estagio='baixado',
            pedido__status='encerrado',
            cancelado=False
            ).annotate(
            mes=TruncMonth('pedido__data')
            ).values('mes').annotate(
            total_vendas=Sum('vlr_icm'),
            total_quantidade=Sum('qtd')
            ).order_by('mes')
                
        meses = []
        quantidades = []
        valores = []

        # Itere sobre o queryset para preencher as listas
        for item in queryset:
            meses.append(item['mes'].strftime('%Y-%m'))  # Converte o objeto de data para o formato 'YYYY-MM'
            quantidades.append(float(item['total_quantidade']) if item['total_quantidade'] else 0)  # Converte para float ou insere 0
            valores.append(float(item['total_vendas']) if item['total_vendas'] else 0)  # Converte para float ou insere 0

        # Converta as listas para JSON
        json_meses       = json.dumps(meses)
        json_quantidades = json.dumps(quantidades)
        json_valores     = json.dumps(valores)

        # Calculando o valor de vendas por origem
        origem_query = Itens.objects.filter(
            produto=produto,
            pedido__data__range=[last_year, today],
            pedido__estagio='baixado',
            pedido__status='encerrado',
            cancelado=False
        ).values('pedido__origem').annotate(
            total_valor=Sum('vlr_icm')
        ).order_by('pedido__origem')

        origens = []
        valores_origem = []

        for item in origem_query:
            origens.append(item['pedido__origem'])
            valores_origem.append(float(item['total_valor']) if item['total_valor'] else 0)

        json_origens = json.dumps(origens)
        json_valores_origem = json.dumps(valores_origem)

        # Filtrando os Pedidos com base nos parâmetros
        pedidos = Pedidos.objects.filter(
                    data__range=date_range,
                    estagio='baixado',
                    status='encerrado'
            )
        # Calculando os totais
        totais = pedidos.aggregate(
                    total_qtd=Sum('qtd_produtos'),
                    total_subtotal=Sum('sub_total'),
                    total_taxa_entrega=Sum('taxa_entrega'),
                    total_taxa_servicos=Sum('taxa_servicos'),
                    total_valor_pedido=Sum('vlr_pedido')
            )
        

        print(data_inicio)
        print(data_fim)
        print(date_range)

        print('Meses:', meses)
        print('Valores:', valores)
        print('Quantidades:', quantidades)


        receitas, total_consumo = obter_ficha_tecnica(pro_cod, pro_qtd)
        
        print("Total Consumo:", total_consumo)
        for receita in receitas:
            print(receita)

        

        context['pro_cod'] = pro_cod
        context['pro_des'] = pro_des
        context['pro_und'] = pro_und
        context['pro_aicms'] = pro_aicms
        context['pro_ncm'] = pro_ncm
        context['pro_cfop'] = pro_cfop
        context['pro_cus'] = pro_cus
        context['pro_qtd'] = pro_qtd
        context['pro_tcs'] = pro_tcs
        context['pro_prc_car']  = pro_prc_car
        context['pro_prc_med']  = pro_prc_med                
        context['total_vendas'] = total_vendas
        context['media_vendas'] = media_vendas
        context['pro_tri']      = pro_tri
        context['pro_icms']     = pro_icms
        context['pro_pis']      = pro_pis
        context['pro_cofins']   = pro_cofins
        context['pro_liq']      = pro_liq
        context['pro_cmv']      = pro_cmv
        context['pro_mrg_brt']  = pro_mrg_brt

        context['vnd_pro_tot']  = vnd_pro_tot
        context['vnd_pro_gru']  = vnd_pro_gru
        context['vnd_pro_tip']  = vnd_pro_tip
        context['vnd_pro_tam']  = vnd_pro_tam

        context['receitas']      = receitas
        context['total_consumo'] = total_consumo

        context['grafico_meses']       = json_meses
        context['grafico_quantidades'] = json_quantidades
        context['grafico_valores']     = json_valores
        context['grafico_origens']     = json_origens
        context['grafico_valores_origem'] = json_valores_origem        

        context['data_inicio']  = data_inicio
        context['data_fim']     = data_fim
        context['filtros'] = {
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        }
        return context