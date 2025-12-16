from django.shortcuts import render

#  Register User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import MenuList
from .serializers import MenuListSerializer

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # 1️⃣ Find user with this email
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        # 2️⃣ Authenticate using username (Django uses username internally)
        user = authenticate(username=user_obj.username, password=password)

        if user is None:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        # 3️⃣ Generate tokens
        refresh = RefreshToken.for_user(user)

        # 4️⃣ Fetch Menu List
        menu_items = MenuList.objects.all().order_by("menu_name")
        menu_data = MenuListSerializer(menu_items, many=True).data

        return Response({
            "message": "User Login successfully",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "menu": menu_data
        }, status=status.HTTP_200_OK)
        
    


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]


class MenuListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        if id:
            try:
                item = MenuList.objects.get(id=id)
                serializer = MenuListSerializer(item)
                return Response(serializer.data, status=200)
            except MenuList.DoesNotExist:
                return Response({"error": "Menu not found"}, status=404)

        # GET all
        items = MenuList.objects.all().order_by("menu_name")
        serializer = MenuListSerializer(items, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = MenuListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Menu created successfully"}, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, id=None):
        if not id:
            return Response({"error": "ID required in URL"}, status=400)

        try:
            item = MenuList.objects.get(id=id)
        except MenuList.DoesNotExist:
            return Response({"error": "Menu not found"}, status=404)

        serializer = MenuListSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Updated successfully"}, status=200)

        return Response(serializer.errors, status=400)

    def delete(self, request, id=None):
        if not id:
            return Response({"error": "ID required in URL"}, status=400)

        try:
            item = MenuList.objects.get(id=id)
        except MenuList.DoesNotExist:
            return Response({"error": "Menu not found"}, status=404)

        item.delete()
        return Response({"message": "Deleted successfully"}, status=200)
