from django.shortcuts import render
from datetime import date,time,timedelta
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper,FloatField, fields, Case, When,  IntegerField, Value
from django.db.models.functions import Coalesce,Substr,Round
from django.db.models import Q,DecimalField, Value as V, DurationField
from django.utils.formats import number_format
from django.utils import timezone
from django_filters.views import FilterView
from django.views.generic import ListView
from django.db.models.aggregates import Avg,Sum,Count,Min,Max,StdDev,Variance
from datetime import date, timedelta
from django.db.models.functions import TruncDay, ExtractWeekDay, ExtractHour
from django.db.models import Q
import re

from .filters import FiltroForm

from produto.models import Produtos, Grupos, Tipos, Tamanhos
from pedidos.models import Pedidos, Itens, Pagamentos,ApuracaoCaixa, FluxoFinanceiro, MovFinanceiro
from pedidos.models import ConciliacaoRecebiveis, Movimento, Combo, Desconto, FluxoProdutoReceita


# metricas do PAINEL WEB


def get_pedidos_metrics(data_inicial, data_final):
    # Configuração inicial
    dbc_tcs     = 0
    dbc_vlr_ped = 0.0
    dbc_vlr_pro = 0.0
    dbc_vlr_te  = 0.0
    dbc_vlr_ts  = 0.0
    dbc_vlr_tax = 0.0
    dbc_vlr_cus = 0.0

    dbc_tri_icm = 0.0
    dbc_tri_pis = 0.0
    dbc_tri_cof = 0.0
    dbc_tri_sim = 0.0
    
    dbc_tri_tot = 0.0

    dbc_mrg_brt = 0.0 

    # Validando datas
    if not data_inicial or not data_final:
        return dict(
            dbc_tcs=0,
            dbc_vlr_ped ='0.00',
            dbc_vlr_pro ='0.00',
            dbc_vlr_tax ='0.00',
            dbc_vlr_te  ='0.00',
            dbc_vlr_ts  ='0.00',
            dbc_vlr_cus ='0.00',
            dbc_tcm     ='0.00',
        )



    # Filtrando pedidos dentro do intervalo de datas
    pedidos = Pedidos.objects.filter(
        status='encerrado',
        estagio='baixado',
        data__range=[data_inicial, data_final]
    )
    
    # Acumulando valores
    dbc_tcs     = pedidos.count()
    dbc_vlr_ped = pedidos.aggregate(Sum('vlr_pedido'))['vlr_pedido__sum'] or 0.0
    dbc_vlr_pro = pedidos.aggregate(Sum('sub_total'))['sub_total__sum'] or 0.0
    dbc_vlr_te  = pedidos.aggregate(Sum('taxa_entrega'))['taxa_entrega__sum'] or 0.0
    dbc_vlr_ts  = pedidos.aggregate(Sum('taxa_servicos'))['taxa_servicos__sum'] or 0.0
    dbc_vlr_cus = pedidos.aggregate(Sum('custo'))['custo__sum'] or 0.0

    dbc_tri_icm = pedidos.aggregate(Sum('apura_icms'))['apura_icms__sum'] or 0.0
    dbc_tri_pis = pedidos.aggregate(Sum('apura_pis'))['apura_pis__sum'] or 0.0
    dbc_tri_cof = pedidos.aggregate(Sum('apura_cofins'))['apura_cofins__sum'] or 0.0
    dbc_tri_sim = pedidos.aggregate(Sum('apura_simples'))['apura_simples__sum'] or 0.0


    dbc_base_red = pedidos.aggregate(Sum('imposto_base_reducao'))['imposto_base_reducao__sum'] or 0.0
    dbc_base_tri = pedidos.aggregate(Sum('imposto_base_tributada'))['imposto_base_tributada__sum'] or 0.0
    dbc_base_sub = pedidos.aggregate(Sum('imposto_base_substituida'))['imposto_base_substituida__sum'] or 0.0

    dbc_vlr_tax = dbc_vlr_te + dbc_vlr_ts
    dbc_tcm     = dbc_vlr_pro / dbc_tcs if dbc_tcs > 0 else 0.0

    dbc_tri_tot = dbc_tri_icm + dbc_tri_pis + dbc_tri_cof

    dbc_mrg_brt = dbc_vlr_pro - ( dbc_tri_tot + dbc_vlr_cus )

    def format_currency(value):
        return "{:,.2f}".format(value)
    
    return dict(
        dbc_tcs=dbc_tcs,
        dbc_vlr_ped=format_currency(dbc_vlr_ped),
        dbc_vlr_pro=format_currency(dbc_vlr_pro),
        dbc_vlr_tax=format_currency(dbc_vlr_tax),
        dbc_vlr_te=format_currency(dbc_vlr_te),
        dbc_vlr_ts=format_currency(dbc_vlr_ts),
        dbc_vlr_cus=format_currency(dbc_vlr_cus),
        dbc_tcm=format_currency(dbc_tcm),

        dbc_tri_icm=format_currency(dbc_tri_icm),
        dbc_tri_pis=format_currency(dbc_tri_pis),
        dbc_tri_cof=format_currency(dbc_tri_cof),
        dbc_tri_sim=format_currency(dbc_tri_sim),
        dbc_tri_tot=format_currency(dbc_tri_tot),

        dbc_base_red=format_currency(dbc_base_red),
        dbc_base_tri=format_currency(dbc_base_tri),
        dbc_base_sub=format_currency(dbc_base_sub),

        dbc_mrg_brt=format_currency(dbc_mrg_brt),

    )


