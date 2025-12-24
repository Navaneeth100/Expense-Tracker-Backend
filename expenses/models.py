from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=30, default="❔")  # emoji or text icon

    def __str__(self):
        return f"{self.icon} {self.name}"

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=30, default="❔")  # emoji or text icon

    def __str__(self):
        return f"{self.icon} {self.name}"
    
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.icon} {self.name}"
    
class IncomeType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"



class Expense(models.Model):

    TRANSACTION_CHOICES = (
        ("Income", "Income"),
        ("Expense", "Expense"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # New field
    
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_CHOICES,
        default="Expense"
    )

    # Only used when transaction_type = "expense"

    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    subcategory = models.ForeignKey(
        "SubCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Only used when transaction_type = "income"

    income_type = models.ForeignKey(
        "IncomeType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="expense_created_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"

#  Category Budget

class CategoryBudget(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)

    year = models.IntegerField()
    month = models.IntegerField()  # 1–12

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "category", "year", "month")

    def __str__(self):
        return f"{self.category.name} - {self.month}/{self.year}"
