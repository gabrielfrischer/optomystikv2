from django.shortcuts import render, get_object_or_404
from .models import Category, Dish, DishImages, Cart, Order, OrderInfo, BillingAddress, ContactUs, Review
from users.models import CustomUser, Profile
from django.contrib.auth import login, logout
from django.contrib import messages
from django.shortcuts import redirect, reverse, render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .forms import OrderInfoForm, BillingAddressForm, ContactUsUnauthenticated, ReviewForm
from django.forms import inlineformset_factory, modelformset_factory
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader
from django.forms.models import model_to_dict
import stripe
from django.conf import settings

# Create your views here.
def home(request):
    categories = Category.objects.all()
    dishimages = DishImages.objects.all()
    reviews = Review.objects.filter(rating=5)
    request.session['guest'] = False
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review was successfully posted.')
            return redirect('home')
        else:
            messages.info(request, 'Your review form is invalid, please fill out all the fields in the proper format.')
            return redirect('home')

    else:
        form = ReviewForm()
    context = {"categories":categories, "dishimages":dishimages, "form":form, 'reviews':reviews}
    return render(request, "recipes/home.html", context)

def category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    context = {
        'category':category
    }
    return render(request, 'recipes/category.html', context)

def dish(request, category_slug, dish_slug, openpics):
    category = Category.objects.get(slug=category_slug)
    dish = category.dishes.get(slug=dish_slug)
    if 'HTTP_REFERER' in request.META and openpics == 1 :
        referer = request.META['HTTP_REFERER'].split('/')[-2] 
        print(referer, category_slug)
        print('Refererer Exists', True)
        context = {"category":category, "dish":dish, 'trigger_pics':True}
    elif openpics == 0:
        print('Refererer Exists', False)
        context = {"category":category, "dish":dish, 'trigger_pics':False}
    else: 
        context = {"category":category, "dish":dish, 'trigger_pics':False}
    return render(request, 'recipes/dish.html', context)


def logoutview(request):
    logout(request)
    messages.success(request, "You've successfully logged out.") #send success message
    return redirect('home')


def cart(request):
    if request.user.is_authenticated:
        cart_qs = Cart.objects.filter(user=request.user, purchased=False)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists() and cart_qs.exists():
            order = order_qs[0]
            return render(request, 'recipes/cart.html', {'cart':cart_qs,'order':order} )
        else:
            messages.info(request, "You have nothing in your cart. Add to your order to view your cart.")
            return redirect('home')
    else:
        session_id = request.session.session_key
        cart_qs = Cart.objects.filter(session=session_id, purchased=False)
        order_qs = Order.objects.filter(session=session_id, ordered=False)
        if order_qs.exists() and cart_qs.exists():
            order = order_qs[0]
            return render(request, 'recipes/cart.html', {'cart':cart_qs,'order':order} )
        else:
            messages.info(request, "You have nothing in your cart. Add to your order to view your cart.")
            return redirect('home')
        context = {
            'cart':request.session['cart'],
            'order':order
            } 
        return render(request, 'recipes/cart.html', context )


def past_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user, ordered=True)
        return render(request, 'recipes/orders.html', {"order":orders})
    else:
        messages.info(request, "Sign up or login to view your orders.")
        return redirect('home')
        



