from django.contrib import admin
from .models import Category, User, Listing, Comment,Bid

admin.site.register(Category)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Listing)
admin.site.register(Bid)
