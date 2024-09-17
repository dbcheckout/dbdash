from django.db import models
from produto.models import Produtos,Grupos,Tipos,Tamanhos

# Create your models here.



class Combo(models.Model):
    numero = models.AutoField(primary_key=True)
    loja = models.IntegerField(default=0)
    descricao = models.CharField(max_length=29, null=True, blank=True)
    preco = models.FloatField(null=True, blank=True)
    precificacao = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        db_table = 'combo'
        unique_together = ('numero', 'loja')
        verbose_name = 'Combo'
        verbose_name_plural = 'Combos'
        managed = False  # Django não gerenciará esta tabela        


class Desconto(models.Model):
    numero = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=50, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo = models.CharField(max_length=15, null=True, blank=True)
    relacao = models.CharField(max_length=15, null=True, blank=True)
    aplicacao = models.CharField(max_length=15, null=True, blank=True)
    loja = models.IntegerField(null=True, blank=True)
    ativado = models.CharField(max_length=1, null=True, blank=True)
    acao = models.CharField(max_length=20, null=True, blank=True)
    assistido = models.CharField(max_length=1, null=True, blank=True)
    data = models.DateTimeField(null=True, blank=True)
    coeficiente = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    incidencia = models.CharField(max_length=1, default='V')

    class Meta:
        db_table = 'descontos'
        managed = False        




class Formas_Pagamento(models.Model):
    codigo      = models.AutoField(primary_key=True)
    codigo_tipo = models.IntegerField(null=True, blank=True)
    descricao   = models.CharField(max_length=20, null=True, blank=True)
    cod_ecf     = models.CharField(max_length=2, default='01')
    bandeira    = models.IntegerField(null=True, blank=True)
    prazo_dias  = models.IntegerField(null=True, blank=True)
    valor_taxa  = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    opera_tef   = models.CharField(max_length=1, null=True, blank=True)
    loja        = models.IntegerField(null=True, blank=True)
    conta_cob   = models.IntegerField(null=True, blank=True)
    compensacao = models.CharField(max_length=1, null=True, blank=True)
    deposito = models.CharField(max_length=1, null=True, blank=True)
    deposito_dia = models.IntegerField(null=True, blank=True)
    ativa = models.CharField(max_length=1, null=True, blank=True)
    parcelas = models.IntegerField(null=True, blank=True)
    salao = models.CharField(max_length=1, null=True, blank=True)
    togo = models.CharField(max_length=1, null=True, blank=True)
    express = models.CharField(max_length=1, null=True, blank=True)
    delivery = models.CharField(max_length=1, null=True, blank=True)
    data = models.DateTimeField(null=True, blank=True)
    autenticador = models.CharField(max_length=20, null=True, blank=True)
    codcor = models.IntegerField(null=True, blank=True)
    lcto_banco = models.IntegerField(null=True, blank=True)
    lcto_agencia = models.IntegerField(null=True, blank=True)
    lcto_conta = models.IntegerField(null=True, blank=True)
    retaguarda = models.CharField(max_length=1, default='0')
    financeira = models.CharField(max_length=1, default='0')
    intervalo_dias = models.IntegerField(default=0)
    entrada_dias = models.IntegerField(default=0)
    ecommerce = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'formas_pgtos'
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        managed = False               