def add_to_cart(request, dish_slug):
    if request.user.is_authenticated:
        dish = get_object_or_404(Dish, slug=dish_slug) #capture dish they want to add to cart via slug on button click
        category_slug = None
        product_slug = None
        if 'HTTP_REFERER' in request.META:
            if 'category' in request.META['HTTP_REFERER']:
                print('Category Referer: ',request.META['HTTP_REFERER'])
                category_slug = request.META['HTTP_REFERER'].split('/')[-2]
            if 'product' in request.META['HTTP_REFERER']:
                print('Product Referer: ',request.META['HTTP_REFERER'])
                cat_slug = request.META['HTTP_REFERER'].split('/')[-4]
                product_slug = request.META['HTTP_REFERER'].split('/')[-3]
                print('Product Slug', product_slug)
                print('Cat Slug', cat_slug)

        cart_item, created = Cart.objects.get_or_create( 
            item = dish,
            user = request.user,
            purchased=False
        ) # Make cart object, and create boolean of whether it was in the user's cart already (created=False) or it had to be created (created=True)
        order_qs = Order.objects.filter(user=request.user, ordered=False) #get queryset of unfulfilled order for that user
        if order_qs.exists(): #if that unfulfilled order qs has unfulfilled order 
            order = order_qs[0] #then capture that unfulfilled order object within the queryset
            if order.orderitems.filter(item__slug=dish.slug).exists():
                cart_item.quantity +=1
                cart_item.save()
                strQuantity = str(cart_item.quantity)
                messages.info(request, f"You added 1 more {dish.name} to your cart. You now have a total of {strQuantity} orders of {dish.name}'s in your cart.")
                if category_slug is not None:
                    print('Redirecting to category')
                    return redirect('category', category_slug=category_slug)
                if product_slug is not None:
                    print('Redirecting to product')
                    return redirect('dish', category_slug=cat_slug, dish_slug=product_slug, openpics=0)
            else:
                order.orderitems.add(cart_item)
                messages.info(request, "One order of %s is now in your cart."%dish.name)
                if category_slug is not None:
                    print('Redirecting to category')
                    return redirect('category', category_slug=category_slug)
                if product_slug is not None:
                    print('Redirecting to product')
                    return redirect('dish', category_slug=cat_slug, dish_slug=product_slug, openpics=0)
        else: #otherwise, if unfulfilled order doesnt exist 
            order = Order.objects.create(user=request.user) # create an unfulfilled order for that user, save it to database
            order.orderitems.add(cart_item) # add dish to empty order
            messages.info(request, "One order of %s was added to your cart."%dish.name)
            if category_slug is not None:
                print('Redirecting to category')
                return redirect('category', category_slug=category_slug)
            if product_slug is not None:
                print('Redirecting to product')
                return redirect('dish', category_slug=cat_slug, dish_slug=product_slug, openpics=0)
    else:
        category_slug = None
        product_slug = None
        if 'HTTP_REFERER' in request.META:
            if 'category' in request.META['HTTP_REFERER']:
                print('Category Referer: ',request.META['HTTP_REFERER'])
                category_slug = request.META['HTTP_REFERER'].split('/')[-2]
            if 'product' in request.META['HTTP_REFERER']:
                print('Product Referer: ',request.META['HTTP_REFERER'])
                cat_slug = request.META['HTTP_REFERER'].split('/')[-4]
                product_slug = request.META['HTTP_REFERER'].split('/')[-3]
                print('Product Slug', product_slug)
                print('Cat Slug', cat_slug)
        dish = get_object_or_404(Dish, slug=dish_slug)
        if not request.session.session_key:
            request.session.create()
            session_id = request.session.session_key
        session_id = request.session.session_key
        print('Session ID: ',session_id)

        cart_item, created = Cart.objects.get_or_create( 
            item = dish,
            session = session_id,
            purchased=False
        )
        order_qs = Order.objects.filter(session = session_id, ordered=False) #get queryset of unfulfilled order for that user
        if order_qs.exists(): #if that unfulfilled order qs has unfulfilled order 
            order = order_qs[0] #then capture that unfulfilled order object within the queryset
            if order.orderitems.filter(item__slug=dish.slug).exists():
                cart_item.quantity +=1
                cart_item.save()
                strQuantity = str(cart_item.quantity)
                request.session['total_quantity'] = order.get_total_quantity()
                request.session.save()
                messages.info(request, f"You added 1 more {dish.name} to your cart. You now have a total of {strQuantity} orders of {dish.name}'s in your cart.")
                if category_slug is not None:
                    print('Redirecting to category')
                    return redirect('category', category_slug=category_slug)
                if product_slug is not None:
                    print('Redirecting to product')
                    return redirect('dish', category_slug=cat_slug, dish_slug=product_slug, openpics=0)
            else:
                order.orderitems.add(cart_item)
                request.session['total_quantity'] = order.get_total_quantity()
                messages.info(request, "One order of %s is now in your cart."%dish.name)
                if category_slug is not None:
                    print('Redirecting to category')
                    return redirect('category', category_slug=category_slug)
                if product_slug is not None:
                    print('Redirecting to product')
                    return redirect('dish', category_slug=cat_slug, dish_slug=product_slug, openpics=0)
        else: #otherwise, if unfulfilled order doesnt exist 
            order = Order.objects.create(session = session_id) # create an unfulfilled order for that user, save it to database
            order.orderitems.add(cart_item) # add dish to empty order
            request.session['total_quantity'] = order.get_total_quantity()
            messages.info(request, "One order of %s was added to your cart."%dish.name)
            if category_slug is not None:
                print('Redirecting to category')
                return redirect('category', category_slug=category_slug)
            if product_slug is not None:
                print('Redirecting to product')
                return redirect('dish', category_slug=cat_slug, dish_slug=product_slug, openpics=0)

