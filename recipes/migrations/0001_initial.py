# Generated by Django 3.0.4 on 2020-03-29 06:57

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(help_text='Example: 123 State St.', max_length=40, verbose_name='Street Address')),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(help_text='State, County, or Province', max_length=30)),
                ('zipcode', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(999999)], verbose_name='Zip Code')),
                ('address', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=33, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('purchased', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Category Name')),
                ('slug', models.SlugField(blank=True, max_length=150, unique=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=50)),
                ('subject', models.CharField(max_length=78)),
                ('text', models.TextField(max_length=3000)),
            ],
            options={
                'verbose_name_plural': 'Messages from Contact Us',
            },
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Dish Name')),
                ('slug', models.SlugField(blank=True, max_length=150, unique=True)),
                ('description', models.TextField(blank=True)),
                ('serves', models.IntegerField(default=4)),
                ('price', models.DecimalField(decimal_places=2, default=33.33, max_digits=5)),
                ('weight', models.IntegerField(default=16, help_text='Weight in Ounces', verbose_name='Weight in Ounces')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('stl', models.FileField(blank=True, null=True, upload_to='stls')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='DishImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='dishimages/')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=33, null=True)),
                ('ordered', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('paid_on', models.DateTimeField(null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('authorized', models.BooleanField(default=False)),
                ('fulfilled', models.BooleanField(default=False)),
                ('orderitems', models.ManyToManyField(related_name='orderitems', to='recipes.Cart')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(5, 'Five'), (4, 'Four'), (3, 'Three'), (2, 'Two'), (1, 'One')])),
                ('opinion', models.TextField(max_length=1000)),
                ('first_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_address', models.CharField(help_text='Example: 123 State St.', max_length=40, verbose_name='Street Address')),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(help_text='State, County, or Province', max_length=30)),
                ('zipcode', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(999999)], verbose_name='Zip Code')),
                ('email', models.EmailField(max_length=254)),
                ('phone_number_to_contact', models.CharField(help_text='Example: (818) 234-5678 or 8182342342', max_length=20, null=True)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('same_as_billing', models.BooleanField(default=True)),
                ('order', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.Order')),
            ],
        ),
    ]
