from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Create your models here.

class Tag(models.Model):
    name = models.TextField(max_length=20, default="")

    def __str__(self):
        return self.name

    def count(self):
        return self.news_with_tag.count()


class Category(models.Model):
    name = models.TextField(max_length=40, default="", unique=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.TextField(max_length=40, default="")
    url = models.TextField(max_length=200, default="")
    articles_page = models.TextField(max_length=400, default="")
    category = models.ForeignKey(Category, related_name="sources", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.TextField()
    text = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name="news_with_tag")
    slug = models.TextField()
    category = models.ForeignKey(Category, related_name="news_in_category",  on_delete=models.CASCADE, null=True, blank=True)
    source = models.ForeignKey(Source, related_name="news_in_source", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.source.name + ": " + self.title

    def likes_count(self):
        return self.likes.all().count()


class Like(models.Model):
    owner = models.ForeignKey(User, related_name="user_likes", on_delete=models.CASCADE)
    article = models.ForeignKey(News, related_name="likes", on_delete=models.CASCADE)


class Image(models.Model):
    url = models.TextField(max_length=500, default="")
    news = models.ForeignKey(News, related_name="article_images", on_delete=models.CASCADE)


class Comment(models.Model):
    article = models.ForeignKey(News, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="user_comments", on_delete=models.CASCADE)
    comment = models.TextField(max_length=1500, default="")


admin.site.register(News)
admin.site.register(Category)
admin.site.register(Source)
admin.site.register(Image)
admin.site.register(Tag)
admin.site.register(Comment)
