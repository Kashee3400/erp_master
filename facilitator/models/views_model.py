from django.db import models
from erp_app.models import MemberHierarchyView,Mpp
from django.utils.translation import gettext_lazy as _


class V_PouredMemberSummary(models.Model):
    member = models.ForeignKey(MemberHierarchyView, to_field="member_code", db_column="member_code", on_delete=models.DO_NOTHING)
    mpp = models.ForeignKey(Mpp, to_field="mpp_code", db_column="mpp_code", on_delete=models.DO_NOTHING)
    collection_date = models.DateField()
    total_qty = models.FloatField()
    avg_fat = models.FloatField()
    avg_snf = models.FloatField()

    class Meta:
        managed = False
        db_table = "V_PouredMemberSummary"
        unique_together = ("member", "mpp", "collection_date")
