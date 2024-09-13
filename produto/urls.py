from django.urls import path
from . import views
from .views import export_data

urlpatterns = [    
    path('am/produtos/list/', views.AMProdutoListView.as_view(), name='am_produto_list'),    
    path('am/produtos/<int:pk>/detail/', views.AMProdutoDetailView.as_view(), name='am_produto_detail'),    
    path('export/', export_data, name='export_data'),
    
]
