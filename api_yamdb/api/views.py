from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework_simplejwt.tokens import RefreshToken
from .filters import TitleFilter

from reviews.models import Category, Comment, Genre, Review, Title, User
from .permissions import (AdminOrSuperUserOnly, StaffOrAuthorOrReadOnly,
                          AdminOnly, IsAdminOrReadOnlyPermission,)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, TitleWriteSerializer,
                          UserSerializer, TitleSerializer, UserSerializerOrReadOnly)


class UserViewSet(viewsets.ModelViewSet):
    """API для работы пользователями"""

    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    # permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', ]

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated],
        url_path='me',
    )
    def me(self, request):
        """
        Запрос и возможность редактирования
        информации профиля пользователя.
        """
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        if request.method == 'PATCH':
            serializer = UserSerializerOrReadOnly(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к Review."""
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (StaffOrAuthorOrReadOnly, )

    def create(self, request, *args, **kwargs):
        title_id = kwargs.get('title_id')
        user = request.user
        if Review.objects.filter(author=user, title=title_id).exists():
            return Response({'message': ['У вас уже есть отзыв!',]},
                        status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        user = self.request.user
        serializer.save(author=user, title=title)

    def update(self, request, *args, **kwargs):
        user = request.user
        review_id = self.kwargs.get('pk')
        review = get_object_or_404(Review, id=review_id)
        if not user == review.author:
            return Response({'message': ['Вы исправляете не свой отзыв!',]},
                        status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        user = request.user
        review_id = self.kwargs.get('pk')
        review = get_object_or_404(Review, id=review_id)
        roles = ['moderator', 'admin']
        if not user == review.author and not user.role in roles:
            return Response({'message': ['Вы удаляете не свой отзыв!',]},
                        status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

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

    def update(self, request, *args, **kwargs):
        user = request.user
        comment_id = self.kwargs.get('pk')
        comment = get_object_or_404(Comment, id=comment_id)
        roles = ['moderator', 'admin']
        if not user.role in roles and not user == comment.author:
            return Response({'message': ['Вы исправляете не свой комментарий!',]},
                        status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        comment_id = self.kwargs.get('pk')
        comment = get_object_or_404(Comment, id=comment_id)
        roles = ['moderator', 'admin']
        if not user == comment.author and not user.role in roles:
            return Response({'message': ['Вы удаляете не свой отзыв!',]},
                        status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

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
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnlyPermission]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleWriteSerializer


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к Ganre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class ApiSignup(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        if not request.data:
            return Response(
                {
                    'username': ['username не заполнено'],
                    'email': ['email не заполнено']
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            username = request.data['username']
            if username == 'me':
                return Response({'username': ['username не может быть me',]},
                                status=status.HTTP_400_BAD_REQUEST)
            email = request.data['email']
            user = get_object_or_404(User, username=username)
            obj_for_code = PasswordResetTokenGenerator()
            code = obj_for_code.make_token(user)
            send_mail(
                'Code for api_yambd',
                f'Your code: {code}',
                'check@mail.com',
                [email, ],
            )
            return Response(
                {
                    'username': username,
                    'email': email
                },
                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetToken(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        fields = ['username', 'confirmation_code']
        for field in fields:
            if field not in request.data.keys():
                return Response({field: [f'{field} не заполнено'],},
                status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, username=request.data.get('username'))
        try:
            code = request.data.get('confirmation_code')
            if code == None:
                return Response({'message': ['пустое поле!',]},
                        status=status.HTTP_400_BAD_REQUEST)
            int(code)
        except ValueError:
            pass
        else:
            return Response({'confirmation_code': ['неправильный тип поля!',]},
                        status=status.HTTP_400_BAD_REQUEST)
        obj_for_code = PasswordResetTokenGenerator()
        if obj_for_code.check_token(user, code):
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'message': ['неверный код',]},
                        status=status.HTTP_400_BAD_REQUEST)
