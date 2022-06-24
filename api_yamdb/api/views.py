from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Comment, Genre, Review, Title, User
from .permissions import (AdminOrSuperUserOnly, StaffOrAuthorOrReadOnly,
                          AdminOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    pagination_class = LimitOffsetPagination

    @action(detail=False,
            url_path='me',
            permission_classes=[AllowAny, ],
            methods=['GET', 'DELETE'])
    def user_for_user_admin_moder(self, request):
        if request.method == 'DELETE':
            user = get_object_or_404(User, username=request.user.username)
            user.delete()
            return Response({'message': 'пользователь удалён.'},
                            status=status.HTTP_202_ACCEPTED)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к Review."""
    serializer_class = ReviewSerializer
    permissions_classes = (StaffOrAuthorOrReadOnly,)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(
            Title,
            pk=title_id
        )
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к Comment."""
    serializer_class = CommentSerializer
    permission_classes = (StaffOrAuthorOrReadOnly,)

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)

    def perform_update(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        comment_id = self.kwargs.get('pk')
        author = Comment.objects.get(pk=comment_id).author
        serializer.save(
            author=author,
            review_id=review.id
        )

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all()


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к Title."""
    pass
    # queryset = Title.objects.all().annotate(
    #     Avg("reviews__score")
    # ).order_by("name")
#     serializer_class = TitleSerializer
#     permission_classes = (AdminOrSuperUserOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к Ganre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrSuperUserOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrSuperUserOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class ApiSignup(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = get_object_or_404(User, username=request.data['username'])
            obj_for_code = PasswordResetTokenGenerator()
            code = obj_for_code.make_token(user)
            send_mail(
                'Code for api_yambd',
                f'Your code: {code}',
                'check@mail.com',
                [request.data['email'], ],
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetToken(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        code = request.data['confirmation_code']
        obj_for_code = PasswordResetTokenGenerator()
        if obj_for_code.check_token(user, code):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'message': 'неверный код/пользователь'})