class Pedidos(models.Model):
    numero         = models.IntegerField(primary_key=True) 
    loja           = models.IntegerField()     
    data           = models.DateTimeField()
    captacao       = models.CharField(max_length=15)    
    atendente      = models.CharField(max_length=15)    

    origem         = models.CharField(max_length=15)
    qtd_pessoas    = models.IntegerField()
    qtd_itens      = models.IntegerField()
    qtd_produtos   = models.FloatField()
    vlr_produtos   = models.FloatField()
    vlr_desconto   = models.FloatField()
    vlr_acrescimos = models.FloatField()
    sub_total      = models.FloatField()
    taxa_servicos  = models.FloatField()
    taxa_entrega   = models.FloatField()
    vlr_pedido     = models.FloatField()
    custo          = models.FloatField()    

    cupom_fiscal_emissao = models.DateField() 
    cupom_fiscal_numero  = models.IntegerField()  
    nfce_status_cod      = models.IntegerField()  

    apura_icms     = models.FloatField()    
    apura_pis      = models.FloatField()    
    apura_cofins   = models.FloatField()    
    apura_simples  = models.FloatField()     
    
    imposto_base_reducao     = models.FloatField()     
    imposto_base_tributada   = models.FloatField()     
    imposto_base_substituida = models.FloatField()     
    imposto_base_st          = models.FloatField()     
    vlr_liquido              = models.FloatField()         
    volume                   = models.FloatField()     

    status         = models.CharField(max_length=15)
    estagio        = models.CharField(max_length=15)
    
    cidade          = models.CharField(max_length=20)
    bairro_des      = models.CharField(max_length=50)
    bairro          = models.IntegerField()

    entregador      = models.IntegerField()
    entregador_nome = models.CharField(max_length=20)


    tempo_ate      = models.CharField(max_length=10)    
    tempo_mon      = models.CharField(max_length=10)    
    tempo_loj      = models.CharField(max_length=10)        
    tempo_ent      = models.CharField(max_length=10)    

    atendimento_abertura     = models.DateTimeField()
    atendimento_encerramento = models.DateTimeField()    
    hora_captura             = models.DateTimeField()    
    hora_expedicao           = models.DateTimeField()    
    hora_baixa               = models.DateTimeField()    

    class Meta:
        db_table = 'pedidos'   
        verbose_name = 'pedidos'
        verbose_name_plural = 'movimento'     
        managed = False  
            

    def __str__(self):
        return str(self.numero)
    

class Itens(models.Model):    
    pedido        = models.ForeignKey(Pedidos, on_delete=models.CASCADE, related_name='itens_pedido', db_column='pedido', primary_key=True)
    data          = models.DateTimeField()
    loja          = models.IntegerField(null=True, blank=True)    
    atendente     = models.CharField(max_length=20)
    produto       = models.ForeignKey(Produtos, on_delete=models.CASCADE, related_name='itens',db_column='produto')
    grupo         = models.ForeignKey(Grupos, on_delete=models.CASCADE,db_column='grupo')
    tipo          = models.ForeignKey(Tipos, on_delete=models.CASCADE,db_column='tipo')
    tamanho       = models.ForeignKey(Tamanhos, on_delete=models.CASCADE,db_column='tamanho')
    descricao     = models.CharField(max_length=50)
    prc_unitario  = models.DecimalField(max_digits=10, decimal_places=2)
    vlr_icm       = models.DecimalField(max_digits=10, decimal_places=2)
    qtd           = models.DecimalField(max_digits=10, decimal_places=2)
    prc_total     = models.DecimalField(max_digits=10, decimal_places=2)
    descto_par    = models.DecimalField(max_digits=10, decimal_places=2)
    valor_liquido = models.DecimalField(max_digits=10, decimal_places=2)
    taxa_servico  = models.DecimalField(max_digits=10, decimal_places=2)
    custo         = models.DecimalField(max_digits=10, decimal_places=2)
    apura_icms    = models.DecimalField(max_digits=10, decimal_places=2)
    apura_pis     = models.DecimalField(max_digits=10, decimal_places=2)
    apura_cofins  = models.DecimalField(max_digits=10, decimal_places=2)
    apura_simples = models.DecimalField(max_digits=10, decimal_places=2)
    cancelado     = models.BooleanField(default=False)
    classe        = models.CharField(max_length=20)
    registro_comanda = models.DateTimeField()


    cfop                  = models.CharField(max_length=10)
    ncm                   = models.CharField(max_length=10)
    icms_cst              = models.CharField(max_length=10)
    icms_aliquota         = models.FloatField()     
    icms_base             = models.FloatField()     
    icms_base_red         = models.FloatField()     
    icms_base_substituida = models.FloatField()         
    icms_base_st          = models.FloatField()     
    icms_valor            = models.FloatField() 
    apura_icms_credito    = models.FloatField()
    codigo_combo          = models.ForeignKey(Combo, on_delete=models.CASCADE,db_column='codigo_combo')
    codigo_desconto       = models.ForeignKey(Desconto, on_delete=models.CASCADE, db_column='codigo_desconto', null=True, blank=True)
   
    class Meta:
        db_table     = 'pedidos_itens'   
        verbose_name = 'itens'
        verbose_name_plural = 'movimento_itens'    
        managed = False       

    def __str__(self):
        return f'{self.produto.CODIGO} - {self.qtd}'
    



