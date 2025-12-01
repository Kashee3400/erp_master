from django.db.models.signals import pre_save
from django.dispatch import receiver
from .model.member_register import (
    MemberRegister,
    MemberHistory,
    MemberBankAccount,
    MemberBankAccountHistory,
)
from django.utils import timezone


@receiver(pre_save, sender=MemberRegister)
def create_member_history(sender, instance, **kwargs):
    """Create history record before Member update"""
    if instance.pk:
        try:
            old_instance = MemberRegister.objects.get(pk=instance.pk)
            MemberHistory.objects.create(
                member=instance,
                full_name=old_instance.full_name,
                status=old_instance.status,
                gender=old_instance.gender,
                date_of_birth=old_instance.date_of_birth,
                mcc=old_instance.mcc,
                mpp=old_instance.mpp,
                valid_from=old_instance.updated_at,
                changed_by=instance.updated_by,
                snapshot_data={
                    "full_name": old_instance.full_name,
                    "status": old_instance.status,
                    "member_code": old_instance.member_code,
                    # Add other relevant fields
                },
            )
            # Close previous history record
            MemberHistory.objects.filter(member=instance, valid_to__isnull=True).update(
                valid_to=timezone.now()
            )
        except MemberRegister.DoesNotExist:
            pass


@receiver(pre_save, sender=MemberBankAccount)
def create_bank_account_history(sender, instance, **kwargs):
    """Create history record before bank account update"""
    if instance.pk:
        try:
            old_instance = MemberBankAccount.objects.get(pk=instance.pk)
            MemberBankAccountHistory.objects.create(
                bank_account=instance,
                account_holder_name=old_instance.account_holder_name,
                account_number_last_4=old_instance.account_number_last_4,
                ifsc_code=old_instance.ifsc_code,
                bank_name=old_instance.bank_name or "",
                valid_from=old_instance.updated_at,
                changed_by=instance.updated_by,
                snapshot_data={
                    "account_holder_name": old_instance.account_holder_name,
                    "ifsc_code": old_instance.ifsc_code,
                    # Add other fields
                },
            )
        except MemberBankAccount.DoesNotExist:
            pass
