from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet
from .views import PaymentMethodViewSet
from .views import IncomeTypeAPI
from .views import ExpenseAPI
from .views import ExpenseSummaryAPI


router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="categories")
router.register("payment-method", PaymentMethodViewSet, basename="payment-method")


urlpatterns = [
    path("income-type/", IncomeTypeAPI.as_view(), name="income-type"),
    path("expense/", ExpenseAPI.as_view(), name="expense"),
    path("expense/<int:id>/", ExpenseAPI.as_view(), name="expense_detail"),
    path("expense-summary/", ExpenseSummaryAPI.as_view(), name="expense-summary"),
]

urlpatterns += router.urls
