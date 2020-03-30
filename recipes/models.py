from django.db import models
from django.utils.html import mark_safe
from django.utils.text import slugify
from users.models import CustomUser
from django.utils import timezone
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator







# Create your models here.
class Category(models.Model):
    name = models.CharField("Category Name", max_length=50)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


    
class Dish(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="dishes")
    name = models.CharField("Dish Name", max_length=50)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True)
    serves = models.IntegerField(default=4)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=33.33)
    weight = models.IntegerField("Weight in Ounces", help_text="Weight in Ounces", default=16 )
    created_at = models.DateTimeField(auto_now_add=True)
    stl = models.FileField(upload_to='stls', max_length=100, null=True, blank=True)
    video = models.FileField(upload_to='creationvideo', max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    def was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=30)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Dish, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Creation'
        verbose_name_plural = 'Creations'

class DishImages(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="dishimages")
    image = models.ImageField(upload_to="dishimages/")
    def image_thumb(self):
        return mark_safe('<img src="%s" height="80" />' % (self.image.url))
    image_thumb.allow_tags = True
    image_thumb.short_description = 'Image'
    def __str__(self):
        return self.image_thumb()
    


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="items", null=True)
    session = models.CharField(max_length=33, null=True)
    item = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="items")
    quantity = models.IntegerField(default=1)
    purchased = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.quantity} of {self.item.name}'

    def get_line_total(self):
        line_total = self.item.price*self.quantity
        return line_total
    
    def get_line_serving_total(self):
        line_serving_total = self.item.serves*self.quantity
        return line_serving_total

    def get_line_quantity(self):
        return self.quantity

class Order(models.Model):
    orderitems = models.ManyToManyField(Cart, related_name='orderitems')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    session = models.CharField(max_length=33, null=True)
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    paid_on = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now = True)
    authorized = models.BooleanField(default=False)
    fulfilled = models.BooleanField(default=False)


    def __str__(self):
        if self.user != None:
            return f'{self.user.email} {self.orderitems.all()} id# {self.id}'
        if self.session != None:
            return f'Session# {self.session} {self.orderitems.all()} id# {self.id}'

    def get_total(self):
        total = 0
        for order_item in self.orderitems.all():
            total+=order_item.get_line_total()
        return total

    def get_serving_total(self):
        total = 0
        for order_item in self.orderitems.all():
            total+=order_item.get_line_serving_total()
        return total

    def get_total_quantity(self):
        total = 0
        for order_item in self.orderitems.all():
            total+=order_item.get_line_quantity()
        return total

    def save(self, *args, **kwargs):
        if self.ordered == True:
            self.paid_on = timezone.now()
            super(Order, self).save(*args, **kwargs)
        else:
            self.paid_on = None
            super(Order, self).save(*args, **kwargs)
    
    

class OrderInfo(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True)
    street_address = models.CharField("Street Address", max_length=40, help_text="Example: 123 State St.")
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30, help_text='State, County, or Province')
    zipcode = models.IntegerField("Zip Code", validators=[MinValueValidator(0), MaxValueValidator(999999)], null=True)
    email = models.EmailField()
    phone_number_to_contact = models.CharField( help_text="Example: (818) 234-5678 or 8182342342" ,max_length=20, null=True)
    address = models.CharField(max_length=200, blank=True)
    same_as_billing = models.BooleanField(default = True)
    def save(self, *args, **kwargs):
        self.address = '{}, {}, {}, {}'.format(self.street_address, self.city, self.state, self.zipcode,)
        super(OrderInfo, self).save(*args, **kwargs)

class BillingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True)
    street_address = models.CharField("Street Address", max_length=40, help_text="Example: 123 State St.")
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30, help_text='State, County, or Province')
    zipcode = models.IntegerField("Zip Code", validators=[MinValueValidator(0), MaxValueValidator(999999) ], null=True)
    address = models.CharField(max_length=200, blank=True)
    def save(self, *args, **kwargs):
        self.address = '{}, {}, {}, {}'.format(self.street_address, self.city, self.state, self.zipcode)
        super(BillingAddress, self).save(*args, **kwargs)


class ContactUs(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length=78)
    text = models.TextField(max_length=3000)
    class Meta:
        verbose_name_plural = "Messages from Contact Us"


class Review(models.Model):
    class Rating(models.IntegerChoices):
        FIVE = 5
        FOUR = 4
        THREE = 3
        TWO = 2
        ONE = 1

    rating = models.IntegerField(choices=Rating.choices)
    opinion = models.TextField(max_length=1000)
    first_name = models.CharField(max_length=30)

    def __str__(self):
        return self.first_name
    