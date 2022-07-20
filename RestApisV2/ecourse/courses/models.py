from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField


# Kế thừa lớp user của django để sử dụng các chức năng chứng thực của nó
class User(AbstractUser):
    """
       Những trường có sẵn từ AbstractUser: id, password, last_login, is_superuser,
       username, first_name, last_name, email, is_staff, is_active, date_joined
    """
    avatar = models.ImageField(null=True, upload_to='users/%Y/%m')


class ModelBase(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(ModelBase):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Course(ModelBase):
    subject = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    image = models.ImageField(null=True, blank=True, upload_to='courses/%Y/%m')
    category = models.ForeignKey(Category, related_name="courses", null=True, on_delete=models.SET_NULL)

    class Meta:
        # Ten khoa hoc khong duoc cung voi ten danh muc
        unique_together = ('subject', 'category')
        # Sap xep giam theo id
        # ordering = ["-id"]

    def __str__(self):
        return self.subject


class Lesson(ModelBase):
    subject = models.CharField(max_length=255)
    # content = models.TextField()
    content = RichTextField()
    image = models.ImageField(null=True, upload_to='lessons/%Y/%m')
    # de trong view cua Coursee duoc phep .lessons vi du lessons = self.get_object().lessons.filter(active=True)
    course = models.ForeignKey(Course,
                               related_name='lessons',
                               related_query_name='my_lesson',
                               on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', related_name="lessons", blank=True)

    def __str__(self):
        return self.subject

    class Meta:
        # Ten bai hoc khong duoc cung voi ten khoa hoc
        unique_together = ('subject', 'course')


class Tag(ModelBase):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Comment(ModelBase):
    content = models.CharField(max_length=255)
    lesson = models.ForeignKey(Lesson, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class ActionBase(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        unique_together = ('user', 'lesson')


# class Action(ActionBase):
#     LIKE, HAHA, HEART = range(3)
#     ACTIONS = [
#         (LIKE, 'like'),
#         (HAHA, 'haha'),
#         (HEART, 'heart')
#     ]
#     type = models.PositiveSmallIntegerField(choices=ACTIONS, default=LIKE)


class Rating(ActionBase):
    rate = models.PositiveSmallIntegerField(default=0)


class Like(ActionBase):
    active = models.BooleanField(default=False)


# class Rating(ActionBase):
#     rate = models.SmallIntegerField(default=0)
class LessonView(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    # 1 lesson thi co duy nhat 1 gia tri trong truong views
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
