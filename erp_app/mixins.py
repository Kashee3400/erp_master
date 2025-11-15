from decimal import Decimal
from django.db import connections


class FastTotalsMixin:
    """
    Mixin to calculate totals (daily/fiscal) from MppCollection using raw SQL.
    """

    @staticmethod
    def calculate_fast_totals(
        member_code, start_date=None, end_date=None, using="sarthak_kashee"
    ):
        """
        Calculate totals:
            - total_qty
            - total_amount
            - weighted_fat
            - weighted_snf
            - total_days
            - total_shift (distinct date + shift)
        Uses raw SQL for maximum speed with existing indexes.
        """
        params = [member_code]
        date_filter = ""
        if start_date and end_date:
            date_filter = "AND collection_date BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        sql = f"""
            SELECT  
                SUM(qty) AS total_qty,
                SUM(amount) AS total_amount,
                SUM(qty * fat) AS qty_fat_sum,
                SUM(qty * snf) AS qty_snf_sum,
                COUNT(DISTINCT CAST(collection_date AS DATE)) AS total_days,
                COUNT(DISTINCT CONCAT(CAST(collection_date AS DATE), '_', CAST(shift_code AS VARCHAR(10)))) AS total_shift
            FROM mpp_collection
            WHERE member_code = %s
            {date_filter};
        """

        with connections[using].cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()

        total_qty = Decimal(row[0] or 0)
        total_amount = Decimal(row[1] or 0)
        qty_fat_sum = Decimal(row[2] or 0)
        qty_snf_sum = Decimal(row[3] or 0)
        total_days = row[4] or 0
        total_shift = row[5] or 0

        epsilon = Decimal("0.00001")
        weighted_fat = float(qty_fat_sum / (total_qty + epsilon)) if total_qty else 0
        weighted_snf = float(qty_snf_sum / (total_qty + epsilon)) if total_qty else 0

        return {
            "total_qty": round(float(total_qty), 2),
            "total_amount": round(float(total_amount), 2),
            "total_payment": round(float(total_amount), 2),
            "avg_fat": round(weighted_fat, 2),
            "avg_snf": round(weighted_snf, 2),
            "total_days": total_days,
            "total_shift": total_shift,
        }

