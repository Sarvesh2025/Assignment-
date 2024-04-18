from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class InvoiceTests(APITestCase):
    def setUp(self):
        self.invoice_data = {
            "customer_name": "John Doe",
            "invoice_details": {
                "description": "This is a test invoice",
                "unit_price": 100,
                "quantity": 2,
                "price": 200,
            },
        }

    def test_create_invoice_with_correct_data(self):
        url = reverse("invoices")
        response = self.client.post(url, self.invoice_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["customer_name"],
            self.invoice_data["customer_name"],
        )

    def test_create_invoice_with_incorrect_data(self):
        url = reverse("invoices")
        data = {
            "name": "John Doe",
        }
        response = self.client.post(url, data, format="json")
        serializer_errors = response.data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer_name", serializer_errors)
        self.assertEqual(
            serializer_errors["customer_name"][0],
            "This field is required.",
        )

    def test_get_invoices(self):
        url = reverse("invoices")

        # Create an Invoice
        self.client.post(url, self.invoice_data, format="json")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["customer_name"],
            self.invoice_data["customer_name"],
        )

    def test_update_invoice(self):
        url = reverse("invoices")
        response = self.client.post(url, self.invoice_data, format="json")
        invoice_id = response.data["id"]

        update_data = {
            "customer_name": "Jane Smith",
            "invoice_details": {
                "description": "Updated invoice description",
                "unit_price": 150,
                "quantity": 3,
                "price": 450,
            },
        }
        update_url = reverse("invoice_detail", kwargs={"pk": invoice_id})
        response = self.client.put(update_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["customer_name"], update_data["customer_name"])

    def test_delete_invoice(self):
        url = reverse("invoices")
        response = self.client.post(url, self.invoice_data, format="json")
        invoice_id = response.data["id"]

        delete_url = reverse("invoice_detail", kwargs={"pk": invoice_id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invoices_after_deletion(self):
        url = reverse("invoices")
        response = self.client.post(url, self.invoice_data, format="json")
        invoice_id = response.data["id"]

        delete_url = reverse("invoice_detail", kwargs={"pk": invoice_id})
        self.client.delete(delete_url)

        url = reverse("invoices")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class InvoiceDetailTests(APITestCase):
    def setUp(self):
        self.invoice_data = {
            "customer_name": "John Doe",
            "invoice_details": {
                "description": "This is a test invoice",
                "unit_price": 100,
                "quantity": 2,
                "price": 200,
            },
        }

    def test_get_invoice_detail(self):
        url = reverse("invoices")
        response = self.client.post(url, self.invoice_data, format="json")
        invoice_id = response.data["id"]
        url = reverse("invoice_detail", args=[invoice_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["invoice"]["customer_name"],
            self.invoice_data["customer_name"],
        )
        self.assertEqual(
            response.data["invoice_details"]["description"],
            self.invoice_data["invoice_details"]["description"],
        )

    def test_get_invoice_detail_with_incorrect_id(self):
        url = reverse("invoice_detail", args=[100])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, "Invoice not found.")
