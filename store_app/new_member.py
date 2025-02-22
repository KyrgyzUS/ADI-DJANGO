from store_app.models import aunth

# Создание нового пользователя
user = aunth(name='user', role='user')
user.set_password('userpass')  # Хеширование и установка пароля
user.save()
