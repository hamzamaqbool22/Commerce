from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect,HttpResponseNotAllowed
from django.shortcuts import render , redirect, get_object_or_404
from django.urls import reverse
from .forms import ListingForm , CommentForm 
from django.contrib.auth.decorators import login_required
from .models import User, Listing, Comment, Category,Bid
from decimal import Decimal


def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    return render(request, 'auctions/index.html', {'listings': active_listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")



@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST,request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            form.save_m2m()  
            return redirect('index')
    else:
        form = ListingForm()
    return render(request, 'auctions/create_listing.html', {'form': form})



@login_required
def place_bid(request, listing_id):
    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')
        user = request.user

        listing = get_object_or_404(Listing, pk=listing_id)
        
        bid_amount_decimal = Decimal(bid_amount)

        if bid_amount_decimal >= listing.starting_bid:
            highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()

            if highest_bid is None or bid_amount_decimal > highest_bid.amount:
                Bid.objects.create(user=user, listing=listing, amount=bid_amount)
                return redirect('listing_detail', listing_id=listing_id)
            else:
                return render(request,'auctions/error.html',{ 'message': "Your bid must be higher than the current highest bid."})
        else:
            return render(request,'auctions/error.html',{'message': "Bid amount should be greater than or equal to the starting bid."})
    else:
        return HttpResponseNotAllowed(['POST'])

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = listing.listing_comments.all()
    latest_bid = Bid.objects.filter(listing=listing).order_by('-date').first()
    user = request.user
    has_won= False
    if latest_bid and not listing.is_active and latest_bid.user == user:
        has_won = True

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing = listing
            comment.user = request.user
            comment.save()
            return redirect('listing_detail', listing_id=listing.pk)
    else:
        form = CommentForm()

    context={ 
        'latest_bid': latest_bid,'listing': listing, 'comments': comments, 'form': form,'has_won': has_won, }
    
    return render(request, 'auctions/listing_detail.html', context )



@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    request.user.watchlist.add(listing)
    return redirect('listing_detail', listing_id=listing.pk)

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    request.user.watchlist.remove(listing)
    return redirect('listing_detail', listing_id=listing.pk)

@login_required
def watchlist(request):
    watchlist_items = request.user.watchlist.all()

    return render(request, 'auctions/watchlist.html', {'watchlist_items':watchlist_items})



@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.user == listing.owner:
        listing.is_active = False
        listing.save()

        highest_bid = listing.current_bid
        if highest_bid > 0:
            listing.highest_bidder = request.user
            listing.save()
        
    return redirect('listing_detail', listing_id=listing.pk)



def categories(request):
    categories= Category.objects.all()
    return render (request, 'auctions/categories.html', {'categories':categories})



def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    active_listings = category.listings.filter(is_active=True)
    return render(request, 'auctions/category_listings.html', {'category': category, 'listings': active_listings})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    # Check if the user is the owner of the comment
    if request.user == comment.user:
        comment.delete()

    return redirect('listing_detail', listing_id=comment.listing.pk)

