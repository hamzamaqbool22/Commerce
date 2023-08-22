from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('listing/<int:listing_id>/close/', views.close_auction, name='close_auction'),
    path('listing/<int:listing_id>/watchlist/', views.add_to_watchlist, name='watchlist'),
    path('place_bid/<int:listing_id>/', views.place_bid, name='place_bid'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),
    path('watchlist/',views.watchlist, name='watchlist' ),
    path('remove_watchlist/<int:listing_id>/', views.remove_from_watchlist, name='remove_watchlist'),
    path('categories/',views.categories, name='categories'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('category/<int:category_id>/', views.category_listings, name='category_listings'),
    path('create_listing/', views.create_listing, name='create_listing')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)