# Generated by Django 5.1.5 on 2025-01-21 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0006_debetors_alter_product_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='orders',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('products_in_order', models.TextField()),
                ('status', models.BooleanField()),
                ('payment', models.CharField(max_length=50)),
                ('user', models.CharField(max_length=100)),
                ('data_payment', models.DateTimeField()),
                ('data_creation', models.DateTimeField()),
            ],
        ),
    ]
