# Generated by Django 5.1.5 on 2025-01-18 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0002_aunth_delete_worker'),
    ]

    operations = [
        migrations.CreateModel(
            name='product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('art', models.IntegerField(default=0, max_length=40)),
                ('name', models.CharField(max_length=120)),
                ('price', models.DecimalField(decimal_places=2, default=2500, max_digits=10)),
                ('description', models.TextField()),
                ('color', models.CharField(max_length=30)),
                ('count', models.IntegerField(max_length=20)),
                ('image', models.ImageField(upload_to='products/')),
            ],
        ),
        migrations.AlterField(
            model_name='aunth',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='aunth',
            name='password',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='aunth',
            name='role',
            field=models.CharField(choices=[('owner', 'Владелец'), ('seller', 'Продавец'), ('user', 'Пользователь')], default='user', max_length=35),
        ),
    ]
