from typing import Union

from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Course, Lesson, Comment, User, Rating, Tag, Like, Rating, LessonView
from .perms import CommentOwnerPermisson
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    LessonSerializer,
    LessonDetailSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    UserSerializer,
    # ActionSerializer,
    RatingSerializer,
    LessonViewSerializer
)
from .paginators import CoursePaginator
from django.http import Http404
from django.db.models import F
from django.conf import settings


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
        # course = Course.objects.get(pk=pk).lessons.filter(active=True)
        # kw = self.request.query_params.get('kw')
        # if kw is not None:
        #     lessons = lessons.filter(subject__icontains=kw)
        lessons = self.get_object().lessons.filter(active=True)
        # tu khoa tim kiem q khong duoc trung voi cac tu khoa khac trong course
        kw = self.request.query_params.get('q')
        if kw is not None:
            # icontains -> khong phan biet hoa thuong khi tim kiem
            lessons = lessons.filter(subject__icontains=kw)

        return Response(data=LessonSerializer(lessons, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Lesson.objects.filter(active=True)
    serializer_class = LessonDetailSerializer

    def get_permissions(self):
        if self.action == 'add_comment':
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    def get_permissions(self):
        if self.action in ['like', 'rating', 'take_action', 'rate']:
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
            # lay tat ca cac tag
            tags = request.data.get("tags")
            if tags is not None:
                for tag in tags:
                    # neu chua co thi tao ra co roi thi add vo list tag
                    t, _ = Tag.objects.get_or_create(name=tag)
                    lesson.tags.add(t)

                lesson.save()
                # Sai
                # return Response(self.serializer_class(lesson, many=True, context={'request': request}).data,
                #                 status=status.HTTP_200_OK)
                return Response(self.serializer_class(lesson, context={'request': request}).data,
                                status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=True, url_path="add-comment")
    def add_comment(self, request, pk):
        content = request.data.get('content')
        if content:
            c = Comment.objects.create(content=content, lesson=self.get_object(), user=request.user)

            return Response(CommentSerializer(c, context={'request': request}).data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        lesson = self.get_object()
        comments = lesson.comments.select_related('user')

        return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)

    # @action(methods=['post'], detail=True, url_path='like')
    # def take_action(self, request, pk):
    #     try:
    #         action_type = int(request.data['type'])
    #     except Union[IndexError, ValueError]:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         ac = Action.objects.create(type=action_type, user=request.user, lesson=self.get_object())
    #
    #         return Response(ActionSerializer(ac).data, status=status.HTTP_200_OK)
    #
    #     return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path='rating')
    def rate(self, request, pk):
        try:
            rating = int(request.data['rating'])
        except Union[IndexError, ValueError] as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            r = Rating.objects.create(rate=rating, user=request.user, lesson=self.get_object())

            return Response(RatingSerializer(r).data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], url_path='like', detail=True)
    def like(self, request, pk):
        lesson = self.get_object()
        user = request.user

        l, _ = Like.objects.get_or_create(lesson=lesson, user=user)
        l.active = not l.active
        l.save()

        return Response(status=status.HTTP_201_CREATED)

    # @action(methods=['post'], url_path='rating', detail=True)
    # def rating(self, request, pk):
    #     if 'rate' not in request.data:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)
    #
    #     lesson = self.get_object()
    #     user = request.user
    #
    #     r, _ = Rating.objects.get_or_create(lesson=lesson, user=user)
    #     r.rate = int(request.data.get('rate'))
    #     r.save()
    #
    #     return Response(status=status.HTTP_201_CREATED)
    # API tang so view
    @action(methods=['get'], detail=True, url_path='views')
    def incre_view(self, request, pk):
        v, created = LessonView.objects.get_or_create(lesson=self.get_object())
        # v.views += 1
        # trong moi truong phan tan phai
        v.views = F('views') + 1

        v.save()
        # cap nhat cho v.views thanh so chu khon phai mac dinh là object
        v.refresh_from_db()

        return Response(LessonViewSerializer(v).data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet, generics.CreateAPIView,
                     generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = CreateCommentSerializer

    # user 2 sao van sua comment cua user co id la 1 được?
    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [CommentOwnerPermisson()]

        return [permissions.IsAuthenticated()]


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'get_current_user':
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='current-user')
    def get_current_user(self, request):
        return Response(self.serializer_class(request.user, context={'request': request}).data, status=status.HTTP_200_OK)


class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)
