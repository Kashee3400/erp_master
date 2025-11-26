# views.py
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from uuid import uuid4
import logging
import json
from decouple import config

from phonepe.sdk.pg.payments.v2.standard_checkout_client import (
    StandardCheckoutClient,
    CreateSdkOrderRequest,
    RefundRequest,
)
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import (
    StandardCheckoutPayRequest,
)
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo

logger = logging.getLogger(__name__)


class PhonePeClientMixin:
    """Mixin to initialize PhonePe client"""

    @staticmethod
    def get_phonepe_client():
        """Initialize and return PhonePe client"""
        try:
            client = StandardCheckoutClient.get_instance(
                client_id=config("PHONEPE_CLIENT_ID"),
                client_secret=config("PHONEPE_CLIENT_SECRET"),
                client_version=config("PHONEPE_CLIENT_VERSION"),
                env=config("PHONEPE_ENV"),
                should_publish_events=False,
            )
            return client
        except Exception as e:
            logger.error(f"Failed to initialize PhonePe client: {str(e)}")
            raise


@method_decorator(csrf_exempt, name="dispatch")
class InitiatePaymentView(View, PhonePeClientMixin):
    """
    Initiate a new payment transaction

    POST /api/payments/initiate/
    Body: {
        "amount": 100,
        "redirect_url": "https://yourapp.com/payment/callback",
        "udf1": "optional_data_1",
        "udf2": "optional_data_2",
        "udf3": "optional_data_3"
    }
    """

    def post(self, request):
        try:
            # Parse request body
            data = json.loads(request.body)
            amount = data.get("amount")
            redirect_url = data.get("redirect_url")

            # Validation
            if not amount or amount <= 0:
                return JsonResponse(
                    {"success": False, "error": "Invalid amount"}, status=400
                )

            if not redirect_url:
                return JsonResponse(
                    {"success": False, "error": "Redirect URL is required"}, status=400
                )

            # Generate unique order ID
            merchant_order_id = str(uuid4())

            # Optional metadata
            meta_info = MetaInfo(
                udf1=data.get("udf1", ""),
                udf2=data.get("udf2", ""),
                udf3=data.get("udf3", ""),
            )

            # Initialize PhonePe client
            client = self.get_phonepe_client()

            # Create payment request
            pay_request = StandardCheckoutPayRequest.build_request(
                merchant_order_id=merchant_order_id,
                amount=int(amount),
                redirect_url=redirect_url,
                meta_info=meta_info,
            )

            # Initiate payment
            pay_response = client.pay(pay_request)

            # Log transaction
            logger.info(f"Payment initiated: Order ID - {merchant_order_id}")

            return JsonResponse(
                {
                    "status": "success",
                    "data": {
                        "merchant_order_id": merchant_order_id,
                        "checkout_url": pay_response.redirect_url,
                        "amount": amount,
                    },
                },
                status=200,
            )

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Payment initiation failed: {str(e)}")
            return JsonResponse(
                {
                    "success": False,
                    "error": "Payment initiation failed",
                    "details": str(e),
                },
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class CreateSDKOrderView(View, PhonePeClientMixin):
    """
    Create SDK order for in-app payment

    POST /api/phonepe/create-sdk-order/
    Body: {
        "amount": 100,
        "redirect_url": "https://yourapp.com/payment/callback",
        "udf1": "optional_data_1",
        "udf2": "optional_data_2",
        "udf3": "optional_data_3"
    }
    """

    def post(self, request):
        try:
            # Parse request body
            data = json.loads(request.body)
            amount = data.get("amount")
            redirect_url = data.get("redirect_url")

            # Validation
            if not amount or amount <= 0:
                return JsonResponse(
                    {"status": "error", "message": "Invalid amount"}, status=400
                )

            if not redirect_url:
                return JsonResponse(
                    {"status": "error", "message": "Redirect URL is required"},
                    status=400,
                )

            # Generate unique order ID
            merchant_order_id = str(uuid4())

            # Optional metadata
            meta_info = MetaInfo(
                udf1=data.get("udf1", ""),
                udf2=data.get("udf2", ""),
                udf3=data.get("udf3", ""),
            )

            # Initialize PhonePe client
            client = self.get_phonepe_client()

            # Create SDK order request
            sdk_order_request = CreateSdkOrderRequest.build_standard_checkout_request(
                merchant_order_id=merchant_order_id,
                amount=int(amount),
                meta_info=meta_info,
                redirect_url=redirect_url,
            )

            # Create order
            create_order_response = client.create_sdk_order(
                sdk_order_request=sdk_order_request
            )

            # Log transaction
            logger.info(f"SDK Order created: Order ID - {merchant_order_id}")

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Order Created Successfully",
                    "data": {
                        "merchant_order_id": merchant_order_id,
                        "token": create_order_response.token,
                        "amount": amount,
                    },
                },
                status=200,
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"SDK order creation failed: {str(e)}")
            return JsonResponse(
                {
                    "status": "error",
                    "message": "SDK order creation failed",
                    "errors": str(e),
                },
                status=500,
            )


