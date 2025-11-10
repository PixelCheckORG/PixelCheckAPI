from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from iam.application.use_cases import RegisterUserUseCase, SignInUseCase
from iam.infrastructure.repositories import DjangoUserRepository
from iam.interface.serializers.auth import SignUpSerializer, SignInSerializer


class SignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        use_case = RegisterUserUseCase(DjangoUserRepository())
        result = use_case.execute(**serializer.validated_data)
        if not result.success:
            return Response({"detail": result.error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"userId": result.data.id}, status=status.HTTP_201_CREATED)


class SignInView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        use_case = SignInUseCase()
        result = use_case.execute(**serializer.validated_data)
        return Response(result.data, status=status.HTTP_200_OK)
