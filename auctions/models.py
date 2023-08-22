from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name='watchlist_users')

User = get_user_model()
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
def upload_listing_image(instance, filename):
    return f"listings/{instance.owner.username}/{filename}"


class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='images/auctions', blank=True, null=True)  
    categories = models.ManyToManyField('Category', related_name="listings")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    is_active = models.BooleanField(default=True)
    comments = models.ManyToManyField('Comment', blank=True, related_name='listing_comments')
    highest_bidder = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="won_listings")


    def __str__(self):
        return self.title


class Bid(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='listing')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f'Bid: {self.amount} by {self.user.username} on {self.listing.title}'
    
class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    Comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} on {self.listing.title}'
