from django.db import models
from django.contrib.auth.models import User

class Relation(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.from_user} following {self.to_user}'


    def following(self):
        return f'You followed {self.to_user}'

    def followers(self):
        return f'{self.from_user} followed you'