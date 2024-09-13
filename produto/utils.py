from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl
from django.http import HttpResponse

from app import metrics
from produto.models import Produtos, Grupos, Tipos, Tamanhos
from pedidos.models import Pedidos,Itens
from . filters import FiltroForm




def export_data(request):
    format = request.GET.get('format', 'pdf')  # Padrão para PDF se não for especificado

    if format == 'pdf':
        return export_to_pdf(request)
    elif format == 'excel':
        return export_to_excel(request)
    else:
        return HttpResponse("Formato não suportado.", status=400)


def export_to_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Adicionar conteúdo ao PDF
    p.drawString(100, height - 100, "Relatório de Produtos")

    # Adicionar mais conteúdo ao PDF
    produtos = Produtos.objects.all()  # Ajuste conforme necessário
    y = height - 120
    for produto in produtos:
        p.drawString(100, y, f'{produto.codigo} - {produto.descricao} - ')
        y -= 20

    p.showPage()
    p.save()
    
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_produtos.pdf"'
    return response

def export_to_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Produtos"

    # Adicionar cabeçalhos
    ws.append(['Código', 'Descrição', 'Quantidade', 'Preço'])

    # Adicionar dados
    produtos = Produtos.objects.all()  # Ajuste conforme necessário
    for produto in produtos:
        ws.append([produto.codigo, produto.descricao, produto.item_qtd, produto.preco])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="relatorio_produtos.xlsx"'
    wb.save(response)
    return response