def add_in_cart(request, dish_slug):
    if request.user.is_authenticated:
        dish = get_object_or_404(Dish, slug=dish_slug) #capture dish they want to add to cart via slug on button click
        cart_item, created = Cart.objects.get_or_create( 
            item = dish,
            user = request.user,
            purchased = False
        ) # Make cart object, and create boolean of whether it was in the cart already (created=False) or it had to be created (created=True)
        order_qs = Order.objects.filter(user=request.user, ordered=False) #get queryset of unfulfilled order for that user
        if order_qs.exists() and not created: #if that unfulfilled order qs has unfulfilled order 
            order = order_qs[0] #then capture that unfulfilled order object within the queryset
            if order.orderitems.filter(item__slug=dish.slug).exists():
                cart_item.quantity +=1
                cart_item.save()
                strQuantity = str(cart_item.quantity)
                messages.info(request, f"You added 1 more {dish.name} to your cart. You now have a total of {strQuantity} orders of {dish.name}'s in your cart.")
                return redirect('cart')
            else:
                order.orderitems.add(cart_item)
                messages.info(request, "One order of %s is now in your cart."%dish.name)
                return redirect('cart')
        else: #otherwise, if unfulfilled order doesnt exist 
            order = Order.objects.create(user=request.user) # create an unfulfilled order for that user, save it to database
            order.orderitems.add(cart_item) # add dish to empty order
            messages.info(request, "One order of %s was added to your cart."%dish.name)
            return redirect('cart')
    else:
        dish = get_object_or_404(Dish, slug=dish_slug) #capture dish they want to add to cart via slug on button click
        session_id = request.session.session_key
        cart_item, created = Cart.objects.get_or_create( 
            item = dish,
            session = session_id,
            purchased = False
        ) # Make cart object, and create boolean of whether it was in the cart already (created=False) or it had to be created (created=True)
        order_qs = Order.objects.filter(session = session_id, ordered=False) #get queryset of unfulfilled order for that user
        if order_qs.exists() and not created: #if that unfulfilled order qs has unfulfilled order 
            order = order_qs[0] #then capture that unfulfilled order object within the queryset
            if order.orderitems.filter(item__slug=dish.slug).exists():
                cart_item.quantity +=1
                cart_item.save()
                request.session['total_quantity'] = order.get_total_quantity()
                request.session.save()
                strQuantity = str(cart_item.quantity)
                messages.info(request, f"You added 1 more {dish.name} to your cart. You now have a total of {strQuantity} orders of {dish.name}'s in your cart.")
                return redirect('cart')
            else:
                order.orderitems.add(cart_item)
                request.session['total_quantity'] = order.get_total_quantity()
                request.session.save()
                messages.info(request, "One order of %s is now in your cart."%dish.name)
                return redirect('cart')
        else: #otherwise, if unfulfilled order doesnt exist 
            order = Order.objects.create(session = session_id) # create an unfulfilled order for that user, save it to database
            order.orderitems.add(cart_item) # add dish to empty order
            request.session['total_quantity'] = order.get_total_quantity()
            request.session.save()
            messages.info(request, "One order of %s was added to your cart."%dish.name)
            return redirect('cart')
        messages.warning(request,"You must be signed in to create orders. Sign up for an account or login to your existing account.")
        return redirect('home')