def get_pedidos_ori_metrics(data_inicial=None, data_final=None,origem=None):    
    # Inicializa variáveis
    dbc_tcs = 0 
    dbc_vlr_ped = 0.0
    dbc_vlr_pro = 0.0
    dbc_vlr_te = 0.0
    dbc_vlr_ts = 0.0
    dbc_vlr_tax = 0.0
    dbc_vlr_cus = 0.0

    # Filtra os pedidos com base nas datas, se fornecidas
    pedidos_query = Pedidos.objects.filter(
        status='encerrado',
        estagio='baixado',
        origem= origem
    )

    if data_inicial and data_final:
        pedidos_query = pedidos_query.filter(data__range=[data_inicial, data_final])

    # Calcula os valores
    for pedido in pedidos_query:
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

    # Previne divisão por zero
    dbc_tcm = dbc_vlr_pro / dbc_tcs if dbc_tcs > 0 else 0
    dbc_vlr_tax = dbc_vlr_te + dbc_vlr_ts

    return dict(
        dbc_tcs=dbc_tcs,
        dbc_vlr_ped=number_format(dbc_vlr_ped, decimal_pos=2, force_grouping=True),
        dbc_vlr_pro=number_format(dbc_vlr_pro, decimal_pos=2, force_grouping=True),        
        dbc_vlr_tax=number_format(dbc_vlr_tax, decimal_pos=2, force_grouping=True),  
        dbc_vlr_te=number_format(dbc_vlr_te, decimal_pos=2, force_grouping=True),                
        dbc_vlr_ts=number_format(dbc_vlr_ts, decimal_pos=2, force_grouping=True),
        dbc_vlr_cus=number_format(dbc_vlr_cus, decimal_pos=2, force_grouping=True),
        dbc_tcm=number_format(dbc_tcm, decimal_pos=2, force_grouping=True),
    )


def get_consulta_vendas_atendimento(data_inicial=None, data_final=None):
    # Consulta com agregações
    resultados = Itens.objects.filter(
        pedido__data__gte=data_inicial,
        pedido__data__lte=data_final,
        pedido__estagio='baixado',
        pedido__status='encerrado',
        vlr_icm__gt=0,
        cancelado=False
    ).values(
        atendimento=Substr(F('atendente'), 1, 15)  # Agrupando por atendente
    ).annotate(
        tcs=Count('pedido__numero'),
        qtde=Sum('qtd'),
        vlr_bruto=Sum('vlr_icm'),
        vlr_liquido=Sum('valor_liquido'),
        vlr_custo=Sum('pedido__custo'),
        tcmi=ExpressionWrapper(Sum('vlr_icm') / Count('pedido__numero'), output_field=DecimalField(max_digits=10, decimal_places=2)),
        tx_servicos=ExpressionWrapper(Sum('taxa_servico'), output_field=DecimalField(max_digits=10, decimal_places=2)),
        ts_total=ExpressionWrapper(Sum('taxa_servico'), output_field=DecimalField(max_digits=10, decimal_places=2)),
        ts_casa=ExpressionWrapper(Sum('taxa_servico') * 0.2, output_field=DecimalField(max_digits=10, decimal_places=2)),
        ts_laboral=ExpressionWrapper(Sum('taxa_servico') * 0.8, output_field=DecimalField(max_digits=10, decimal_places=2)),
        ts_sindicato=ExpressionWrapper(Sum('taxa_servico') * 0.000, output_field=DecimalField(max_digits=10, decimal_places=2)),
        ts_producao=ExpressionWrapper(Sum('taxa_servico') * 0.157, output_field=DecimalField(max_digits=10, decimal_places=2)),
        ts_atendimento=ExpressionWrapper(Sum('taxa_servico') * 0.643, output_field=DecimalField(max_digits=10, decimal_places=2)),
        tcmp=ExpressionWrapper(Sum('vlr_icm') / Count('pedido__numero'), output_field=DecimalField(max_digits=10, decimal_places=2)),
        pri_lcto=Min('registro_comanda'),
        ult_lcto=Max('registro_comanda')
    )

    # Convertendo os resultados em um dicionário
    resultado_dict = []
    for item in resultados:
        pri_lcto = item['pri_lcto'].strftime('%H:%M') if item['pri_lcto'] else 'N/A'
        ult_lcto = item['ult_lcto'].strftime('%H:%M') if item['ult_lcto'] else 'N/A'
        
        resultado_dict.append({
            'atendente': item['atendimento'],
            'tcs': item['tcs'],
            'qtde': item['qtde'],
            'vlr_bruto': item['vlr_bruto'],
            'vlr_liquido': item['vlr_liquido'],
            'vlr_custo': item['vlr_custo'],
            'tcmi': item['tcmi'],
            'tx_servicos': item['tx_servicos'],
            'ts_total': item['ts_total'],
            'ts_casa': item['ts_casa'],
            'ts_laboral': item['ts_laboral'],
            'ts_sindicato': item['ts_sindicato'],
            'ts_producao': item['ts_producao'],
            'ts_atendimento': item['ts_atendimento'],
            'tcmp': item['tcmp'],
            'pri_lcto': pri_lcto,
            'ult_lcto': ult_lcto
        })

    return resultado_dict


