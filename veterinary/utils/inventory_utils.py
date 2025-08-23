# utils.py
from django.utils import timezone
from django.db.models import Sum, F, Q
from datetime import timedelta
from ..models.stock_models import MedicineStock, UserMedicineStock


def get_inventory_alerts(days_ahead=30, low_stock_threshold=10):
    """
    Get comprehensive inventory alerts for dashboard
    """
    alerts = []
    now = timezone.now()

    # 1. Global Stock Alerts
    # Low stock alerts
    low_stocks = (
        MedicineStock.objects.annotate(
            allocated_quantity=Sum("user_allocations__allocated_quantity"),
            available_quantity=F("total_quantity") - F("allocated_quantity"),
        )
        .filter(
            Q(available_quantity__lte=low_stock_threshold)
            | Q(
                available_quantity__isnull=True, total_quantity__lte=low_stock_threshold
            )
        )
        .select_related("medicine", "medicine__category")
    )

    for stock in low_stocks:
        available = stock.available_quantity or stock.total_quantity
        alerts.append(
            {
                "type": "global_stock",
                "severity": "critical" if available <= 5 else "warning",
                "medicine_name": stock.medicine.medicine,
                "medicine_strength": stock.medicine.strength or "",
                "current_quantity": available,
                "threshold_quantity": float(low_stock_threshold),
                "unit_of_quantity": stock.medicine.category.unit_of_quantity,
                "batch_number": stock.batch_number,
                "alert_id": f"global_{stock.id}",
                "message": f"Low global stock: {available} {stock.medicine.category.unit_of_quantity} remaining",
            }
        )

    # Expiry alerts
    future_date = now.date() + timedelta(days=days_ahead)
    expiring_stocks = MedicineStock.objects.filter(
        expiry_date__lte=future_date, expiry_date__isnull=False
    ).select_related("medicine", "medicine__category")

    for stock in expiring_stocks:
        days_to_expiry = (stock.expiry_date - now.date()).days
        severity = (
            "expired"
            if days_to_expiry < 0
            else "critical" if days_to_expiry <= 7 else "warning"
        )

        alerts.append(
            {
                "type": "global_stock",
                "severity": severity,
                "medicine_name": stock.medicine.medicine,
                "medicine_strength": stock.medicine.strength or "",
                "current_quantity": stock.total_quantity,
                "unit_of_quantity": stock.medicine.category.unit_of_quantity,
                "batch_number": stock.batch_number,
                "expiry_date": stock.expiry_date,
                "days_to_expiry": days_to_expiry,
                "alert_id": f"expiry_{stock.id}",
                "message": f"{'Expired' if days_to_expiry < 0 else 'Expiring in'} {abs(days_to_expiry)} days",
            }
        )

    # 2. User Stock Alerts
    user_low_stocks = (
        UserMedicineStock.objects.annotate(
            remaining=F("allocated_quantity") - F("used_quantity")
        )
        .filter(
            Q(remaining__lte=F("min_threshold"))
            | Q(remaining__lte=F("threshold_quantity"))
        )
        .select_related(
            "user", "medicine_stock__medicine", "medicine_stock__medicine__category"
        )
    )

    for stock in user_low_stocks:
        remaining = stock.remaining_quantity()
        threshold = max(stock.min_threshold, stock.threshold_quantity)

        alerts.append(
            {
                "type": "user_stock",
                "severity": "critical" if remaining <= threshold * 0.5 else "warning",
                "medicine_name": stock.medicine_stock.medicine.medicine,
                "medicine_strength": stock.medicine_stock.medicine.strength or "",
                "current_quantity": remaining,
                "threshold_quantity": threshold,
                "unit_of_quantity": stock.medicine_stock.medicine.category.unit_of_quantity,
                "user_name": stock.user.get_full_name(),
                "user_id": stock.user.id,
                "alert_id": f"user_{stock.id}",
                "message": f"{stock.user.get_full_name()} - Low stock: {remaining} {stock.medicine_stock.medicine.category.unit_of_quantity} remaining",
            }
        )

    # Sort by severity
    severity_order = {"expired": 0, "critical": 1, "warning": 2}
    alerts.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return alerts


