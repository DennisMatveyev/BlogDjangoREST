from django.db.models import Q

from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.generics import (ListAPIView,
                                     CreateAPIView,
                                     RetrieveAPIView,
                                     RetrieveUpdateAPIView,
                                     DestroyAPIView)

from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from posts.models import Post
from .pagination import PostPageNumberPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (PostListSerializer,
                          PostDetailSerializer,
                          PostCreateUpdateSerializer)


class PostListAPIView(ListAPIView):
    serializer_class = PostListSerializer
    pagination_class = PostPageNumberPagination    # PostLimitOffsetPagination

    # in url - ?search=... - seeking in search_fields
    # and ordering - &ordering=...
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content', 'user__first_name']

    def get_queryset(self, *args, **kwargs):
        queryset_list = Post.objects.all()
        query = self.request.GET.get("q")   # narrow the searching, in url - ?search=...&q=...
        if query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            ).distinct()

        return queryset_list


class PostCreateAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'


class PostUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateUpdateSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