def remove_from_cart(request, dish_slug, pk):
    if request.user.is_authenticated:   
        item = get_object_or_404(Dish, slug=dish_slug)
        cart_qs = Cart.objects.filter(user=request.user, item=item, pk=pk)
        if cart_qs.exists():
            cart = cart_qs[0]
        # Checking the cart quantity
            if cart.quantity > 1:
                cart.quantity -= 1
                cart.save()
                strQuantity = str(cart.quantity)
                messages.info(request, f"You removed 1 {item.name} to your cart. You now have a total of {strQuantity} orders of {item.name}'s in your cart.")
                return redirect("cart")
            else:
                cart_qs.delete()
                order_qs = Order.objects.filter(
                user=request.user,
                ordered=False
                )
                if order_qs.exists():
                    order = order_qs[0]
                # check if the order item is in the order
                if order.orderitems.filter(item__pk=item.pk).exists():
                    order_item = Cart.objects.filter(
                        item=item,
                        user=request.user,
                    )[0]
                    order.orderitems.remove(order_item)
                    messages.warning(request, "%s was removed from your cart."%item.name)
                return redirect("cart")

        else:
            messages.warning(request, "You do not have an active order")
            return redirect("cart")
    else:
        item = get_object_or_404(Dish, slug=dish_slug)
        session_id = request.session.session_key
        cart_qs = Cart.objects.filter(session = session_id, item=item, pk=pk)
        if cart_qs.exists():
            cart = cart_qs[0]
        # Checking the cart quantity
            if cart.quantity > 1:
                cart.quantity -= 1
                cart.save()
                order_qs = Order.objects.filter(
                session = session_id,
                ordered=False
                )
                order = order_qs[0]
                request.session['total_quantity'] = order.get_total_quantity()
                request.session.save()
                strQuantity = str(cart.quantity)
                messages.info(request, f"You removed 1 {item.name} to your cart. You now have a total of {strQuantity} orders of {item.name}'s in your cart.")
                return redirect("cart")
            else:
                cart_qs.delete()
                order_qs = Order.objects.filter(
                session = session_id,
                ordered=False
                )
                print('Removed entirely from order')
                request.session['total_quantity'] = order_qs[0].get_total_quantity()
                request.session.save()
                if order_qs.exists():
                    order = order_qs[0]
                # check if the order item is in the order
                if order.orderitems.filter(item__pk=item.pk).exists():
                    order_item = Cart.objects.filter(
                        item=item,
                        session = session_id,
                    )[0]
                    order.orderitems.remove(order_item)

                    if order.count() == 0:
                        request.session['total_quantity']
                    messages.warning(request, "%s was removed from your cart."%item.name)
                return redirect("cart")

        else:
            messages.warning(request, "You do not have an active order")
            return redirect("cart")



def add_order_info(request, pk):
    if request.user.is_authenticated:
        order = Order.objects.get(user=request.user, pk=pk, ordered=False)
        order_info = OrderInfo.objects.get_or_create(order=order)
        if request.method == 'POST':
            form = OrderInfoForm(request.POST, instance=order.orderinfo,)
            if form.is_valid():
                order_info = form.save(commit=False)
                order_info.street_address = form.cleaned_data['street_address']
                order_info.city = form.cleaned_data['city']
                order_info.state = form.cleaned_data['state']
                order_info.zipcode = form.cleaned_data['zipcode']
                order_info.email = form.cleaned_data['email']
                order_info.phone_number_to_contact = form.cleaned_data['phone_number_to_contact']
                order_info.same_as_billing = form.cleaned_data['same_as_billing']
                order_info.save()
                return redirect(reverse('add_billing_info', kwargs={"pk":order.pk}))
            else:
                form = OrderInfoForm(initial={'email':request.user.email})
                messages.info(request, "Form is invalid")
                return render(request, 'recipes/add_order_info.html', {"form":form, "order": order})

        else:
            saved_info = model_to_dict(OrderInfo.objects.get(order=order))
            if saved_info['email'] == '':
                saved_info['email'] = request.user.email
            else:
                saved_info['email'] == saved_info['email']
            form = OrderInfoForm(initial=saved_info)
            return render(request, 'recipes/add_order_info.html', {"form":form,"order": order})
    else:
        session_id = request.session.session_key
        order = Order.objects.get(session = session_id, pk=pk, ordered=False)
        order_info = OrderInfo.objects.get_or_create(order=order)
        if request.method == 'POST':
            form = OrderInfoForm(request.POST, instance=order.orderinfo)
            if form.is_valid():
                order_info = form.save(commit=False)
                order_info.street_address = form.cleaned_data['street_address']
                order_info.city = form.cleaned_data['city']
                order_info.state = form.cleaned_data['state']
                order_info.zipcode = form.cleaned_data['zipcode']
                order_info.email = form.cleaned_data['email']
                order_info.phone_number_to_contact = form.cleaned_data['phone_number_to_contact']
                order_info.same_as_billing = form.cleaned_data['same_as_billing']
                order_info.save()
                return redirect(reverse('add_billing_info', kwargs={"pk":order.pk}))
            else:
                form = OrderInfoForm()
                messages.info(request, "Form is invalid")
                return render(request, 'recipes/add_order_info.html', {"form":form, "order": order})

        else:
            saved_info = model_to_dict(OrderInfo.objects.get(order=order,))
            if saved_info['email'] == '':
                saved_info['email'] = ''
            else:
                saved_info['email'] == saved_info['email']
            form = OrderInfoForm(initial=saved_info)
            return render(request, 'recipes/add_order_info.html', {"form":form, "order": order})