class Pagamentos(models.Model):
    sequencia    = models.AutoField(primary_key=True)
    pedido       = models.ForeignKey(Pedidos, on_delete=models.CASCADE, related_name='pagamentos_itens', db_column='pedido')
    loja         = models.IntegerField(null=True, blank=True)
    data         = models.DateTimeField(null=True, blank=True)    
    caixa_numero = models.IntegerField(null=True, blank=True)
    codigo_forma = models.ForeignKey(Formas_Pagamento, on_delete=models.CASCADE, related_name='itens',db_column='codigo_forma')
    nome         = models.CharField(max_length=100, null=True, blank=True)
    cpf_cnpj     = models.CharField(max_length=25, null=True, blank=True)
    banco        = models.CharField(max_length=4, null=True, blank=True)
    agencia      = models.CharField(max_length=20, null=True, blank=True)
    conta        = models.CharField(max_length=20, null=True, blank=True)
    ncheque      = models.CharField(max_length=20, null=True, blank=True)
    ncartao      = models.CharField(max_length=25, null=True, blank=True)
    validade     = models.CharField(max_length=6, null=True, blank=True)
    codseguranca = models.CharField(max_length=15, null=True, blank=True)
    valor        = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_pago   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)    
    operador_caixa = models.CharField(max_length=20, null=True, blank=True)
    data_registro = models.DateTimeField(null=True, blank=True)
    base_compensacao = models.DateTimeField(null=True, blank=True)
    ordem = models.CharField(max_length=10, null=True, blank=True)
    cod_anterior = models.IntegerField(null=True, blank=True)
    captacao = models.CharField(max_length=15, null=True, blank=True)
    origem = models.CharField(max_length=15, null=True, blank=True)
    turno = models.IntegerField(null=True, blank=True)
    vencimento = models.DateTimeField(null=True, blank=True)
    valor_custo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tef = models.CharField(max_length=1, null=True, blank=True)    
    tef_nsu = models.CharField(max_length=15, default='')
    tef_rede = models.CharField(max_length=15, default='')
    nsu_bandeira = models.IntegerField(default=0)
    tef_bandeira = models.IntegerField(default=0)
    par_per = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    par_con = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    par_pro = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    par_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'pedidos_pgtos'
        unique_together = (('sequencia', 'pedido'),)
        verbose_name = 'Pedido Pagamento'
        verbose_name_plural = 'Pedidos Pagamentos'
        managed = False        



class ApuracaoCaixa(models.Model):
    id     = models.AutoField(primary_key=True)
    chave  = models.CharField(max_length=20, null=True, blank=True)
    codigo = models.IntegerField(null=True, blank=True)
    loja   = models.IntegerField(null=True, blank=True)
    origem = models.CharField(max_length=20, null=True, blank=True)
    caixa  = models.IntegerField(null=True, blank=True)
    turno  = models.IntegerField(null=True, blank=True)
    data   = models.DateTimeField(null=True, blank=True)
    forma_pgto = models.IntegerField(null=True, blank=True)
    forma_pgto_descricao = models.CharField(max_length=20, null=True, blank=True)
    docs = models.IntegerField(default=0)
    valor = models.FloatField(null=True, blank=True)
    valor_recebido = models.FloatField(null=True, blank=True)
    diferenca = models.FloatField(null=True, blank=True)
    autenticador = models.CharField(max_length=20, null=True, blank=True)
    repasse = models.FloatField(null=True, blank=True)
    data_registro = models.DateTimeField(null=True, blank=True)
    cpu_caixa = models.CharField(max_length=20, null=True, blank=True)
    outros_creditos = models.FloatField(default=0.00)
    outros_debitos = models.FloatField(default=0.00)
    operador = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'apuracao_caixa'
        managed = False  # Caso a tabela já exista no banco e não deva ser gerenciada pelo Django

    def __str__(self):
        return f"{self.chave} - {self.loja} - {self.data}"
    



