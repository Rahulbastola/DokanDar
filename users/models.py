from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        ADMIN = 'admin', 'Admin (Vendor)'
        USER = 'user', 'User (Customer)'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    is_approved = models.BooleanField(
        default=False,
        help_text='Admin (vendor) accounts must be approved by a super admin before they can log in as admin.',
    )
    phone = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        # Customers and super admins don't go through an approval workflow.
        if self.role != self.Role.ADMIN:
            self.is_approved = True
        super().save(*args, **kwargs)

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def is_vendor(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return f'{self.username} ({self.role})'
