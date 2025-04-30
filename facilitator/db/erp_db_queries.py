from django.db import connections


def get_poured_mpp_data(collection_date, mpp_codes):
    placeholders = ",".join(["%s"] * len(mpp_codes))  # safely format IN clause
    query = f"""
            SELECT mpp_code, SUM(total_qty) AS total_qty
            FROM V_PouredMemberSummary
            WHERE collection_date = %s AND mpp_code IN ({placeholders})
            GROUP BY mpp_code
        """
    params = [collection_date] + list(mpp_codes)

    with connections["sarthak_kashee"].cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    return [{"mpp_code": row[0], "total_qty": row[1]} for row in rows]


def get_poured_members_from_view(mpp_code, collection_date, using="sarthak_kashee"):
    query = """
        SELECT 
            member_code, mpp_code, collection_date, total_qty, avg_fat, avg_snf
        FROM V_PouredMemberSummary
        WHERE mpp_code = %s AND collection_date = %s
    """
    with connections[using].cursor() as cursor:
        cursor.execute(query, [mpp_code, collection_date])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