def add_billing_info(request,pk):
    if request.user.is_authenticated:
        order = Order.objects.get(user=request.user, pk=pk, ordered=False)
        billing_address = BillingAddress.objects.get_or_create(order=order)
        if request.method == 'POST':
            form = BillingAddressForm(request.POST, instance=billing_address[0])
            if form.is_valid():
                billing_info = form.save(commit=False)
                billing_info.street_address = form.cleaned_data['street_address']
                billing_info.city = form.cleaned_data['city']
                billing_info.state = form.cleaned_data['state']
                billing_info.zipcode = form.cleaned_data['zipcode']
                billing_info.save()
                return redirect(reverse('review_order', kwargs={"pk":order.pk}))
            else:
                print(form.errors)
        else:
            if order.orderinfo.same_as_billing:
                saved_info = model_to_dict(OrderInfo.objects.get(order=order))
                del saved_info['email']
                del saved_info['phone_number_to_contact']
                del saved_info['same_as_billing']
                print('Billing Address Saved Info', saved_info)
                form = BillingAddressForm(initial=saved_info)
                return render(request, 'recipes/add_billing_info.html', {"form":form, "order":order})

            else:
                form = BillingAddressForm()
                return render(request, 'recipes/add_billing_info.html', {"form":form, "order":order})

    else:
        session_id = request.session.session_key
        order = Order.objects.get(pk=pk, session=session_id)
        billing_address = BillingAddress.objects.get_or_create(order=order)
        if request.method == 'POST':
            form = BillingAddressForm(request.POST, instance=billing_address[0])
            if form.is_valid():
                billing_info = form.save(commit=False)
                billing_info.street_address = form.cleaned_data['street_address']
                billing_info.city = form.cleaned_data['city']
                billing_info.state = form.cleaned_data['state']
                billing_info.zipcode = form.cleaned_data['zipcode']
                billing_info.save()
                return redirect(reverse('review_order', kwargs={"pk":order.pk}))
            else:
                print(form.errors)
        else:
            if order.orderinfo.same_as_billing:
                saved_info = model_to_dict(OrderInfo.objects.get(order=order))
                del saved_info['email']
                del saved_info['phone_number_to_contact']
                del saved_info['same_as_billing']
                print('Billing Address Saved Info', saved_info)
                form = BillingAddressForm(initial=saved_info)
                return render(request, 'recipes/add_billing_info.html', {"form":form, "order":order})

            else:
                form = BillingAddressForm()
                return render(request, 'recipes/add_billing_info.html', {"form":form, "order":order})


def review_order(request, pk):
    if request.user.is_authenticated:
        cart_qs = Cart.objects.filter(user=request.user)
        order_qs = Order.objects.filter(user=request.user, ordered=False, pk=pk)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        key = settings.STRIPE_PUBLISHABLE_KEY
        order = Order.objects.get(pk=pk, user=request.user, ordered=False)
        total = int(float(order.get_total()*100))
        if request.method == "POST":
            charge = stripe.Charge.create(
                amount = total,
                currency='usd',
                description = order_qs,
                source = request.POST['stripeToken'])
            if charge.status == 'succeeded':
                print('Charge Success')
                order.ordered = True
                order.save()
                cartItems = Cart.objects.filter(user=request.user)
                for item in cartItems:
                    item.purchased = True
                    item.save()
                    print('Item purchased')
                print('Email Sending')
                html_message = loader.render_to_string(
                    'recipes/emailtemplates/OrderConfirmation.html',
                    {'order':order, 'host':request.get_host(), 'hashNumber':pk}
                )
                send_mail(
                "Your OptOMystik Order", 
                'Thank You!',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL, request.user.email], 
                fail_silently=False,
                html_message=html_message)
                return redirect('order_complete', pk=pk)
            else:
                print('Charge Failed')
                return redirect('review_order', pk=pk)
        else:
            if cart_qs.exists():
                order = Order.objects.get(pk=pk, user=request.user, ordered=False)
                order_info = order.orderinfo                
                return render(request, 'recipes/review_order.html', {'cart':cart_qs,'order':order, 'total':total,  'order_info':order_info, 'key':key} )
            else:
                messages.info(request, "You have nothing in your cart. Add to your order to review your cart.")
                return redirect('home')
    else:
        session_id = request.session.session_key
        cart_qs = Cart.objects.filter(session = session_id)
        order_qs = Order.objects.filter(session = session_id, ordered=False, pk=pk)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        order = Order.objects.get(pk=pk, session = session_id)
        key = settings.STRIPE_PUBLISHABLE_KEY
        total = int(float(order.get_total()*100))
        if request.method == "POST":
            print('Post made with stripe')
            charge = stripe.Charge.create(
                amount = total,
                currency='usd',
                description = order_qs,
                source = request.POST['stripeToken'])
            if charge.status == 'succeeded':
                print('Charge Success')
                order.ordered = True
                order.save()
                cartItems = Cart.objects.filter(session = session_id)
                for item in cartItems:
                    item.purchased = True
                    item.save()
                html_message = loader.render_to_string(
                    'recipes/emailtemplates/OrderConfirmationNoAccount.html',
                    {'order':order, 'session_id':session_id,}
                )
                send_mail(
                "Your OptOMystik Order", 
                'Thank You!',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL, order.orderinfo.email], 
                fail_silently=False,
                html_message=html_message)
                if request.session.session_key:
                    request.session.create()
                    request.session['total_quantity'] = 0
                return redirect('order_complete', pk=pk)
            else:
                return redirect('review_order', pk=pk)
        else:
            if cart_qs.exists():
                order = Order.objects.get(pk=pk, session = session_id)
                order_info = order.orderinfo
                print('total: ',total)
                return render(request, 'recipes/review_order.html', {'cart':cart_qs,'order':order, 'total':total, 'order_info':order_info, 'key':key} )
            else:
                messages.info(request, "You have nothing in your cart. Add to your order to review your cart.")
                return redirect('home')