class FluxoFinanceiro(models.Model):
    codigo = models.AutoField(primary_key=True)
    historico = models.CharField(max_length=50, null=True, blank=True)
    fluxo = models.CharField(max_length=1, null=True, blank=True)
    movbco = models.CharField(max_length=1, null=True, blank=True)
    hiscom = models.CharField(max_length=1, null=True, blank=True)
    movtrf = models.CharField(max_length=1, null=True, blank=True)
    tipo = models.CharField(max_length=30, null=True, blank=True)
    grupo = models.CharField(max_length=20, null=True, blank=True)
    plano_de_contas = models.CharField(max_length=20, null=True, blank=True)
    categoria = models.CharField(max_length=1, null=True, blank=True)
    origem = models.CharField(max_length=12, null=True, blank=True)
    data = models.DateField(null=True, blank=True)
    dre = models.CharField(max_length=1, default='0')
    fin = models.CharField(max_length=1, default='0')
    contra_partida = models.IntegerField(default=0)
    outros_creditos = models.IntegerField(default=0)
    outros_debitos = models.IntegerField(default=0)

    class Meta:
        db_table = 'contas_financeiras_historico'
        managed = False  # Para tabelas que já existem e não precisam ser gerenciadas pelo Django

    def __str__(self):
        return f"Historico {self.codigo} - {self.historico}"
    

class MovFinanceiro(models.Model):
    registro = models.AutoField(primary_key=True)
    origem = models.CharField(max_length=20, null=True, blank=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    empresa = models.CharField(max_length=20, null=True, blank=True)
    loja = models.IntegerField(null=True, blank=True)
    lancamento = models.CharField(max_length=1, null=True, blank=True)
    datareg = models.DateTimeField(null=True, blank=True)
    tipodocumento = models.CharField(max_length=15, null=True, blank=True)
    fluxofinanceiro = models.ForeignKey(FluxoFinanceiro, on_delete=models.CASCADE, related_name='MovFin',db_column='fluxofinanceiro')
    forma = models.IntegerField(null=True, blank=True)
    dtemissao = models.DateTimeField(null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    conta = models.IntegerField(null=True, blank=True)
    historico = models.CharField(max_length=80, null=True, blank=True)
    usuario = models.IntegerField(null=True, blank=True)
    dataalt = models.IntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=8, null=True, blank=True)
    chave = models.CharField(max_length=50, null=True, blank=True)
    departamento = models.IntegerField(null=True, blank=True)
    funcionario = models.IntegerField(null=True, blank=True)
    qtd = models.FloatField(null=True, blank=True)
    valor_unitario = models.FloatField(null=True, blank=True)
    autenticador = models.CharField(max_length=20, null=True, blank=True)
    empenho = models.CharField(max_length=1, null=True, blank=True)
    empenho_qtd = models.IntegerField(null=True, blank=True)
    empenho_valor = models.FloatField(null=True, blank=True)
    data = models.DateTimeField(null=True, blank=True)
    plano_contas = models.CharField(max_length=20, null=True, blank=True)
    CNPJ_CPF = models.CharField(max_length=20, null=True, blank=True)
    chaveimportacao = models.CharField(max_length=20, null=True, blank=True)
    favorecido = models.CharField(max_length=100, null=True, blank=True)
    contrato = models.CharField(max_length=20, null=True, blank=True)
    codigo_coorelacao = models.IntegerField(null=True, blank=True)
    concilia = models.CharField(max_length=100, default='0', null=True, blank=True)
    cliente = models.IntegerField(null=True, blank=True)
    pedido = models.IntegerField(default=999, null=True, blank=True)
    checkout = models.CharField(max_length=20, null=True, blank=True)
    tipolancamento = models.CharField(max_length=15, null=True, blank=True)
    competencia = models.IntegerField(default=0, null=True, blank=True)
    nf_recibo = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        db_table = 'mov_financeiro'
        indexes = [
            models.Index(fields=['dtemissao', 'forma'], name='ind_01'),
            models.Index(fields=['CNPJ_CPF', 'contrato'], name='ind_02'),
            models.Index(fields=['dtemissao'], name='ind_03'),
        ]
        managed = False      


from django.db import models

class ConciliacaoRecebiveis(models.Model):
    registro = models.AutoField(primary_key=True)
    loja = models.IntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=15, null=True, blank=True)
    fluxo = models.CharField(max_length=1, default='E')
    chave = models.CharField(max_length=30, default='recebiveis')
    adquirente = models.CharField(max_length=30, null=True, blank=True)
    autenticador = models.CharField(max_length=20, null=True, blank=True)
    data_registro = models.DateTimeField(null=True, blank=True)
    id_transacao = models.CharField(max_length=50, null=True, blank=True)
    numero_cartao = models.CharField(max_length=50, null=True, blank=True)
    data_transacao = models.DateTimeField(null=True, blank=True)
    conciliacao_competencia = models.DateTimeField(null=True, blank=True)
    operacao = models.CharField(max_length=20, null=True, blank=True)
    bandeira = models.CharField(max_length=20, null=True, blank=True)
    forma_pgto = models.CharField(max_length=20, null=True, blank=True)
    identificacao_maquininha = models.CharField(max_length=20, null=True, blank=True)
    valor_bruto = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valor_liquido = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    valor_taxa = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, null=True, blank=True)
    nsu = models.CharField(max_length=20, null=True, blank=True)
    cod_venda = models.CharField(max_length=20, null=True, blank=True)
    nome_cliente = models.CharField(max_length=100, null=True, blank=True)
    email_cliente = models.CharField(max_length=100, null=True, blank=True)
    conciliacao_data = models.DateTimeField(null=True, blank=True)
    conciliacao_pedido = models.IntegerField(null=True, blank=True)
    conciliacao_lcto = models.IntegerField(null=True, blank=True)
    conciliacao_tipo = models.IntegerField(default=0)

    class Meta:
        db_table = 'conciliacao_recebiveis'
        managed = False  # Defina como True se o Django deve gerenciar este modelo


