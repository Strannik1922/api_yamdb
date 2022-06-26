from rest_framework import serializers, status
from rest_framework.response import Response
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер вьюсета User."""
    # Теперь поле примет только значение, упомянутое в списке CHOICES
    # username = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('first_name', 'last_name', 'bio', 'role',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер вьюсета Review."""
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = (
            'author', 'text', 'pub_date', 'title', 'rating'
        )


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер вьюсета Comment."""
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment


class GenreSerializer(serializers.ModelSerializer):
    """Сериалайзер вьюсета Genre."""
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    """Сериалайзер вьюсета Title."""
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')


class CategorySerializer(serializers.ModelSerializer):
    """Сериалайзер вьюсета Category."""
    class Meta:
        model = Category
        exclude = ('id',)
