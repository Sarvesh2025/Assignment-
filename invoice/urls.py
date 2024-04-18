from django.urls import path
from .views import InvoiceView, InvoiceDetailView

urlpatterns = [
    path(
        "invoices/",
        InvoiceView.as_view(),
        name="invoices",
    ),
    path(
        "invoices/<int:pk>/",
        InvoiceDetailView.as_view(),
        name="invoice_detail",
    ),
]
