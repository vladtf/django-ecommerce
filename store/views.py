import datetime
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt
from ecommerce import urls
from store.models import *
from .utils import cartData, guestOrder


def store(request):
    context = cartData(request)
    return render(request, 'store/store.html', context)


def cart(request):
    context = cartData(request)
    return render(request, 'store/cart.html', context)


def checkout(request):
    context = cartData(request)
    return render(request, 'store/checkout.html', context)


def product(request, id):
    context = cartData(request)
    context['product'] = Product.objects.get(id=id)

    return render(request, 'store/product.html', context)


def login_view(request):
    context = {}
    return render(request, 'store/login.html', context)


def auth(request):
    username = request.body['username']
    password = request.body['password']

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect('store')
    else:
        messages.error('Failed to login!')
        return redirect('login')


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    print('Action:', action)
    print('Product:', product_id)

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity = (order_item.quantity + 1)
    elif action == 'remove':
        order_item.quantity = (order_item.quantity - 1)

    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()

    return JsonResponse('Item was added', safe=False)


# @csrf_exempt
def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if float(order.get_cart_total) == total:
        order.complete = True
        print(total, '=', order.get_cart_total)

    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            country=data['shipping']['country'],
        )

    return JsonResponse('Payment complete!', safe=False)
