from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Invoice, InvoiceDetail
from .serializer import InvoiceSerializer, InvoiceDetailSerializer


class InvoiceView(APIView):
    def get(self, request):
        invoices = Invoice.objects.all()
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            invoice_details = request.data.pop("invoice_details")
        except KeyError:
            invoice_details = {}
        invoice_serializer = InvoiceSerializer(data=request.data)

        if invoice_serializer.is_valid():
            invoice = invoice_serializer.save()
            if not invoice_details:
                return Response(invoice_serializer.data)
            invoice_details["invoice"] = invoice.id
            invoice_detail_serializer = InvoiceDetailSerializer(
                data=invoice_details,
            )
            if invoice_detail_serializer.is_valid():
                invoice_detail_serializer.save()
                return Response(
                    invoice_serializer.data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    invoice_detail_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                invoice_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class InvoiceDetailView(APIView):
    def get(self, request, pk):
        try:
            invoice = Invoice.objects.get(id=pk)
        except Invoice.DoesNotExist:
            return Response(
                "Invoice not found.",
                status=status.HTTP_404_NOT_FOUND,
            )
        invoice_serializer = InvoiceSerializer(invoice)

        try:
            invoice_details = InvoiceDetail.objects.get(invoice=invoice)
            invoice_detail_serializer = InvoiceDetailSerializer(
                invoice_details,
            )
        except InvoiceDetail.DoesNotExist:
            invoice_detail_serializer = InvoiceDetailSerializer()

        response = {
            "invoice": invoice_serializer.data,
            "invoice_details": invoice_detail_serializer.data,
        }
        return Response(response)

    def patch(self, request, pk):
        try:
            invoice_details = request.data.pop("invoice_details")
        except KeyError:
            invoice_details = {}

        try:
            invoice = Invoice.objects.get(id=pk)
            invoice_serializer = InvoiceSerializer(
                invoice,
                data=request.data,
                partial=True,
            )
        except Invoice.DoesNotExist:
            return Response(
                "Invoice not found.",
                status=status.HTTP_404_NOT_FOUND,
            )

        if invoice_serializer.is_valid():
            updated_invoice = invoice_serializer.save()
            try:
                invoice_detail = InvoiceDetail.objects.get(
                    invoice=updated_invoice,
                )
                invoice_details["invoice"] = updated_invoice.id
                invoice_detail_serializer = InvoiceDetailSerializer(
                    invoice_detail, data=invoice_details, partial=True
                )
            except InvoiceDetail.DoesNotExist:
                return Response(
                    "Invoice Detail not found.",
                    status=status.HTTP_404_NOT_FOUND,
                )
            if invoice_detail_serializer.is_valid():
                invoice_detail_serializer.save()
                return Response(invoice_serializer.data)
            else:
                return Response(
                    invoice_detail_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                invoice_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk):
        try:
            invoice = Invoice.objects.get(id=pk)
            invoice.delete()
            return Response("Invoice deleted successfully.")
        except Invoice.DoesNotExist:
            return Response(
                "Invoice not found.",
                status=status.HTTP_404_NOT_FOUND,
            )
