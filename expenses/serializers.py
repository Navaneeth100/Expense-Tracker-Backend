from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, PaymentMethod, IncomeType, Expense

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "icon"]


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ["id", "name"]


class IncomeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeType
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ExpenseSerializer(serializers.ModelSerializer):

    # ---- READ ONLY ----
    category_data = CategorySerializer(source="category", read_only=True)
    payment_method_data = PaymentMethodSerializer(source="payment_method", read_only=True)
    income_type_data = IncomeTypeSerializer(source="income_type", read_only=True)
    created_by = UserSerializer(read_only=True)

    # ---- WRITE ONLY ----
    category = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    income_type = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    payment_method = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Expense
        fields = [
            "id",
            "transaction_type",
            "amount",
            "date",
            "description",

            # GET nested
            "category_data",
            "income_type_data",
            "payment_method_data",
            "created_by",

            # POST input
            "category",
            "income_type",
            "payment_method",

            "created_at",
        ]

    # STEP 1 — Fix empty string BEFORE validation
    def to_internal_value(self, data):
        if data.get("category") == "":
            data["category"] = None
        if data.get("income_type") == "":
            data["income_type"] = None

        return super().to_internal_value(data)

    # STEP 2 — Validate transaction type rules
    def validate(self, data):
        trx = data.get("transaction_type")

        if trx == "Income":
            if not data.get("income_type"):
                raise serializers.ValidationError({"income_type": "income_type required for Income"})
            data["category"] = None

        elif trx == "Expense":
            if not data.get("category"):
                raise serializers.ValidationError({"category": "category required for Expense"})
            data["income_type"] = None

        else:
            raise serializers.ValidationError({"transaction_type": "Invalid type (Income / Expense only)"})

        return data

    # STEP 3 — Create object
    def create(self, validated_data):
        category_id = validated_data.pop("category", None)
        income_type_id = validated_data.pop("income_type", None)
        payment_method_id = validated_data.pop("payment_method", None)

        category = Category.objects.get(id=category_id) if category_id else None
        income_type = IncomeType.objects.get(id=income_type_id) if income_type_id else None
        payment_method = PaymentMethod.objects.get(id=payment_method_id) if payment_method_id else None

        user = self.context["request"].user

        return Expense.objects.create(
            category=category,
            income_type=income_type,
            payment_method=payment_method,
            created_by=user,
            user=user,
            **validated_data
        )

    def update(self, instance, validated_data):
        category_id = validated_data.pop("category", None)
        income_type_id = validated_data.pop("income_type", None)
        payment_method_id = validated_data.pop("payment_method", None)

        trx = validated_data.get("transaction_type", instance.transaction_type)

        # Apply rules
        if trx == "Income":
            instance.category = None
        elif trx == "Expense":
            instance.income_type = None

        # convert IDs → instances
        if category_id:
            instance.category = Category.objects.get(id=category_id)
        if income_type_id:
            instance.income_type = IncomeType.objects.get(id=income_type_id)
        if payment_method_id:
            instance.payment_method = PaymentMethod.objects.get(id=payment_method_id)

        # update normal fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
