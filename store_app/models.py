# models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password as django_check_password

class aunth(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Владелец'),
        ('seller', 'Продавец'),
        ('user', 'Пользователь'),
    ]

    name = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)  # Длина увеличена для хранения хешированных паролей
    role = models.CharField(max_length=35, choices=ROLE_CHOICES, default='user')

    def set_password(self, raw_password):
        """
        Хеширует пароль и сохраняет его в поле password.
        """
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """
        Проверяет, соответствует ли предоставленный пароль хешу в базе данных.
        """
        return django_check_password(raw_password, self.password)

    def __str__(self):
        return f'{self.name} ({self.role})'

class debetors (models.Model):
    name = models.CharField(max_length=50)
    debet = models.IntegerField(default= 0)

    def __str__(self):
        return f'{self.name} ({self.debet})'


class product(models.Model):
    art = models.IntegerField(default= 0)
    name1 = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2,  default= 2500)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=30)
    count = models.IntegerField()
    image = models.ImageField(upload_to='products/',blank=True, null=True)  # Указывает папку для хранения изображений

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['art', 'color'], name='unique_art_color')
        ]

    def __str__(self):
        return f"{self.name1} ({self.art}, {self.color})"

class orders(models.Model):
    id = models.AutoField(primary_key=True)  # Автоинкрементный ID
    products_in_order = models.TextField(null=False)  # JSON-строка с товарами
    status = models.BooleanField(default=False)  # False: не завершён, True: завершён
    payment = models.CharField(max_length=50, choices=[('Банк', 'Банк'), ('Наличные', 'Наличные'), ('Должник', 'Должник')])
    user = models.CharField(max_length=100)
    data_payment = models.DateTimeField(blank=True, null=True)
    data_creation = models.DateTimeField(auto_now_add=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Скидка
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Итоговая сумма

    def __str__(self):
        return f"Заказ {self.id} ({self.data_creation}, {self.status})"