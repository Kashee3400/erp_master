from django.urls import path
from .views import (
    InitiatePaymentView,
    CheckPaymentStatusView,
    InitiateRefundView,
    RefundStatusView,
    PaymentWebhookView,
    VerifyPaymentView,
)

app_name = "gateway"

urlpatterns = [
    # Payment initiation
    path(
        "api/phonepe/initiate/", InitiatePaymentView.as_view(), name="initiate_payment"
    ),
    # PhonePe calls this webhook (server-to-server)
    path("api/phonepe/webhook/", PaymentWebhookView.as_view(), name="payment_webhook"),
    # Client checks payment status
    path(
        "api/phonepe/order-status/<str:merchant_order_id>/",
        CheckPaymentStatusView.as_view(),
        name="order_status",
    ),
    # Manual verification (optional, for admin use)
    path("api/phonepe/verify/", VerifyPaymentView.as_view(), name="verify_payment"),
    # Refund
    path("api/phonepe/refund/", InitiateRefundView.as_view(), name="initiate_refund"),
    path(
        "api/phonepe/refund-status/<str:merchant_refund_id>/",
        RefundStatusView.as_view(),
        name="refund_status",
    ),
]
