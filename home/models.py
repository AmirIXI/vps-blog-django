from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError


import re

def validate_english(value):
    """Validate that the input contains only English letters, numbers, and underscores."""
    if not re.match(r'^[a-zA-Z0-9_ ]*$', value):
        raise ValidationError('Only English letters, numbers, and underscores are allowed.')

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, validators=[validate_english])
    body = models.TextField(validators=[validate_english])  # اگر بخواهید در متن هم محدودیت بگذارید
    slug = models.SlugField(max_length=50, validators=[validate_english])  # اعتبارسنجی برای slug
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.title[:10]} - {self.created}'

    def get_absolute_url(self):
        return reverse('home:post_detail', args=(self.id, self.slug))

    def likes_count(self):
        return self.pvotes.count()


    class Meta:
        ordering = ['-created']


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ucomments') # user send comment
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='pcomments') # for post we send comment
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='rcomments', null=True, blank=True) # blank and null is for not requierd this field
    is_reply = models.BooleanField(default=False)
    body = models.TextField(max_length=400) # comment body
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.body[:30]} - {self.is_reply}'


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uvotes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='pvotes')

    def __str__(self):
        return f'{self.user} - liked -  {self.post.title}'
