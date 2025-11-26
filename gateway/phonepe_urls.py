from django.urls import path
from .views import (
    InitiatePaymentView,
    CreateSDKOrderView,
    OrderStatusView,
    InitiateRefundView,
    RefundStatusView,
    PaymentCallbackView,
    phonepe_return,
)

app_name = "gateway"

urlpatterns = [
    path("phonepe/return/", phonepe_return, name="return"),
    # Payment initiation
    path(
        "api/phonepe/initiate/", InitiatePaymentView.as_view(), name="initiate_payment"
    ),
    # SDK order creation (for Flutter in-app payment)
    path(
        "api/phonepe/create-sdk-order/",
        CreateSDKOrderView.as_view(),
        name="create_sdk_order",
    ),
    # Order status
    path(
        "api/phonepe/order-status/<str:merchant_order_id>/",
        OrderStatusView.as_view(),
        name="order_status",
    ),
    # Refund
    path("api/phonepe/refund/", InitiateRefundView.as_view(), name="initiate_refund"),
    path(
        "api/phonepe/refund-status/<str:merchant_refund_id>/",
        RefundStatusView.as_view(),
        name="refund_status",
    ),
    path(
        "phonepe/sdk-callback/",
        PaymentCallbackView.as_view(),
        name="phonepe_sdk_callback",
    ),
]