def calculate_stock_metrics():
    """
    Calculate comprehensive stock metrics for dashboard
    """
    now = timezone.now()

    # Global metrics
    total_medicine_types = MedicineStock.objects.values("medicine").distinct().count()
    total_stock_batches = MedicineStock.objects.count()

    # Stock status counts
    expired_count = MedicineStock.objects.filter(expiry_date__lt=now.date()).count()
    expiring_soon_count = MedicineStock.objects.filter(
        expiry_date__lte=now.date() + timedelta(days=30), expiry_date__gte=now.date()
    ).count()

    # Low stock count
    low_stock_count = (
        MedicineStock.objects.annotate(
            available=F("total_quantity") - Sum("user_allocations__allocated_quantity")
        )
        .filter(
            Q(available__lte=10) | Q(available__isnull=True, total_quantity__lte=10)
        )
        .count()
    )

    # User allocation metrics
    total_user_allocations = UserMedicineStock.objects.count()
    critical_user_stock_count = (
        UserMedicineStock.objects.annotate(
            remaining=F("allocated_quantity") - F("used_quantity")
        )
        .filter(
            Q(remaining__lte=F("min_threshold"))
            | Q(remaining__lte=F("threshold_quantity"))
        )
        .count()
    )

    # Calculate total stock value if cost information is available
    total_stock_value = 0  # Would need cost field in model

    return {
        "total_medicines": total_medicine_types,
        "total_stock_items": total_stock_batches,
        "total_user_allocations": total_user_allocations,
        "expired_stock_count": expired_count,
        "expiring_soon_count": expiring_soon_count,
        "low_stock_count": low_stock_count,
        "critical_user_stock_count": critical_user_stock_count,
        "total_stock_value": total_stock_value,
        "last_updated": now,
    }


def bulk_stock_update(updates, user):
    """
    Perform bulk stock updates with audit logging
    """
    from ..models.stock_models import MedicineStock, MedicineStockAudit

    success_count = 0
    errors = []

    for update in updates:
        try:
            stock_id = update.get("id")
            new_quantity = update.get("quantity")
            reason = update.get("reason", "Bulk update")
            transaction_type = update.get("transaction_type", "adjustment")

            if not stock_id or new_quantity is None:
                errors.append("Missing stock ID or quantity")
                continue

            stock = MedicineStock.objects.get(id=stock_id)
            old_quantity = stock.total_quantity

            # Validate quantity
            if new_quantity < 0:
                errors.append(f"Stock {stock_id}: Quantity cannot be negative")
                continue

            # Check if reducing stock below allocated amount
            allocated_total = (
                stock.user_allocations.aggregate(total=Sum("allocated_quantity"))[
                    "total"
                ]
                or 0
            )

            if new_quantity < allocated_total:
                errors.append(
                    f"Stock {stock_id}: Cannot reduce below allocated quantity ({allocated_total})"
                )
                continue

            # Update stock
            stock.total_quantity = new_quantity
            stock.save()

            # Create audit log
            if old_quantity != new_quantity:
                audit_transaction_type = "IN" if new_quantity > old_quantity else "OUT"
                quantity_change = abs(new_quantity - old_quantity)

                MedicineStockAudit.objects.create(
                    medicine=stock.medicine,
                    transaction_type=audit_transaction_type,
                    quantity=quantity_change,
                    description=f"{reason} - Changed from {old_quantity} to {new_quantity}",
                    created_by=user,
                )

            success_count += 1

        except MedicineStock.DoesNotExist:
            errors.append(f"Stock with ID {stock_id} not found")
        except Exception as e:
            errors.append(f"Error updating stock {stock_id}: {str(e)}")

    return {
        "success_count": success_count,
        "error_count": len(errors),
        "errors": errors,
    }