def get_resumo_pedidos(data_inicial=None, data_final=None):
    # Filtrando os pedidos dentro do intervalo de datas
    pedidos = Pedidos.objects.filter(
        data__gte=data_inicial,
        data__lte=data_final,
        estagio='baixado',  # Assumindo que o estágio relevante é 'baixado'
        status='encerrado'  # Assumindo que o status relevante é 'encerrado'
    )
    
    # Calculando a quantidade de pedidos, a quantidade de dias operados e o valor total de sub_total
    resumo = pedidos.aggregate(
        qtd_pedidos=Count('numero'),
        dias_operados=Count('data', distinct=True),
        valor_total_subtotal=Sum('sub_total') ,
        media_pedidos_por_dia=Avg('sub_total'),
        media_subtotal_por_pedido=Avg('sub_total'),       
        valor_total_pedidos=Sum('vlr_pedido')
    )

    # Calculando a média de pedidos por dia
    if resumo['dias_operados']:
        media_pedidos_por_dia = resumo['qtd_pedidos'] / resumo['dias_operados']
    else:
        media_pedidos_por_dia = 0

    # Adicionando a média calculada ao dicionário de resultados
    resumo['media_pedidos_por_dia'] = media_pedidos_por_dia

    return resumo


def get_consulta_vendas_grupo(data_inicial=None, data_final=None):
    # Obtendo o resumo dos pedidos
    resumo = get_resumo_pedidos(data_inicial, data_final)

    # Extraindo as informações do resumo
    qtd_pedidos          = resumo.get('qtd_pedidos', 0)
    dias_operados        = resumo.get('dias_operados', 1)  # Evitar divisão por zero
    valor_total_subtotal = resumo.get('valor_total_subtotal', 0)

    resultados = Itens.objects.filter(
        pedido__data__gte=data_inicial,
        pedido__data__lte=data_final,
        pedido__estagio='baixado',
        pedido__status='encerrado',
        cancelado=False
    ).values(
        grupo_nome=F('grupo__grupo')  # Alterado para evitar conflito
    ).annotate(
        total_pedidos=Count('pedido__numero'),
        quantidade_total=Sum('qtd'),
        valor_bruto=Sum('vlr_icm'),
        valor_liquido=Sum('vlr_icm'),
        valor_custo=Sum('custo'),
        margem=ExpressionWrapper(
            ((Sum('vlr_icm') - Sum('custo')) * 100) / Coalesce(Sum('vlr_icm'), 1),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        preco_medio=ExpressionWrapper(
            Sum('vlr_icm') / Coalesce(Sum('qtd'), 1),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        itens_por_pedido=ExpressionWrapper(
            Sum('qtd') / float(qtd_pedidos) if qtd_pedidos else 0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        itens_por_dia=ExpressionWrapper(
            Sum('qtd') / float(dias_operados) if dias_operados else 0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),

        participacao_vnd=ExpressionWrapper(
            (Sum('vlr_icm') * 100) / float(valor_total_subtotal) if valor_total_subtotal else 0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).values(
        'grupo_nome',
        'total_pedidos',
        'quantidade_total',
        'valor_bruto',
        'valor_liquido',
        'valor_custo',
        'margem',
        'preco_medio',
        'itens_por_pedido',
        'itens_por_dia',        
        'participacao_vnd'
    ).order_by('-valor_bruto')

     # Convertendo os resultados para uma lista de dicionários
    resultado_dict = list(resultados)

    return resultado_dict


def get_consulta_formas_pagamento(data_inicial=None, data_final=None):
    """
    Função para totalizar os valores por formas de pagamento em um período.
    :param data_inicial: Data de início do período (datetime)
    :param data_final: Data de fim do período (datetime)
    :return: Queryset com a descrição da forma de pagamento e o total pago.
    """

    # Extraindo as informações do resumo
    resumo = get_resumo_pedidos(data_inicial, data_final)    
    qtd_pedidos = resumo.get('qtd_pedidos', 0)
    dias_operados = resumo.get('dias_operados', 1)  # Evitar divisão por zero
    valor_total_subtotal = resumo.get('valor_total_subtotal', 0)
    valor_total_pedidos  = resumo.get('valor_total_pedidos', 0)

    # Filtro aplicado ao modelo Pagamentos
    total_pagamentos = Pagamentos.objects.filter(
        pedido__data__gte=data_inicial,
        pedido__data__lte=data_final,
        pedido__estagio='baixado',
        pedido__status='encerrado',
    ).values(
        forma_nome=F('codigo_forma__descricao')  # Nome da forma de pagamento
    ).annotate(
        total_lctos=Count('*'),  # Contar o número de registros
        total_pago=Sum('valor_pago'),
        total_troco=Sum('valor_pago') - Sum('valor'),
        valor_custo=Sum('valor_custo'),
        pgto_por_pedido=ExpressionWrapper(
            Sum('valor_pago') / Count('*'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        pgto_por_dia=ExpressionWrapper(
            Sum('valor_pago') / float(dias_operados) if dias_operados else 0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        participacao_vnd=ExpressionWrapper(
            (Sum('valor_pago') * 100) / float(valor_total_subtotal) if valor_total_subtotal else 0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).order_by('-total_pago')

    resultado_dict = list(total_pagamentos)

    return total_pagamentos


def get_apuracao_caixa(data_inicial, data_final):
    # Obter os resultados agrupados por forma de pagamento
    resultados = (
        ApuracaoCaixa.objects
        .filter(
            data__gte=data_inicial,
            data__lte=data_final,
            valor__gt=0
        )
        .values('forma_pgto', 'forma_pgto_descricao')
        .annotate(
            docs=Sum('docs'),
            venda=Sum('valor'),
            outros_creditos=Sum('outros_creditos'),
            outros_debitos=Sum('outros_debitos'),
            apuracao=Sum('valor_recebido'),
            quebra=Sum('diferenca')
        )
        .order_by('forma_pgto', 'forma_pgto_descricao')
    )

    # Calcular o total e o saldo da quebra no Python
    total_venda = 0
    total_outros_creditos = 0
    total_outros_debitos = 0
    total_apuracao = 0
    total_quebra = 0

    for item in resultados:
        item['total'] = item['venda'] + item['outros_creditos'] - item['outros_debitos']
        total_venda += item['venda']
        total_outros_creditos += item['outros_creditos']
        total_outros_debitos += item['outros_debitos']
        total_apuracao += item['apuracao']
        total_quebra += item['quebra']

    saldo_quebra = total_venda + total_outros_creditos - total_outros_debitos - total_apuracao

    # Adiciona o total geral e saldo da quebra ao retorno
    return {
        'resultados': list(resultados),  # Converte o QuerySet para uma lista
        'total_venda': total_venda,
        'total_outros_creditos': total_outros_creditos,
        'total_outros_debitos': total_outros_debitos,
        'total_apuracao': total_apuracao,
        'total_quebra': total_quebra,
        'saldo_quebra': saldo_quebra
    }

def get_apuracao_icms(data_inicial, data_final):
    # Filtra os pedidos e pedidos_itens conforme as condições
    queryset = Itens.objects.filter(
        pedido__cupom_fiscal_emissao__gte=data_inicial,
        pedido__cupom_fiscal_emissao__lte=data_final,
        pedido__cupom_fiscal_numero__gt=0,
        pedido__nfce_status_cod=100,
        pedido__status="encerrado",
        pedido__estagio="baixado",
        vlr_icm__gt=0,
        cancelado="0"
    ).exclude(classe="servico").values(
        'cfop',
        'ncm',
        'icms_cst',
        'icms_aliquota',
        'produto',
        'produto__descricao'
    ).annotate(
        produto_des=Substr('produto__descricao', 1, 24),
        qtd_total=Sum('qtd'),
        venda_total=Round(Sum('vlr_icm'), 2),
        icms_base_red_total=Round(Sum('icms_base_red'), 2),
        icms_base_sub_total=Round(Sum('icms_base_substituida'), 2),
        icms_base_total=Round(Sum('icms_base'), 2),
        icms_valor_total=Round(Sum('icms_valor'), 2),
        icms_credito_total=Round(Sum('apura_icms_credito'), 2),
        icms_compensado_total=Round(Sum(F('icms_valor') - F('apura_icms_credito')), 2),
        icms_basest_total=Round(Sum('icms_base_st'), 2),
        base_contribuicoes_total=Round(Sum('valor_liquido'), 2),
        apura_pis_total=Round(Sum('apura_pis'), 2),
        apura_cofins_total=Round(Sum('apura_cofins'), 2),
        apura_simples_total=Round(Sum('apura_simples'), 2),
    ).order_by('grupo','tipo','tamanho','cfop', 'ncm', 'icms_cst')

    resultado_dict = list(queryset)

    return resultado_dict


def get_media_diaria_venda(data_inicial, data_final):
    # Definir os períodos de almoço e jantar
    periodo_almoço = Q(hora__gte=10, hora__lte=15)
    periodo_jantar = Q(hora__gte=16, hora__lte=23)

    # Dicionário para mapear os dias da semana
    dias_semana = {
        1: 'Domingo',
        2: 'Segunda',
        3: 'Terça',
        4: 'Quarta',
        5: 'Quinta',
        6: 'Sexta',
        7: 'Sábado'
    }

    # Filtra os pedidos e itens conforme as condições e horários
    queryset = Pedidos.objects.filter(
        data__gte=data_inicial,
        data__lte=data_final,
        estagio='baixado',
        status='encerrado',
    ).annotate(
        dia_da_semana=ExtractWeekDay(TruncDay('data')),
        hora=ExtractHour('atendimento_abertura')
    ).values(
        'dia_da_semana',
    ).annotate(
        # Quantidade de pedidos por dia
        quantidade_pedidos=Count('numero'),
        # Quantidade de pedidos durante o período de almoço
        quantidade_pedidos_almoço=Count(Case(
            When(periodo_almoço, then=F('numero')),
            default=None,
            output_field=IntegerField()
        )),
        # Quantidade de pedidos durante o período de jantar
        quantidade_pedidos_jantar=Count(Case(
            When(periodo_jantar, then=F('numero')),
            default=None,
            output_field=IntegerField()
        )),
        # Total para o período de almoço
        total_almoço=Sum(Case(
            When(periodo_almoço, then=F('sub_total')),
            default=0,
            output_field=FloatField()
        )),
        # Total para o período de jantar
        total_jantar=Sum(Case(
            When(periodo_jantar, then=F('sub_total')),
            default=0,
            output_field=FloatField()
        )),
        # Total do dia
        total_dia=Sum('sub_total'),
        # Média de vendas por dia (total de vendas dividido pela quantidade de pedidos)
        media_dia=Case(
            When(quantidade_pedidos=0, then=0),
            default=F('total_dia') / F('quantidade_pedidos'),
            output_field=FloatField()
        ),
        # Média de vendas durante o almoço
        media_almoço=Case(
            When(quantidade_pedidos_almoço=0, then=0),
            default=F('total_almoço') / F('quantidade_pedidos_almoço'),
            output_field=FloatField()
        ),
        # Média de vendas durante o jantar
        media_jantar=Case(
            When(quantidade_pedidos_jantar=0, then=0),
            default=F('total_jantar') / F('quantidade_pedidos_jantar'),
            output_field=FloatField()
        ),
    ).order_by('dia_da_semana')

    # Convertendo o número do dia da semana para o nome
    resultado_dict = list(queryset)
    for item in resultado_dict:
        item['dia_da_semana'] = dias_semana[item['dia_da_semana']]

    # Calcula a quantidade de ocorrências de cada dia da semana
    incidencia_dias = Pedidos.objects.filter(
        data__gte=data_inicial,
        data__lte=data_final,
        estagio='baixado',
        status='encerrado',
    ).annotate(
        dia_da_semana=ExtractWeekDay(TruncDay('data'))
    ).values(
        'dia_da_semana'
    ).annotate(
        quantidade_dias=Count('dia_da_semana')
    ).order_by('dia_da_semana')

    # Cria um dicionário para armazenar a quantidade de dias
    quantidade_dias_dict = {dia['dia_da_semana']: dia['quantidade_dias'] for dia in incidencia_dias}

    # Adiciona a quantidade de dias ao resultado principal
    for item in resultado_dict:
        dia_num = [k for k, v in dias_semana.items() if v == item['dia_da_semana']][0]
        item['quantidade_dias'] = quantidade_dias_dict.get(dia_num, 0)

    return resultado_dict


def get_fluxo_financeiro(data_inicial, data_final):
    # Filtra os registros com base no intervalo de data de emissão
    queryset = MovFinanceiro.objects.filter(
        dtemissao__gte=data_inicial,
        dtemissao__lte=data_final
    ).values(
        'fluxofinanceiro__historico',
        'fluxofinanceiro__fluxo'
    ).annotate(
        lctos=Count('registro'),  # Contagem de lançamentos
        valor_total=Sum('valor'),  # Soma dos valores
        menor_lcto=Min('valor'),  # Menor valor
        maior_lcto=Max('valor'),  # Maior valor
        media_lcto=Avg('valor')   # Média dos valores
    ).order_by('fluxofinanceiro__historico')

    # Inicializa variáveis para créditos e débitos
    total_credito = 0
    total_debito = 0

    # Calcula o total para crédito e débito
    for item in queryset:
        fluxo = item['fluxofinanceiro__fluxo']
        
        # Supondo que os fluxos de crédito e débito são identificados por descrições específicas
        if 'C' in fluxo:  # Ajustar conforme seus valores reais de fluxo
            total_credito += item['valor_total']
        elif 'D' in fluxo:  # Ajustar conforme seus valores reais de fluxo
            total_debito += item['valor_total']

    # Calcula o saldo final
    saldo = total_credito - total_debito

    # Retorna os dados agregados e o saldo
    return {
        'dados_fluxo': list(queryset),
        'total_credito': total_credito,
        'total_debito': total_debito,
        'saldo': saldo,
    }


def get_conciliacao_recebiveis(data_inicial, data_final):
    # Executa a consulta agregada
    dados = ConciliacaoRecebiveis.objects.filter(
        data_transacao__gte=data_inicial,
        data_transacao__lte=data_final
    ).values(
        'conciliacao_competencia',        
        'adquirente',
        'operacao'        
    ).annotate(
        lctos=Count('registro'),
        valor_bruto=Sum('valor_bruto'),
        taxa=Sum('valor_taxa'),
        valor_liquido=Sum('valor_liquido')
    ).order_by('-conciliacao_competencia')

    # Convertendo os resultados para um dicionário
    resultado_dict = []

    # Calculando o percentual da taxa e a transação média
    for item in dados:
        valor_bruto = item['valor_bruto'] or 1  # Evitar divisão por zero
        taxa = item['taxa'] or 0
        lctos = item['lctos'] or 1  # Evitar divisão por zero

        # Cálculo do percentual da taxa sobre o valor bruto
        percentual_taxa = (taxa / valor_bruto) * 100

        # Cálculo da transação média (valor bruto dividido pelos lançamentos)
        transacao_media = valor_bruto / lctos

        # Formatando a data no formato dd/mm/yyyy
        item['conciliacao_competencia'] = item['conciliacao_competencia'].strftime('%d/%m/%Y')

        # Adicionando os cálculos ao dicionário
        item['percentual_taxa'] = percentual_taxa
        item['transacao_media'] = transacao_media

        resultado_dict.append(item)

    return resultado_dict


def get_movimento_caixa(data_inicial, data_final):
    # Filtra os registros de movimento entre as datas fornecidas e ordena por data de forma descendente
    movimentos = Movimento.objects.filter(
        data__gte=data_inicial,   # Data inicial do filtro
        data__lte=data_final      # Data final do filtro
    ).values(
        'numero',
        'data',
        'origem',
        'saldoinicial',
        'abertura',
        'autenticador_abertura',
        'saldofinal',
        'autenticador_encerramento',
        'fechamento',
        'situacao'
    ).order_by('-data')  # Ordenação descendente pela data
    
    # Converte a lista de valores em uma lista de dicionários
    resultado_list = [
        {
            'numero': movimento['numero'],
            'data': movimento['data'],
            'origem': movimento['origem'],
            'saldo_inicial': movimento['saldoinicial'],
            'abertura': movimento['abertura'],
            'autenticador_abertura': movimento['autenticador_abertura'],
            'saldo_final': movimento['saldofinal'],
            'autenticador_encerramento': movimento['autenticador_encerramento'],
            'fechamento': movimento['fechamento'],
            'situacao': movimento['situacao']
        }
        for movimento in movimentos
    ]

    # Retorna a lista com as informações
    return resultado_list


def format_to_float(value):
    # Remove os pontos usados como separadores de milhar e substitui a vírgula por ponto
    if isinstance(value, str):
        value = value.replace('.', '').replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return 0.0


def get_venda_bairro(data_inicial, data_final):

    # Extraindo as informações do resumo
    resumo = get_pedidos_ori_metrics(data_inicial, data_final, 'delivery')    
    qtd_pedidos = resumo.get('dbc_tcs', 0)
    valor_total_pedidos = resumo.get('dbc_vlr_ped', 0)

    # Converte o valor_total_pedidos para float, removendo possíveis separadores de milhar
    valor_total_pedidos = format_to_float(valor_total_pedidos)

    if valor_total_pedidos == 0:
        valor_total_pedidos = 1  # Para evitar divisão por zero

    # Executa a consulta agregada
    pedidos_summary = Pedidos.objects.filter(
        data__gte=data_inicial,   # Data inicial do filtro
        data__lte=data_final,     # Data final do filtro
        estagio='baixado',
        status='encerrado',        
        origem='delivery'         # Origem fixa como "delivery"
    ).values(
        'cidade',
        'bairro',
        'bairro_des'
    ).annotate(
        pedidos=Count('numero'),
        produtos=Sum('qtd_produtos'),
        vlr_produtos=Sum('sub_total'),
        entrega=Sum('taxa_entrega'),
        valor=Sum('vlr_pedido'),
        tcm=Avg('sub_total')
    ).order_by('-valor')

    # Calcula a participação manualmente
    resultado_list = [
        {
            'cidade': item['cidade'],
            'bairro': item['bairro'],
            'descricao': item['bairro_des'],
            'pedidos': item['pedidos'],
            'produtos': item['produtos'],
            'vlr_produtos': item['vlr_produtos'],
            'entrega': item['entrega'],
            'valor': item['valor'],
            'tcm': item['tcm'],
            'participacao': (item['valor'] * 100 / valor_total_pedidos) if valor_total_pedidos != 0 else 0
        }
        for item in pedidos_summary
    ]

    return resultado_list


def get_venda_entregador(data_inicial, data_final):

    # Extraindo as informações do resumo
    resumo = get_pedidos_ori_metrics(data_inicial, data_final, 'delivery')    
    qtd_pedidos = resumo.get('dbc_tcs', 0)
    valor_total_pedidos = resumo.get('dbc_vlr_ped', 0)

    # Converte o valor_total_pedidos para float, removendo possíveis separadores de milhar
    valor_total_pedidos = format_to_float(valor_total_pedidos)

    if valor_total_pedidos == 0:
        valor_total_pedidos = 1  # Para evitar divisão por zero

    # Função para converter o campo 'tempo_ent' de string para timedelta
    def str_to_timedelta(tempo_str):
        horas, minutos, segundos = map(int, tempo_str.split(':'))
        return timedelta(hours=horas, minutes=minutos, seconds=segundos)

    # Função para formatar timedelta como hh:mm:ss
    def format_timedelta_to_hhmmss(td):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    # Executa a consulta agregada
    pedidos_summary = Pedidos.objects.filter(
        data__gte=data_inicial,   # Data inicial do filtro
        data__lte=data_final,     # Data final do filtro
        estagio='baixado',
        status='encerrado',        
        origem='delivery'         # Origem fixa como "delivery"
    ).values(
        'entregador',
        'entregador_nome'
    ).annotate(
        pedidos=Count('numero'),
        produtos=Sum('qtd_produtos'),
        vlr_produtos=Sum('sub_total'),
        entrega=Sum('taxa_entrega'),
        valor=Sum('vlr_pedido'),
        tcm=Avg('sub_total')
    ).order_by('-valor')

    # Calcula a participação e média do tempo de entrega por entregador
    resultado_list = []
    for item in pedidos_summary:
        entregador_pedidos = Pedidos.objects.filter(
            entregador=item['entregador'],
            data__gte=data_inicial,
            data__lte=data_final,
            estagio='baixado',
            status='encerrado',
            origem='delivery'
        ).values_list('tempo_ent', flat=True)

        # Calcula o total de tempo de entrega para o entregador
        total_tempo_entrega = timedelta()
        qtd_entregas = 0

        for tempo_entrega_str in entregador_pedidos:
            if tempo_entrega_str:
                tempo_entrega = str_to_timedelta(tempo_entrega_str)
                total_tempo_entrega += tempo_entrega
                qtd_entregas += 1

        # Cálculo da média de tempo de entrega para o entregador
        media_tempo_entrega = total_tempo_entrega / qtd_entregas if qtd_entregas > 0 else timedelta()

        # Formata a média de tempo de entrega como hh:mm:ss
        media_tempo_entrega_formatada = format_timedelta_to_hhmmss(media_tempo_entrega)

        resultado_list.append({
            'entregador': item['entregador_nome'],
            'pedidos': item['pedidos'],
            'produtos': item['produtos'],
            'vlr_produtos': item['vlr_produtos'],
            'entrega': item['entrega'],
            'valor': item['valor'],
            'tcm': item['tcm'],
            'participacao': (item['valor'] * 100 / valor_total_pedidos) if valor_total_pedidos != 0 else 0,
            'media_tempo_entrega': media_tempo_entrega_formatada  # Retorna a média formatada
        })

    return resultado_list


def get_venda_atendente(data_inicial, data_final):

    # Extraindo as informações do resumo
    resumo = get_pedidos_ori_metrics(data_inicial, data_final, 'delivery')    
    qtd_pedidos = resumo.get('dbc_tcs', 0)
    valor_total_pedidos = resumo.get('dbc_vlr_ped', 0)

    # Converte o valor_total_pedidos para float, removendo possíveis separadores de milhar
    valor_total_pedidos = format_to_float(valor_total_pedidos)

    if valor_total_pedidos == 0:
        valor_total_pedidos = 1  # Para evitar divisão por zero

    # Função para converter o campo 'tempo_ent' de string para timedelta
    def str_to_timedelta(tempo_str):
        horas, minutos, segundos = map(int, tempo_str.split(':'))
        return timedelta(hours=horas, minutes=minutos, seconds=segundos)

    # Função para formatar timedelta como hh:mm:ss
    def format_timedelta_to_hhmmss(td):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    # Executa a consulta agregada
    pedidos_summary = Pedidos.objects.filter(
        data__gte=data_inicial,   # Data inicial do filtro
        data__lte=data_final,     # Data final do filtro
        estagio='baixado',
        status='encerrado',        
        origem='delivery'         # Origem fixa como "delivery"
    ).values(
        'atendente',
        'captacao'
    ).annotate(
        pedidos=Count('numero'),
        produtos=Sum('qtd_produtos'),
        vlr_produtos=Sum('sub_total'),
        entrega=Sum('taxa_entrega'),
        valor=Sum('vlr_pedido'),
        tcm=Avg('sub_total')
    ).order_by('-valor')

    # Calcula a participação e média do tempo de entrega por entregador
    resultado_list = []
    for item in pedidos_summary:
        entregador_pedidos = Pedidos.objects.filter(
            atendente=item['atendente'],
            captacao=item['captacao'],
            data__gte=data_inicial,
            data__lte=data_final,
            estagio='baixado',
            status='encerrado',
            origem='delivery'
        ).values_list('tempo_ate', flat=True)

        # Calcula o total de tempo de entrega para o entregador
        total_tempo_entrega = timedelta()
        qtd_entregas = 0

        for tempo_entrega_str in entregador_pedidos:
            if tempo_entrega_str:
                tempo_entrega = str_to_timedelta(tempo_entrega_str)
                total_tempo_entrega += tempo_entrega
                qtd_entregas += 1

        # Cálculo da média de tempo de entrega para o entregador
        media_tempo_entrega = total_tempo_entrega / qtd_entregas if qtd_entregas > 0 else timedelta()

        # Formata a média de tempo de entrega como hh:mm:ss
        media_tempo_entrega_formatada = format_timedelta_to_hhmmss(media_tempo_entrega)

        resultado_list.append({
            'atendente': item['atendente'],
            'captacao':  item['captacao'],            
            'pedidos': item['pedidos'],
            'produtos': item['produtos'],
            'vlr_produtos': item['vlr_produtos'],
            'entrega': item['entrega'],
            'valor': item['valor'],
            'tcm': item['tcm'],
            'participacao': (item['valor'] * 100 / valor_total_pedidos) if valor_total_pedidos != 0 else 0,
            'media_tempo_entrega': media_tempo_entrega_formatada  # Retorna a média formatada
        })

    return resultado_list


def get_kpi_delivery(data_inicial, data_final):
    from datetime import timedelta
    from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, DurationField

    # Dicionário para mapear o nome do dia da semana em inglês para abreviações em português
    dias_da_semana = {
        'Monday': 'SEG',
        'Tuesday': 'TER',
        'Wednesday': 'QUA',
        'Thursday': 'QUI',
        'Friday': 'SEX',
        'Saturday': 'SAB',
        'Sunday': 'DOM'
    }

    # Função para formatar timedelta como hh:mm:ss
    def format_timedelta_to_hhmmss(td):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    # Função para formatar a data como dd/mm/yy e incluir o nome do dia da semana em português
    def format_date(date):
        day_name = dias_da_semana[date.strftime('%A')]  # Nome do dia da semana em português
        day_date = date.strftime('%d/%m/%y')
        return f"{day_date}.{day_name}"

    # Extraindo as informações do resumo
    resumo = get_pedidos_ori_metrics(data_inicial, data_final, 'delivery')
    qtd_pedidos = resumo.get('dbc_tcs', 0)
    valor_total_pedidos = resumo.get('dbc_vlr_ped', 0)

    # Converte o valor_total_pedidos para float, removendo possíveis separadores de milhar
    valor_total_pedidos = format_to_float(valor_total_pedidos)
    if valor_total_pedidos == 0:
        valor_total_pedidos = 1  # Para evitar divisão por zero

    # Consulta agregada para retornar as informações por dia de operação
    pedidos_summary = Pedidos.objects.filter(
        data__gte=data_inicial,   # Data inicial do filtro
        data__lte=data_final,     # Data final do filtro
        estagio='baixado',
        status='encerrado',
        origem='delivery'         # Origem fixa como "delivery"
    ).values(
        'data'  # Agrupa por dia
    ).annotate(
        atendentes=Count('atendente', distinct=True),
        entregadores=Count('entregador', distinct=True),
        produtos=Sum('qtd_produtos'),
        ticket_medio=Avg('sub_total'),
        pedidos=Count('numero'),
        vlr_produtos=Sum('sub_total'),
        tempo_atendimento=Avg(ExpressionWrapper(F('atendimento_encerramento') - F('atendimento_abertura'), output_field=DurationField())),
        tempo_montagem=Avg(ExpressionWrapper(F('hora_expedicao') - F('hora_captura'), output_field=DurationField())),
        tempo_loja=Avg(ExpressionWrapper(F('hora_expedicao') - F('atendimento_abertura'), output_field=DurationField())),
        tempo_entrega=Avg(ExpressionWrapper(F('hora_baixa') - F('hora_expedicao'), output_field=DurationField())),
        tempo_operacao=Avg(ExpressionWrapper(F('hora_baixa') - F('atendimento_abertura'), output_field=DurationField()))
    ).order_by('data')

    # Lista de resultados
    resultado_list = []

    for item in pedidos_summary:
        # Calcula a média de cada tempo e formata para hh:mm:ss
        media_tempo_atendimento_formatada = format_timedelta_to_hhmmss(item.get('tempo_atendimento', timedelta()))
        media_tempo_montagem_formatada = format_timedelta_to_hhmmss(item.get('tempo_montagem', timedelta()))
        media_tempo_loja_formatada = format_timedelta_to_hhmmss(item.get('tempo_loja', timedelta()))
        media_tempo_entrega_formatada = format_timedelta_to_hhmmss(item.get('tempo_entrega', timedelta()))
        media_tempo_operacao_formatada = format_timedelta_to_hhmmss(item.get('tempo_operacao', timedelta()))

        # Adiciona o resultado formatado na lista de resultados
        resultado_list.append({
            'data': format_date(item['data']),
            'atendentes': item.get('atendentes', 0),
            'entregadores': item.get('entregadores', 0),
            'produtos': item.get('produtos', 0),
            'vlr_produtos': item.get('vlr_produtos', 0),
            'ticket_medio': item.get('ticket_medio', 0),
            'pedidos': item.get('pedidos', 0),
            'media_tempo_atendimento': media_tempo_atendimento_formatada,
            'media_tempo_montagem': media_tempo_montagem_formatada,
            'media_tempo_loja': media_tempo_loja_formatada,
            'media_tempo_entrega': media_tempo_entrega_formatada,
            'media_tempo_operacao': media_tempo_operacao_formatada
        })

    return resultado_list


def get_venda_combo(data_inicial, data_final):
    """
    Retorna um resumo dos combos vendidos, incluindo quantidade e valor total.
    """
    combos_summary = (Itens.objects
                      .filter(pedido__data__gte=data_inicial, 
                              pedido__data__lte=data_final,
                              pedido__estagio='baixado',
                              pedido__status='status')
                      .values('produto__descricao', 'produto__codigo')  # Campo ajustado
                      .annotate(
                          qtd=Sum('qtd'),
                          valor=Sum('vlr_icm')
                      )
                      .order_by('produto__descricao'))

    return combos_summary


def get_venda_desconto(data_inicial, data_final):
    # Query para descontos auditados
    descontos_auditados = (Itens.objects
                           .filter(pedido__data__gte=data_inicial, 
                                   pedido__data__lte=data_final, 
                                   pedido__estagio='baixado',
                                   pedido__status='encerrado',
                                   cancelado=False,
                                   codigo_desconto__isnull=False,
                                   descto_par__gt=0)

                           .values('codigo_desconto', 'codigo_desconto__descricao')
                           .annotate(
                               qtd=Count('pedido'),
                               valor=Sum('descto_par'),
                               menord=Min('descto_par'),
                               maiord=Max('descto_par'),
                               media=Avg('descto_par')                               
                           )
                           .order_by('codigo_desconto__descricao'))
    
    # Query para descontos diretos
    descontos_diretos = (Itens.objects
                         .filter(data__gte=data_inicial, 
                                 data__lte=data_final, 
                                 pedido__estagio='baixado',
                                 pedido__status='encerrado',
                                 cancelado=False,
                                 codigo_desconto__isnull=True,
                                 descto_par__gt=0)
                         .values('codigo_desconto')
                         .annotate(
                             qtd=Count('pedido'),
                             valor=Sum('descto_par'),
                             menord=Min('descto_par'),
                             maiord=Max('descto_par'),
                             media=Avg('descto_par')

                         )
                         .order_by('codigo_desconto'))

    # Adicionar tipo de desconto nos resultados
    descontos_auditados = [{'codigo_desconto': item['codigo_desconto'],
                            'descricao': item['codigo_desconto__descricao'],
                            'tipo_desconto': 'Auditado',
                            'qtd': item['qtd'],
                          'valor': item['valor'],
                          'menord': item['menord'],
                          'maiord': item['maiord'],                                                    
                          'media': item['media']} for item in descontos_auditados]
    
    descontos_diretos = [{'codigo_desconto': None,
                          'descricao': 'Direto',
                          'tipo_desconto': 'Direto',
                          'qtd': item['qtd'],
                          'valor': item['valor'],
                          'menord': item['menord'],
                          'maiord': item['maiord'],                                                    
                          'media': item['media']} for item in descontos_diretos]    

    # Concatenar os resultados
    descontos_summary = descontos_auditados + descontos_diretos

    return descontos_summary


def get_fluxo_produto_receita(data_inicial, data_final):
    resultado = (FluxoProdutoReceita.objects
                 .filter(data__gte=data_inicial, data__lte=data_final)
                 .values(
                     'produto_codigo',  # `produto_produtos`.`codigo`
                     'ingrediente_codigo',  # `produto_produtos`.`DESCRICAO`
                 )
                 .annotate(
                     consumo = Sum('ingrediente_qtd'),  # SUM(`dem_fluxo_produto_receita`.`ingrediente_qtd`) AS CONSUMO
                     valor   = Sum(F('custo') , output_field=DecimalField()) 
                 )
                 .order_by('ingrediente_codigo'))

    return resultado
