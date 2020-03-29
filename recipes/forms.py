from django import forms
from .models import Order, OrderInfo, BillingAddress,ContactUs, Review




class OrderInfoForm(forms.ModelForm):
    class Meta:
        model = OrderInfo
        fields = '__all__'
        exclude = ['order', 'address']
        labels = {
            'same_as_billing':'Shipping Address is the same as Billing Address'
        }

        

class BillingAddressForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = '__all__'
        exclude = ['order', 'address']


class ContactUsUnauthenticated(forms.ModelForm):
    class Meta:
        model=ContactUs
        fields='__all__'
        exclude = ['order']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields='__all__'
        widgets = { 
            'opinion': forms.Textarea(attrs={'placeholder': u"What do you think about OptOMystik, including our products and customer service?", 'rows':'3'}),
        }   