def order_complete(request, pk):
    if request.user.is_authenticated:
        order_id = pk
        return render(request, 'recipes/order_complete.html', {'order_id':order_id})
    else:
        if request.session.session_key:
            print('Old session key', request.session.session_key)
            request.session.create()
            request.session['total_quantity'] = 0
            print('New session key', request.session.session_key)
            order_id = pk
        return render(request, 'recipes/order_complete.html', {'order_id':order_id})



def orders(request):
    orders = Order.objects.filter(user=request.user, ordered=True)
    return render(request, 'recipes/orders.html', {'orders':orders})

def contact_us_post_order(request, pk):
    if request.user.is_authenticated:
        order = Order.objects.get(pk=pk)
        MessageFormset = inlineformset_factory(Order, ContactUs, fields=('email','subject','text',), extra=1 )
        if request.method == 'POST':
            formset = MessageFormset(request.POST, instance=order)
            if formset.is_valid():
                message_instance = formset.save(commit=False)
                               
                html_message = loader.render_to_string(
                'recipes/emailtemplates/OrderMessage.html',
                {'message':message_instance[0]}
                )
                send_mail(
                "Message Regarding OptOMystik Order", 
                '',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL, request.user.email], 
                fail_silently=False,
                html_message=html_message)
                message_instance[0].save()
                messages.success(request, 'Your message was successfully sent. We will get back to you promptly.')
                return redirect('message_sent')
            else:
                print(formset)
                messages.info(request, 'Your message is invalid, please fill out all the fields in the proper format.')
                return redirect('contactafterorder', pk=pk)
    
        formset = MessageFormset(instance=order, initial=[{'email':request.user.email}] )
        return render(request, 'recipes/contact_post_order.html', {'form':formset})
    else:
        messages.warning(request, 'You must be logged in.')
        return redirect('home')

    

def contact_us(request):
    if request.method == 'POST':
        form = ContactUsUnauthenticated(request.POST)
        if form.is_valid():
            message_instance = form.save(commit=False)
            html_message1 = loader.render_to_string(
                'recipes/emailtemplates/ContactUsNoOrder.html',
                {'message':message_instance}
                )
            send_mail(
                "Thank You for your message sent to the OptOMystik store", 
                '',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL, form.cleaned_data['email']], 
                fail_silently=False,
                html_message=html_message1)
            message_instance.save()
            messages.success(request, 'Your message was successfully sent. We will get back to you promptly.')
            return redirect('message_sent')
        else:
            messages.info(request, 'Your message is invalid, please fill out all the fields in the proper format.')
            return redirect('contact')
    else:
        form = ContactUsUnauthenticated()
        return render(request, 'recipes/contact_us.html', {'form':form})



def message_sent(request):
    return render(request, 'recipes/message_sent.html')


