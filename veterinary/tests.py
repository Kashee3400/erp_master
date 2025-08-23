# tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models.stock_models import (
    Medicine,
    MedicineCategory,
    MedicineStock,
    UserMedicineStock,
    UserMedicineTransaction,
    MedicineStockAudit,
)
from .choices import MedicineFormChoices, ActionTypeChoices

User = get_user_model()


class MedicineStockModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.category = MedicineCategory.objects.create(
            category="Tablet",
            medicine_form=MedicineFormChoices.TABLET,
            unit_of_quantity="tablets",
        )

        self.medicine = Medicine.objects.create(
            medicine="Paracetamol", strength="500mg", category=self.category
        )

        self.stock = MedicineStock.objects.create(
            medicine=self.medicine,
            total_quantity=100,
            batch_number="BATCH001",
            expiry_date=date.today() + timedelta(days=365),
        )

    def test_medicine_stock_creation(self):
        self.assertEqual(self.stock.medicine.medicine, "Paracetamol")
        self.assertEqual(self.stock.total_quantity, 100)
        self.assertEqual(self.stock.batch_number, "BATCH001")

    def test_user_medicine_allocation(self):
        allocation = UserMedicineStock.objects.create(
            user=self.user,
            medicine_stock=self.stock,
            allocated_quantity=20,
            min_threshold=5,
            allocated_by=self.user,
        )

        self.assertEqual(allocation.remaining_quantity(), 20)
        self.assertFalse(allocation.is_below_threshold())

        # Test usage
        allocation.used_quantity = 16
        allocation.save()

        self.assertEqual(allocation.remaining_quantity(), 4)
        self.assertTrue(allocation.is_below_threshold())


class MedicineStockAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_staff=True,
        )

        self.regular_user = User.objects.create_user(
            username="regularuser", email="regular@example.com", password="testpass123"
        )

        self.token = Token.objects.create(user=self.user)
        self.regular_token = Token.objects.create(user=self.regular_user)

        self.category = MedicineCategory.objects.create(
            category="Tablet",
            medicine_form=MedicineFormChoices.TABLET,
            unit_of_quantity="tablets",
        )

        self.medicine = Medicine.objects.create(
            medicine="Paracetamol", strength="500mg", category=self.category
        )

        self.stock = MedicineStock.objects.create(
            medicine=self.medicine,
            total_quantity=100,
            batch_number="BATCH001",
            expiry_date=date.today() + timedelta(days=365),
        )

    def test_medicine_stock_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        url = reverse("medicinestock-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["medicine_name"], "Paracetamol")

    def test_medicine_stock_create(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        url = reverse("medicinestock-list")

        data = {
            "medicine": self.medicine.id,
            "total_quantity": 50,
            "batch_number": "BATCH002",
            "expiry_date": date.today() + timedelta(days=200),
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicineStock.objects.count(), 2)

        # Check audit log created
        self.assertTrue(
            MedicineStockAudit.objects.filter(
                medicine=self.medicine, transaction_type="IN"
            ).exists()
        )

    def test_regular_user_cannot_create_stock(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.regular_token.key)
        url = reverse("medicinestock-list")

        data = {
            "medicine": self.medicine.id,
            "total_quantity": 50,
            "batch_number": "BATCH002",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_low_stock_alerts(self):
        # Create low stock
        low_stock = MedicineStock.objects.create(
            medicine=self.medicine, total_quantity=5, batch_number="LOW001"
        )

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        url = reverse("medicinestock-low-stock-alerts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

        # Check alert contains expected fields
        alert = response.data[0]
        self.assertEqual(alert["type"], "global_stock")
        self.assertIn("severity", alert)
        self.assertIn("message", alert)

    def test_expiry_alerts(self):
        # Create expiring stock
        expiring_stock = MedicineStock.objects.create(
            medicine=self.medicine,
            total_quantity=30,
            batch_number="EXP001",
            expiry_date=date.today() + timedelta(days=5),
        )

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        url = reverse("medicinestock-expiry-alerts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

        alert = response.data[0]
        self.assertEqual(alert["type"], "global_stock")
        self.assertEqual(alert["days_to_expiry"], 5)

    def test_bulk_stock_update(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        url = reverse("medicinestock-bulk-update-stock")

        data = {
            "updates": [
                {"id": self.stock.id, "quantity": 150, "reason": "Test bulk update"}
            ]
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success_count"], 1)
        self.assertEqual(response.data["error_count"], 0)

        # Check stock updated
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.total_quantity, 150)


class UserMedicineStockAPITest(APITestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="testpass123",
            is_staff=True,
        )

        self.regular_user = User.objects.create_user(
            username="regular", email="regular@example.com", password="testpass123"
        )

        self.staff_token = Token.objects.create(user=self.staff_user)
        self.regular_token = Token.objects.create(user=self.regular_user)

        self.category = MedicineCategory.objects.create(
            category="Tablet",
            medicine_form=MedicineFormChoices.TABLET,
            unit_of_quantity="tablets",
        )

        self.medicine = Medicine.objects.create(
            medicine="Aspirin", strength="100mg", category=self.category
        )

        self.stock = MedicineStock.objects.create(
            medicine=self.medicine, total_quantity=100, batch_number="ASP001"
        )

    def test_allocate_medicine_to_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.staff_token.key)
        url = reverse("usermedicinestock-list")

        data = {
            "user": self.regular_user.id,
            "medicine_stock": self.stock.id,
            "allocated_quantity": 20,
            "min_threshold": 5,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check allocation created
        allocation = UserMedicineStock.objects.get(
            user=self.regular_user, medicine_stock=self.stock
        )
        self.assertEqual(allocation.allocated_quantity, 20)
        self.assertEqual(allocation.allocated_by, self.staff_user)

        # Check transaction logged
        self.assertTrue(
            UserMedicineTransaction.objects.filter(
                user_medicine_stock=allocation, action="ALLOCATED"
            ).exists()
        )

    def test_insufficient_stock_allocation(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.staff_token.key)
        url = reverse("usermedicinestock-list")

        data = {
            "user": self.regular_user.id,
            "medicine_stock": self.stock.id,
            "allocated_quantity": 150,  # More than available
            "min_threshold": 5,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Insufficient stock", str(response.data))

    def test_use_medicine(self):
        # First allocate medicine
        allocation = UserMedicineStock.objects.create(
            user=self.regular_user,
            medicine_stock=self.stock,
            allocated_quantity=20,
            min_threshold=5,
            allocated_by=self.staff_user,
        )

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.regular_token.key)
        url = reverse("usermedicinestock-use-medicine", kwargs={"pk": allocation.id})

        data = {"quantity": 5, "note": "Treatment for patient"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        allocation.refresh_from_db()
        self.assertEqual(allocation.used_quantity, 5)
        self.assertEqual(allocation.remaining_quantity(), 15)

    def test_return_medicine(self):
        # Allocate and use some medicine
        allocation = UserMedicineStock.objects.create(
            user=self.regular_user,
            medicine_stock=self.stock,
            allocated_quantity=20,
            used_quantity=5,
            min_threshold=5,
            allocated_by=self.staff_user,
        )

        original_stock_quantity = self.stock.total_quantity

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.regular_token.key)
        url = reverse("usermedicinestock-return-medicine", kwargs={"pk": allocation.id})

        data = {"quantity": 10, "note": "Returning unused medicine"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        allocation.refresh_from_db()
        self.stock.refresh_from_db()

        self.assertEqual(
            allocation.allocated_quantity, 10
        )  # Reduced by returned amount
        self.assertEqual(self.stock.total_quantity, original_stock_quantity + 10)

    def test_user_can_only_see_own_allocations(self):
        # Create allocations for both users
        allocation1 = UserMedicineStock.objects.create(
            user=self.regular_user,
            medicine_stock=self.stock,
            allocated_quantity=10,
            allocated_by=self.staff_user,
        )

        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="testpass123"
        )

        allocation2 = UserMedicineStock.objects.create(
            user=other_user,
            medicine_stock=self.stock,
            allocated_quantity=15,
            allocated_by=self.staff_user,
        )

        # Regular user should only see their own allocation
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.regular_token.key)
        url = reverse("usermedicinestock-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], allocation1.id)

    def test_low_stock_users_alert(self):
        # Create user with low stock
        low_allocation = UserMedicineStock.objects.create(
            user=self.regular_user,
            medicine_stock=self.stock,
            allocated_quantity=10,
            used_quantity=8,  # Only 2 remaining
            min_threshold=5,
            allocated_by=self.staff_user,
        )

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.staff_token.key)
        url = reverse("usermedicinestock-low-stock-users")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

        alert = response.data[0]
        self.assertEqual(alert["type"], "user_stock")
        self.assertEqual(alert["current_quantity"], 2)


class DashboardAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            is_staff=True,
        )

        self.token = Token.objects.create(user=self.user)

        # Create test data
        self.category = MedicineCategory.objects.create(
            category="Tablet",
            medicine_form=MedicineFormChoices.TABLET,
            unit_of_quantity="tablets",
        )

        self.medicine = Medicine.objects.create(
            medicine="Test Medicine", category=self.category
        )

        # Create various stock scenarios
        self.normal_stock = MedicineStock.objects.create(
            medicine=self.medicine, total_quantity=100, batch_number="NORMAL001"
        )

        self.low_stock = MedicineStock.objects.create(
            medicine=self.medicine, total_quantity=3, batch_number="LOW001"
        )

        self.expiring_stock = MedicineStock.objects.create(
            medicine=self.medicine,
            total_quantity=50,
            batch_number="EXP001",
            expiry_date=date.today() + timedelta(days=5),
        )

    def test_dashboard_stats(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        url = reverse("dashboard-stats")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn("total_medicines", data)
        self.assertIn("total_stock_items", data)
        self.assertIn("expired_stock_count", data)
        self.assertIn("expiring_soon_count", data)
        self.assertIn("low_stock_count", data)

        self.assertEqual(data["total_stock_items"], 3)
        self.assertTrue(data["low_stock_count"] >= 1)
        self.assertTrue(data["expiring_soon_count"] >= 1)

    def test_all_alerts(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        url = reverse("dashboard-all-alerts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            len(response.data) >= 2
        )  # Should have low stock and expiry alerts

        # Check alert structure
        for alert in response.data:
            self.assertIn("type", alert)
            self.assertIn("severity", alert)
            self.assertIn("message", alert)
            self.assertIn("medicine_name", alert)

    def test_medicine_list(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        url = reverse("dashboard-medicine-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["medicine"], "Test Medicine")


# Integration Tests
class InventoryWorkflowTest(APITestCase):
    """Test complete inventory management workflow"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            is_staff=True,
        )

        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="user123"
        )

        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user1)

    def test_complete_workflow(self):
        """Test: Create medicine -> Add stock -> Allocate to user -> Use medicine -> Check alerts"""

        # 1. Create medicine category and medicine
        category = MedicineCategory.objects.create(
            category="Antibiotics",
            medicine_form=MedicineFormChoices.TABLET,
            unit_of_quantity="tablets",
        )

        medicine = Medicine.objects.create(
            medicine="Amoxicillin", strength="500mg", category=category
        )

        # 2. Add stock (as admin)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)
        stock_data = {
            "medicine": medicine.id,
            "total_quantity": 100,
            "batch_number": "AMX001",
            "expiry_date": date.today() + timedelta(days=365),
        }

        stock_response = self.client.post(
            reverse("medicinestock-list"), stock_data, format="json"
        )

        self.assertEqual(stock_response.status_code, status.HTTP_201_CREATED)
        stock_id = stock_response.data["id"]

        # 3. Allocate to user
        allocation_data = {
            "user": self.user1.id,
            "medicine_stock": stock_id,
            "allocated_quantity": 20,
            "min_threshold": 5,
        }

        allocation_response = self.client.post(
            reverse("usermedicinestock-list"), allocation_data, format="json"
        )

        self.assertEqual(allocation_response.status_code, status.HTTP_201_CREATED)
        allocation_id = allocation_response.data["id"]

        # 4. User uses medicine
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)

        use_response = self.client.post(
            reverse("usermedicinestock-use-medicine", kwargs={"pk": allocation_id}),
            {"quantity": 16, "note": "Patient treatment"},
            format="json",
        )

        self.assertEqual(use_response.status_code, status.HTTP_200_OK)

        # 5. Check that user now has low stock alert
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.admin_token.key)

        alerts_response = self.client.get(reverse("usermedicinestock-low-stock-users"))

        self.assertEqual(alerts_response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(alerts_response.data) >= 1)

        # Verify alert details
        alert = alerts_response.data[0]
        self.assertEqual(alert["type"], "user_stock")
        self.assertEqual(alert["current_quantity"], 4)  # 20 - 16 = 4
        self.assertEqual(alert["severity"], "warning")  # 4 < 5 threshold

        # 6. Check dashboard stats
        dashboard_response = self.client.get(reverse("dashboard-stats"))

        self.assertEqual(dashboard_response.status_code, status.HTTP_200_OK)
        self.assertEqual(dashboard_response.data["critical_user_stock_count"], 1)
