from django.db import models

from orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        INITIATED = 'initiated', 'Initiated'
        COMPLETE = 'complete', 'Complete'
        FAILED = 'failed', 'Failed'
        CANCELED = 'canceled', 'Canceled'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    gateway = models.CharField(max_length=20, default='esewa')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    ref_id = models.CharField(max_length=100, blank=True)
    raw_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment for {self.order} via {self.gateway} ({self.status})'
