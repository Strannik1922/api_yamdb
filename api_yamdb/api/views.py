from rest_framework import filters, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from reviews.models import Comment, Genre, Review, Title, User

from .permissions import AdminOrSuperUserOnly, StaffOrAuthorOrReadOnly
from .serializers import (CommentSerializer, GenreSerializer, ReviewSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для API к User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOrSuperUserOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)


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
    pass
