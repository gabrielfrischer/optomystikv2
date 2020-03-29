from django import template
from recipes.models import Order
from django.db.models import Sum

register = template.Library()

@register.filter
def cart_total(user):
    if user.is_authenticated:
        order_qs = Order.objects.filter(user=user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            quantity_array = list(order.orderitems.values_list('quantity', flat=True))
            total_quantity = sum(quantity_array)
            print(quantity_array)
            return total_quantity

        else:
    	    return 0
    else:
        return 0


