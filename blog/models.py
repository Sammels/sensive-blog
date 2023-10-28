from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Prefetch
from django.urls import reverse


class PostQuerySet(models.QuerySet):
    def popular(self):
        sorted_by_likes_count = self.annotate(
            num_likes=Count("likes", distinct=True)
        ).order_by("-num_likes")
        return sorted_by_likes_count

    def fetch_with_comments_count(self):
        """Reduces the number of queries, doing so more efficiently than annotations."""

        most_popular_posts = list(self)
        most_popular_posts_ids = [post.pk for post in most_popular_posts]
        posts_with_comments = Post.objects.filter(
            pk__in=most_popular_posts_ids
        ).annotate(num_comments=Count("comments"))
        ids_and_comments = posts_with_comments.values_list("id", "num_comments")
        ids_and_comments = dict(ids_and_comments)
        for post in most_popular_posts:
            post.num_comments = ids_and_comments[post.pk]
        return most_popular_posts

    def prefetch_tags_with_num_posts(self):
        return self.prefetch_related(
            Prefetch("tags", queryset=Tag.objects.annotate(num_posts=Count("posts")))
        )

    def prefetch_num_likes(self):
        return self.annotate(num_likes=Count("likes", distinct=True))


class TagQuerySet(models.QuerySet):
    def popular(self):
        popular = self.annotate(num_posts=Count("posts")).order_by("-num_posts")
        return popular


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField("Текст")
    slug = models.SlugField("Название в виде url", max_length=200)
    image = models.ImageField("Картинка")
    published_at = models.DateTimeField("Дата и время публикации")

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        limit_choices_to={"is_staff": True},
    )
    likes = models.ManyToManyField(
        User, related_name="liked_posts", verbose_name="Кто лайкнул", blank=True
    )
    tags = models.ManyToManyField("Tag", related_name="posts", verbose_name="Теги")
    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "пост"
        verbose_name_plural = "посты"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", args={"slug": self.slug})


class Tag(models.Model):
    title = models.CharField("Тег", max_length=20, unique=True)
    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse("tag_filter", args={"tag_title": self.slug})

    class Meta:
        ordering = ["title"]
        verbose_name = "тег"
        verbose_name_plural = "теги"


class Comment(models.Model):
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост, к которому написан",
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")

    text = models.TextField("Текст комментария")
    published_at = models.DateTimeField("Дата и время публикации")

    def __str__(self):
        return f"{self.author.username} under {self.post.title}"

    class Meta:
        ordering = ["published_at"]
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"