class Movimento(models.Model):
    numero = models.AutoField(primary_key=True)
    caixa_numero = models.IntegerField()
    data = models.DateTimeField()
    caixa_cpu = models.CharField(max_length=30)
    origem = models.CharField(max_length=20, default='')
    venda = models.FloatField(null=True, blank=True)
    saldoinicial = models.FloatField(null=True, blank=True)
    taxa_servico = models.FloatField(null=True, blank=True)
    taxa_entrega = models.FloatField(null=True, blank=True)
    venda_dinheiro = models.FloatField(null=True, blank=True)
    venda_recebiveis = models.FloatField(null=True, blank=True)
    sangria = models.FloatField(null=True, blank=True)
    reforco = models.FloatField(null=True, blank=True)
    saldofinal = models.FloatField(null=True, blank=True)
    diferenca = models.FloatField(null=True, blank=True)
    situacao = models.CharField(max_length=15, null=True, blank=True)
    turno = models.CharField(max_length=15, null=True, blank=True)
    operador = models.CharField(max_length=20, null=True, blank=True)
    loja = models.IntegerField(null=True, blank=True)
    consideracoes = models.TextField(null=True, blank=True)
    autenticador_abertura = models.CharField(max_length=20, null=True, blank=True)
    autenticador_trocaturbo = models.CharField(max_length=20, null=True, blank=True)
    autenticador_encerramento = models.CharField(max_length=20, null=True, blank=True)
    ger_abe = models.IntegerField(null=True, blank=True)
    ger_fch = models.IntegerField(null=True, blank=True)
    abertura = models.DateTimeField(null=True, blank=True)
    fechamento = models.DateTimeField(null=True, blank=True)
    troca_turno = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'movimento'
        unique_together = (('numero', 'caixa_numero', 'data', 'caixa_cpu', 'origem'),)
        managed = False  # Django não gerenciará esta tabela



class FluxoProdutoReceita(models.Model):
    numero             = models.AutoField(primary_key=True)
    loja               = models.IntegerField(null=True, blank=True)
    data               = models.DateField(null=True, blank=True)
    origem             = models.CharField(max_length=20, null=True, blank=True)
    turno              = models.IntegerField(null=True, blank=True)
    tipo               = models.CharField(max_length=20, null=True, blank=True)    
    produto_codigo     = models.IntegerField(null=True, blank=True)
    produto_qtd        = models.IntegerField(null=True, blank=True)
    ingrediente_codigo = models.ForeignKey(Produtos, on_delete=models.CASCADE, db_column='ingrediente_codigo') 
    ingrediente_qtd    = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    pre_receita        = models.CharField(max_length=1, default='0')
    categoria          = models.CharField(max_length=1, null=True, blank=True)
    classe             = models.CharField(max_length=15, null=True, blank=True)
    aquisicao          = models.CharField(max_length=15, null=True, blank=True)
    custo              = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    produto_base       = models.CharField(max_length=1, default='0')
    mvto_estoque       = models.CharField(max_length=1, default='0')

    class Meta:
        db_table = 'dem_fluxo_produto_receita'
        verbose_name = 'Fluxo Produto Receita'
        verbose_name_plural = 'Fluxo Produtos Receitas'
        managed = False  # Django não gerenciará esta tabela        
