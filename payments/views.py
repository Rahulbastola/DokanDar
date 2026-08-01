from django.shortcuts import redirect
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from .esewa import check_transaction_status, decode_callback_payload, verify_callback_signature
from .models import Payment


class EsewaVerifyView(APIView):
    """
    Handles eSewa's redirect back to success_url (GET ?data=<base64 json>).
    Verifies the payload signature, then double-checks against eSewa's
    server-side status API before marking the order as paid.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data_param = request.query_params.get('data')
        if not data_param:
            return Response({'detail': 'Missing data parameter.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = decode_callback_payload(data_param)
        except Exception:
            return Response({'detail': 'Invalid payment payload.'}, status=status.HTTP_400_BAD_REQUEST)

        if not verify_callback_signature(payload):
            return Response({'detail': 'Signature verification failed.'}, status=status.HTTP_400_BAD_REQUEST)

        transaction_uuid = payload.get('transaction_uuid')
        try:
            order = Order.objects.get(order_id=transaction_uuid)
        except (Order.DoesNotExist, ValueError):
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        status_result = check_transaction_status(
            transaction_uuid=transaction_uuid,
            total_amount=payload.get('total_amount'),
        )

        payment, _ = Payment.objects.get_or_create(order=order, gateway='esewa')
        payment.ref_id = payload.get('transaction_code', '')
        payment.raw_response = str(status_result)

        if payload.get('status') == 'COMPLETE' and status_result.get('status') == 'COMPLETE':
            payment.status = Payment.Status.COMPLETE
            order.status = Order.Status.PAID
            order.transaction_id = payment.ref_id
        else:
            payment.status = Payment.Status.FAILED
            order.status = Order.Status.FAILED

        payment.save()
        order.save(update_fields=['status', 'transaction_id', 'updated_at'])

        return Response({'order_status': order.status, 'payment_status': payment.status})


class EsewaFailureView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        transaction_uuid = request.query_params.get('transaction_uuid') or request.query_params.get('data')
        order = None
        if transaction_uuid:
            order = Order.objects.filter(order_id=transaction_uuid).first()
        if order:
            order.status = Order.Status.FAILED
            order.save(update_fields=['status', 'updated_at'])
            Payment.objects.filter(order=order).update(status=Payment.Status.FAILED)
        return Response({'detail': 'Payment failed or was canceled.'})
