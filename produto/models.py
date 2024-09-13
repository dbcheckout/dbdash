from django.db import models

class Grupos(models.Model):
    codigo   = models.IntegerField(primary_key=True)     
    grupo    = models.CharField(max_length=30)
    classe   = models.CharField(max_length=30)    
    loja     = models.IntegerField()          

    class Meta:
        ordering = ['grupo']

    def __str__(self):
        return self.grupo
    
class Tipos(models.Model):
    codigo   = models.IntegerField(primary_key=True) 
    loja     = models.IntegerField()      
    grupo    = models.ForeignKey(Grupos, on_delete=models.CASCADE,db_column='grupo')
    tipo     = models.CharField(max_length=30)
    
    
    class Meta:
        ordering = ['tipo']

    def __str__(self):
        return self.tipo
    
class Tamanhos(models.Model):
    codigo   = models.IntegerField(primary_key=True) 
    loja     = models.IntegerField()      
    tipo     = models.ForeignKey(Tipos, on_delete=models.CASCADE,db_column='grupo')
    tamanho  = models.CharField(max_length=30)
        
    class Meta:
        ordering = ['tamanho']

    def __str__(self):
        return self.tamanho

class Produtos(models.Model):
    codigo     = models.IntegerField(primary_key=True) 
    loja       = models.IntegerField()      
    grupo      = models.ForeignKey(Grupos, on_delete=models.CASCADE,db_column='grupo')
    tipo       = models.ForeignKey(Tipos, on_delete=models.CASCADE,db_column='tipo')
    tamanho    = models.ForeignKey(Tamanhos, on_delete=models.CASCADE,db_column='tamanho')
    familia    = models.CharField(max_length=20)            
    classe     = models.CharField(max_length=30)    
    unidade_consumo = models.CharField(max_length=3)        
    classe_aquisicao  = models.CharField(max_length=20)        
    descricao  = models.CharField(max_length=50)    
    custo_real = models.FloatField()
    icms_aliquota   = models.FloatField()
    ncm             = models.CharField(max_length=15)        
    cfop_saida_est  = models.CharField(max_length=10)        
    status_produto  = models.CharField(max_length=20)        


    class Meta:
        ordering = ['grupo','tipo','descricao']
        db_table = 'produtos'
        verbose_name = 'produtos'
        verbose_name_plural = 'produtos'

        

    def __str__(self):
        return self.descricao
    

class Receitas(models.Model):
    produto      = models.ForeignKey(Produtos, on_delete=models.CASCADE,db_column='produto')
    ingrediente  = models.ForeignKey(Produtos, on_delete=models.CASCADE,related_name='receitas_produto',related_query_name='receita_ingrediente')    
    apelido      = models.CharField(max_length=20)            
    tipo         = models.CharField(max_length=1)            
    qtd          = models.DecimalField(max_digits=10, decimal_places=4)
    unidade      = models.CharField(max_length=3)            
    custo        = models.DecimalField(max_digits=10, decimal_places=4)
    retirado     = models.BooleanField(default=False)
    adicionado   = models.BooleanField(default=False)
     

    class Meta:
        ordering = ['apelido']
        
    class Meta:
        db_table = 'produtos_receitas'
        verbose_name = 'produtos_receitas'
        


    def __str__(self):
        return self.apelido



