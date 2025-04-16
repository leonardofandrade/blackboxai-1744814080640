from django.db import models
from django.contrib.auth.models import User

class ComponentType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class ComponentModel(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} - {self.name}"

    class Meta:
        ordering = ['brand__name', 'name']

class Component(models.Model):
    type = models.ForeignKey(ComponentType, on_delete=models.CASCADE, related_name='components')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='components')
    model = models.ForeignKey(ComponentModel, on_delete=models.CASCADE, related_name='components')
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    specifications = models.JSONField(default=dict)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_components')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['type__name', 'brand__name', 'name']

    def save(self, *args, **kwargs):
        # Generate code if not provided
        if not self.code:
            prefix = f"{self.type.name[:3]}{self.brand.name[:3]}".upper()
            last_component = Component.objects.filter(code__startswith=prefix).order_by('-code').first()
            if last_component:
                try:
                    number = int(last_component.code[6:]) + 1
                except ValueError:
                    number = 1
            else:
                number = 1
            self.code = f"{prefix}{number:04d}"
        super().save(*args, **kwargs)
