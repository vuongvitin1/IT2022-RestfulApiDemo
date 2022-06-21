from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Course, Lesson, Comment, User, Like, Rating, Tag
from .perms import CommentOwnerPermisson
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    LessonSerializer,
    LessonDetailSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    UserSerializer
)
from .paginators import CoursePaginator
from django.http import Http404


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True)
    serializer_class = CategorySerializer

    def get_queryset(self):
        query = self.queryset

        kw = self.request.query_params.get('kw')
        if kw:
            query = query.filter(name__icontains=kw)

        return query


class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_queryset(self):
        query = self.queryset

        kw = self.request.query_params.get('kw')
        if kw:
            query = query.filter(subject__icontains=kw)

        cate_id = self.request.query_params.get('category_id')
        if cate_id:
            query = query.filter(category_id=cate_id)

        return query

    @action(methods=['get'], detail=True, url_path='lessons')
    def get_lessons(self, request, pk):
        # course = Course.objects.get(pk=pk)
        # lessons = course.lessons.filter(active=True)
        lessons = self.get_object().lessons

        kw = request.query_params.get('kw')
        if kw:
            lessons = lessons.filter(subject__icontains=kw)

        return Response(data=LessonSerializer(lessons, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Lesson.objects.filter(active=True)
    serializer_class = LessonDetailSerializer

    def get_permissions(self):
        if self.action in ['like', 'rating']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    # Them tag
    @action(methods=['post'], detail=True, url_path="tags")
    def add_tag(self, request, pk):
        try:
            lesson = self.get_object()
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            tags = request.data.get("tags")
            if tags is not None:
                for tag in tags:
                    t, _ = Tag.objects.get_or_create(name=tag)
                    lesson.tags.add(t)

                lesson.save()
                # Sai
                # return Response(self.serializer_class(lesson, many=True, context={'request': request}).data,
                #                 status=status.HTTP_200_OK)
                return Response(self.serializer_class(lesson,  context={'request': request}).data,
                                status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        lesson = self.get_object()
        comments = lesson.comments.select_related('user')

        return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='like', detail=False)
    def like(self, request, pk):
        lesson = self.get_object()
        user = request.user

        l, _ = Like.objects.get_or_create(lesson=lesson, user=user)
        l.active = not l.active
        l.save()

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['post'], url_path='rating', detail=True)
    def rating(self, request, pk):
        if 'rate' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lesson = self.get_object()
        user = request.user

        r, _ = Rating.objects.get_or_create(lesson=lesson, user=user)
        r.rate = int(request.data.get('rate'))
        r.save()

        return Response(status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ViewSet, generics.CreateAPIView,
                     generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = CreateCommentSerializer

    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [CommentOwnerPermisson()]

        return [permissions.IsAuthenticated()]


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