class OrderStatusView(View, PhonePeClientMixin):
    """
    Get order status

    GET /api/payments/order-status/<merchant_order_id>/
    Query params: ?details=true (optional)
    """

    def get(self, request, merchant_order_id):
        try:
            if not merchant_order_id:
                return JsonResponse(
                    {"status": "error", "message": "Order ID is required"}, status=400
                )

            # Get details parameter
            details = request.GET.get("details", "false").lower() == "true"

            # Initialize PhonePe client
            client = self.get_phonepe_client()

            # Get order status
            response = client.get_order_status(
                merchant_order_id=merchant_order_id, details=details
            )

            # Log status check
            logger.info(f"Order status checked: {merchant_order_id} - {response.state}")

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Order status checked: {merchant_order_id} - {response.state}",
                    "data": {
                        "merchant_order_id": merchant_order_id,
                        "state": response.state,
                        "response": response.__dict__ if details else None,
                    },
                },
                status=200,
            )

        except Exception as e:
            logger.error(f"Order status check failed: {str(e)}")
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Failed to get order status",
                    "errors": str(e),
                },
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class InitiateRefundView(View, PhonePeClientMixin):
    """
    Initiate refund for an order

    POST /api/payments/refund/
    Body: {
        "original_order_id": "uuid-of-original-order",
        "amount": 100
    }
    """

    def post(self, request):
        try:
            # Parse request body
            data = json.loads(request.body)
            original_order_id = data.get("original_order_id")
            amount = data.get("amount")

            # Validation
            if not original_order_id:
                return JsonResponse(
                    {"success": "error", "message": "Original order ID is required"},
                    status=400,
                )

            if not amount or amount <= 0:
                return JsonResponse(
                    {"success": "error", "message": "Invalid refund amount"}, status=400
                )

            # Generate unique refund ID
            merchant_refund_id = str(uuid4())

            # Initialize PhonePe client
            client = self.get_phonepe_client()

            # Create refund request
            refund_request = RefundRequest.build_refund_request(
                merchant_refund_id=merchant_refund_id,
                original_merchant_order_id=original_order_id,
                amount=amount,
            )

            # Initiate refund
            refund_response = client.refund(refund_request=refund_request)

            # Log refund
            logger.info(f"Refund initiated: Refund ID - {merchant_refund_id}")

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Refund initiated: Refund ID - {merchant_refund_id}",
                    "data": {
                        "merchant_refund_id": merchant_refund_id,
                        "original_order_id": original_order_id,
                        "state": refund_response.state,
                        "amount": amount,
                    },
                },
                status=200,
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Refund initiation failed: {str(e)}")
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Refund initiation failed",
                    "details": str(e),
                },
                status=500,
            )


class RefundStatusView(View, PhonePeClientMixin):
    """
    Get refund status

    GET /api/payments/refund-status/<merchant_refund_id>/
    """

    def get(self, request, merchant_refund_id):
        try:
            if not merchant_refund_id:
                return JsonResponse(
                    {"success": "error", "message": "Refund ID is required"}, status=400
                )

            # Initialize PhonePe client
            client = self.get_phonepe_client()

            # Get refund status
            refund_response = client.get_refund_status(
                merchant_refund_id=merchant_refund_id
            )

            # Log status check
            logger.info(
                f"Refund status checked: {merchant_refund_id} - {refund_response.state}"
            )

            return JsonResponse(
                {
                    "success": "success",
                    "message": f"Refund status checked: {merchant_refund_id} - {refund_response.state}",
                    "data": {
                        "merchant_refund_id": merchant_refund_id,
                        "state": refund_response.state,
                        "response": refund_response.__dict__,
                    },
                },
                status=200,
            )

        except Exception as e:
            logger.error(f"Refund status check failed: {str(e)}")
            return JsonResponse(
                {
                    "success": False,
                    "message": "Failed to get refund status",
                    "errors": str(e),
                },
                status=500,
            )


from django.http import HttpResponse, JsonResponse


@method_decorator(csrf_exempt, name="dispatch")
class PaymentCallbackView(View):
    """
    Handles server-to-server callback from PhonePe.
    Also returns an HTML page that automatically opens
    the mobile app using deep link:
        kashee://gateway/phonepe/callback?order_id=<merchant_order_id>
    """

    def post(self, request):
        try:
            # Parse callback JSON sent by PhonePe
            data = json.loads(request.body)
            logger.info(f"📩 PhonePe Callback Data: {data}")

            # Extract identifiers
            merchant_order_id = data.get("data", {}).get("merchantTransactionId")

            # Extract metaInfo if needed
            meta = data.get("data", {}).get("metaInfo", {}) or {}
            udf1 = meta.get("udf1")
            udf2 = meta.get("udf2")
            udf3 = meta.get("udf3")

            # Log meta details
            logger.info(f"Callback meta: udf1={udf1}, udf2={udf2}, udf3={udf3}")

            # TODO: Update your order payment status here
            # e.g. PaymentStatus.objects.update(...)
            #      CaseEntry / MilkBill mapping using udf1 & udf2

            # Construct deep link
            deep_link = (
                f"kashee://gateway/phonepe/callback?order_id={merchant_order_id}"
            )

            # HTML auto-redirect page
            html = f"""
            <html>
              <head>
                <title>Redirecting...</title>
                <meta name='viewport' content='width=device-width, initial-scale=1.0'>
              </head>
              <body style='font-family: Arial; text-align: center; margin-top: 40px;'>

                <p>Processing payment… redirecting to Kashee app</p>

                <script>
                    // Auto-open the mobile app
                    window.location.href = "{deep_link}";

                    // After 2 seconds show fallback
                    setTimeout(function() {{
                        document.body.innerHTML = "<h2>Payment Processed</h2><p>You may now return to the Kashee app.</p>";
                    }}, 2000);
                </script>

              </body>
            </html>
            """

            # IMPORTANT:
            # PhonePe expects HTTP 200 OK for callback
            return HttpResponse(html, status=200)

        except Exception as e:
            logger.error(f"❌ Payment callback processing failed: {str(e)}")
            return JsonResponse(
                {
                    "success": False,
                    "error": "Callback processing failed",
                    "details": str(e),
                },
                status=500,
            )
