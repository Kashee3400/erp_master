from django.shortcuts import render
from django.http import HttpRequest


def phonepe_return(request: HttpRequest):
    """
    User lands here after paying on PhonePe.
    Show a 'Processing...' page and let frontend poll /status endpoint.
    """

    merchant_txn_id = request.POST.get("merchantTransactionId") or request.GET.get(
        "merchantTransactionId"
    )

    context = {
        "merchant_transaction_id": merchant_txn_id,
    }
    return render(request, "gateway/phonepe/return.html", context)
