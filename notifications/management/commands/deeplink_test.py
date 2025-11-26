# notifications/management/commands/generate_deeplink.py
from typing import Optional
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from notifications.deeplink_service import DeepLinkService
from notifications.model import DeepLink

User = get_user_model()


PRESET_CONFIGS = {
    "visit-detail": {
        "deeplink_type": "visit-detail",
        "url_name": "visit-detail",
        "route_template": "visits/{{ visit.case_no }}/",
        "fallback_template": "https://kmpcl.netlify.app/vet/visit/",
        "inapp_route": "visits/{{ visit.case_no }}/",
        "expires_in_days": 7,
        "max_uses": 1,
        "meta": {"purpose": "visit_test"},
    },
    "feedback-update": {
        "deeplink_type": "feedback-update",
        # "route_template": "/admin/feedback/feedback/{{ feedback.id }}/change/",
        "fallback_template": "https://kmpcl.netlify.app/feedback/",
        "inapp_route": "/feedback/{{ feedback.pk }}/",
        "expires_in_days": 14,
        "max_uses": 3,
        "meta": {"purpose": "feedback_update"},
    },
    "account-verify": {
        "deeplink_type": "account-verify",
        "url_name": "verify-account",
        "route_template": "auth/verify/{{ user.pk }}/",
        "fallback_template": "https://kmpcl.netlify.app/auth/verify/",
        "inapp_route": "auth/verify/{{ user.pk }}",
        "expires_in_days": 2,
        "max_uses": 1,
        "meta": {"purpose": "verify_test"},
    },
}


class Command(BaseCommand):
    help = "Generate a test deep link (DB record + smart URL) using DeepLinkService."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id", type=int, required=True, help="ID of the user owner"
        )
        parser.add_argument("--count", type=int, required=True, help="Count")

        parser.add_argument(
            "--preset",
            type=str,
            default=None,
            help=f"Use a preset config. Available: {', '.join(PRESET_CONFIGS.keys())}",
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]
        preset_name = options["preset"]
        count = options["count"]

        # optionally apply preset
        preset_config = {}
        if preset_name:
            preset_config = PRESET_CONFIGS.get(preset_name)
            if not preset_config:
                raise CommandError(
                    f"Preset '{preset_name}' not found. Available: {', '.join(PRESET_CONFIGS.keys())}"
                )
            # preset values are used unless overridden by explicit CLI args
            route = (
                preset_config.get("route_template")
                or preset_config.get("inapp_route")
                or ""
            )
            url_name = preset_config.get("url_name")
            fallback = preset_config.get("fallback_template") or preset_config.get(
                "fallback_url"
            )
            expires_days = preset_config.get("expires_in_days")

            max_uses = preset_config.get("max_uses", 0)
            preset_meta = preset_config.get("meta", {})
            meta = preset_meta

        # validate user exists
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise CommandError(f"User with id={user_id} does not exist")

        service = (
            DeepLinkService()
        )  # instantiate your service; adjust if it's different

        created = []

        for i in range(count):
            try:
                # If service exposes generate_deep_link, use it
                if hasattr(service, "generate_deep_link"):
                    smart_url = service.generate_deep_link(
                        user_id=user.pk,
                        url_name=url_name,
                        route_template=route,
                        context={"user": user},
                        fallback_url=fallback,
                        expires_in_days=expires_days,
                        max_uses=max_uses,
                        meta=meta,
                    )

                    # Try find the DB object by token contained in smart_url (best-effort)
                    dl_obj: Optional[DeepLink] = None
                    try:
                        token = smart_url.rstrip("/").split("/")[-1]
                        dl_obj = DeepLink.objects.filter(token=token).first()
                    except Exception:
                        dl_obj = None

                else:
                    # Fallback: create record directly
                    clean_route = route.lstrip("/")
                    if not hasattr(service, "create_deep_link_record"):
                        raise CommandError(
                            "DeepLinkService has neither generate_deep_link nor create_deep_link_record."
                        )
                    dl_obj = service.create_deep_link_record(
                        user_id=user.pk,
                        clean_route=clean_route,
                        url_name=url_name,
                        route_template=route,
                        context={"user": user},
                        fallback_url=fallback,
                        expires_in_days=expires_days,
                        max_uses=max_uses,
                        meta=meta,
                    )
                    if hasattr(service, "smart_url_for_deeplink"):
                        smart_url = service.smart_url_for_deeplink(dl_obj)
                    else:
                        smart_url = (
                            f"{getattr(service, 'SMART_HOST', '')}{dl_obj.token}"
                        )

                # Prepare output
                out = {
                    "token": str(dl_obj.token) if dl_obj else None,
                    "deep_link": dl_obj.deep_link if dl_obj else None,
                    "deep_path": dl_obj.deep_path if dl_obj else None,
                    "smart_url": smart_url,
                    "expires_at": (
                        dl_obj.expires_at.isoformat()
                        if dl_obj and dl_obj.expires_at
                        else None
                    ),
                    "max_uses": dl_obj.max_uses if dl_obj else max_uses,
                    "created_at": dl_obj.created_at.isoformat() if dl_obj else None,
                }
                created.append(out)

            except Exception as e:
                raise CommandError(f"Failed to create deep link (iteration {i}): {e}")

        else:
            self.stdout.write(
                self.style.SUCCESS(f"Created {len(created)} deep link(s).")
            )
