from django.dispatch import receiver
from .model.member_register import (
    MemberRegister,
    MemberHistory,
    MemberBankAccount,
    MemberBankAccountHistory,
)
from django.utils import timezone

from django.db.models.signals import m2m_changed, post_save, post_delete, pre_delete,pre_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from .menu_model import MenuItem, Role, UserMenuPreference
from .menu_config import MenuFilterService

import logging

logger = logging.getLogger(__name__)


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


# ============================================================================
# User Role/Permission Changes
# ============================================================================


@receiver(m2m_changed, sender=User.groups.through)
def invalidate_menu_on_user_group_change(sender, instance, action, **kwargs):
    """Invalidate user's menu cache when their groups change"""
    if action in ["post_add", "post_remove", "post_clear"]:
        tenant_id = (
            getattr(instance, "tenant_id", None)
            if hasattr(instance, "tenant_id")
            else None
        )
        MenuFilterService.invalidate_user_cache(instance.id, tenant_id)
        logger.info(
            f"Menu cache invalidated for user {instance.id} due to group change"
        )


@receiver(m2m_changed, sender=User.user_permissions.through)
def invalidate_menu_on_user_permission_change(sender, instance, action, **kwargs):
    """Invalidate user's menu cache when their permissions change"""
    if action in ["post_add", "post_remove", "post_clear"]:
        tenant_id = (
            getattr(instance, "tenant_id", None)
            if hasattr(instance, "tenant_id")
            else None
        )
        MenuFilterService.invalidate_user_cache(instance.id, tenant_id)
        logger.info(
            f"Menu cache invalidated for user {instance.id} due to permission change"
        )


@receiver(m2m_changed, sender=Group.permissions.through)
def invalidate_menu_on_group_permission_change(sender, instance, action, **kwargs):
    """Invalidate menu cache for all users in a group when group permissions change"""
    if action in ["post_add", "post_remove", "post_clear"]:
        user_ids = instance.user_set.values_list("id", flat=True)
        for user_id in user_ids:
            MenuFilterService.invalidate_user_cache(user_id)
        logger.info(
            f"Menu cache invalidated for {len(user_ids)} users in group {instance.name}"
        )


# ============================================================================
# Menu Structure Changes
# ============================================================================


@receiver(post_save, sender=MenuItem)
def invalidate_all_menus_on_item_save(sender, instance, created, **kwargs):
    """Invalidate all menu caches when menu structure changes"""
    MenuFilterService.invalidate_all_caches()
    logger.info(
        f"All menu caches invalidated due to MenuItem {'creation' if created else 'update'}: {instance.code}"
    )


@receiver(post_delete, sender=MenuItem)
def invalidate_all_menus_on_item_delete(sender, instance, **kwargs):
    """Invalidate all menu caches when menu item is deleted"""
    MenuFilterService.invalidate_all_caches()
    logger.info(
        f"All menu caches invalidated due to MenuItem deletion: {instance.code}"
    )


@receiver(m2m_changed, sender=MenuItem.roles.through)
def invalidate_all_menus_on_item_roles_change(sender, instance, action, **kwargs):
    """Invalidate all menu caches when menu item roles change"""
    if action in ["post_add", "post_remove", "post_clear"]:
        MenuFilterService.invalidate_all_caches()
        logger.info(
            f"All menu caches invalidated due to role change on MenuItem: {instance.code}"
        )


@receiver(m2m_changed, sender=MenuItem.required_permissions.through)
def invalidate_all_menus_on_item_permissions_change(sender, instance, action, **kwargs):
    """Invalidate all menu caches when menu item permissions change"""
    if action in ["post_add", "post_remove", "post_clear"]:
        MenuFilterService.invalidate_all_caches()
        logger.info(
            f"All menu caches invalidated due to permission change on MenuItem: {instance.code}"
        )


# ============================================================================
# Role Changes
# ============================================================================


@receiver(post_save, sender=Role)
def invalidate_menus_on_role_change(sender, instance, **kwargs):
    """Invalidate menu caches when role is modified"""
    if not instance.is_active:
        # Role deactivated - invalidate all users with this role
        user_ids = instance.group.user_set.values_list("id", flat=True)
        for user_id in user_ids:
            MenuFilterService.invalidate_user_cache(user_id)
        logger.info(
            f"Menu caches invalidated for users with deactivated role: {instance.code}"
        )


# ============================================================================
# User Preference Changes
# ============================================================================


@receiver(post_save, sender=UserMenuPreference)
@receiver(post_delete, sender=UserMenuPreference)
def invalidate_menu_on_preference_change(sender, instance, **kwargs):
    """Invalidate user's menu cache when their preferences change"""
    tenant_id = (
        getattr(instance.user, "tenant_id", None)
        if hasattr(instance.user, "tenant_id")
        else None
    )
    MenuFilterService.invalidate_user_cache(instance.user_id, tenant_id)
