from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, permissions
from .models import Category
from .models import PaymentMethod
from .models import IncomeType
from .models import Expense
from .models import CategoryBudget
from .serializers import CategorySerializer
from .serializers import PaymentMethodSerializer
from .serializers import IncomeTypeSerializer
from .serializers import ExpenseSerializer
from .serializers import CategoryBudgetSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]  

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all().order_by("name")
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated] 

class IncomeTypeAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # ✔ GET ALL INCOME TYPE

    def get(self, request):
        types = IncomeType.objects.all().order_by("name")
        serializer = IncomeTypeSerializer(types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ✔ CREATE NEW INCOME TYPE

    def post(self, request):
        serializer = IncomeTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Income type created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ✔ UPDATE INCOME TYPE

    def put(self, request):
        id = request.data.get("id")
        if not id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exp_type = IncomeType.objects.get(id=id)
        except IncomeType.DoesNotExist:
            return Response({"error": "Income type not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = IncomeTypeSerializer(exp_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ✔ DELETE INCOME TYPE
    
    def delete(self, request):
        id = request.data.get("id")
        if not id:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exp_type = IncomeType.objects.get(id=id)
        except IncomeType.DoesNotExist:
            return Response({"error": "Income type not found"}, status=status.HTTP_404_NOT_FOUND)

        exp_type.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_200_OK)
    


    
class ExpenseAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # GET all expenses for logged-in user
    def get(self, request):
        expenses = Expense.objects.filter(user=request.user).order_by("-date")
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=200)

    # CREATE Expense

    def post(self, request):
        serializer = ExpenseSerializer(
            data=request.data,
            context={"request": request}   # IMPORTANT FIX
        )
        
        if serializer.is_valid():
            serializer.save()  # created_by and user handled inside serializer
            return Response({"message": "Expense added successfully"}, status=201)
        
        return Response(serializer.errors, status=400)

    # UPDATE

    def put(self, request, id):

        try:
            expense = Expense.objects.get(id=id, user=request.user)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=404)

        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Expense updated successfully"})
        return Response(serializer.errors, status=400)

    # DELETE

    def delete(self, request, id):

        expense = Expense.objects.get(id=id, user=request.user)

        try:
            expense = Expense.objects.get(id=id, user=request.user)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=404)

        expense.delete()
        return Response({"message": "Expense deleted successfully"})

from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

class ExpenseSummaryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        total_income = Expense.objects.filter(
            user=user, transaction_type="Income"
        ).aggregate(total=Sum("amount"))["total"] or 0

        total_expense = Expense.objects.filter(
            user=user, transaction_type="Expense"
        ).aggregate(total=Sum("amount"))["total"] or 0

        total_balance = total_income - total_expense


        # CATEGORY-WISE TOTAL EXPENSE (Graph)

        category_data = (
            Expense.objects.filter(user=user, transaction_type="Expense")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        graph_data = [
            {
                "category": item["category__name"],
                "total": item["total"] or 0
            }
            for item in category_data
        ]

        #  HIGHEST SPENDING CATEGORY

        highest_category = graph_data[0] if graph_data else None
        lowest_category = graph_data[-1] if graph_data else None

        return Response({
            "total_income": total_income,
            "total_expense": total_expense,
            "total_balance": total_balance,
            "highest_category": highest_category,
            "lowest_category": lowest_category,
            "graph_data": graph_data
        })
    

from datetime import date

class CategoryBudgetAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()

        budgets = CategoryBudget.objects.filter(
            user=user,
            month=today.month,
            year=today.year
        )

        result = []

        for budget in budgets:
            spent = Expense.objects.filter(
                user=user,
                category=budget.category,
                transaction_type="Expense",
                date__month=today.month,
                date__year=today.year
            ).aggregate(total=Sum("amount"))["total"] or 0

            spent = spent or 0
            limit = budget.monthly_limit

            # Remaining should not go below 0

            remaining = max(limit - spent, 0)

            # Percent used should not exceed 100
            
            if limit > 0:
                percent_used = min((spent / limit) * 100, 100)
            else:
                percent_used = 0

            percent_remains = max(100 - percent_used, 0)

            result.append({
                "id": budget.id,
                "category": {
                    "id": budget.category.id,
                    "name": budget.category.name
                },
                "budget": budget.monthly_limit,
                "spent": spent,
                "remaining": remaining,
                "percent_used": round(percent_used, 2),
                "percent_remains": round(percent_remains, 2),
                "over_budget": spent > budget.monthly_limit
            })

        return Response(result)

    def post(self, request):
        serializer = CategoryBudgetSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Budget saved"}, status=201)
        return Response(serializer.errors, status=400)
    
    # UPDATE

    def put(self, request, id):

        try:
            categorybudget = CategoryBudget.objects.get(id=id, user=request.user)
        except CategoryBudget.DoesNotExist:
            return Response({"error": "Category Budget not found"}, status=404)

        serializer = CategoryBudgetSerializer(categorybudget, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category Budget updated successfully"})
        return Response(serializer.errors, status=400)
    
    # DELETE

    def delete(self, request, id):

        try:
            categorybudget = CategoryBudget.objects.get(id=id, user=request.user)
        except CategoryBudget.DoesNotExist:
            return Response({"error": "Category Budget not found"}, status=404)

        categorybudget.delete()
        return Response({"message": "Category Budget deleted successfully"})