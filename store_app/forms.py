# forms.py
from django import forms
from .models import product

class LoginForm(forms.Form):
    name = forms.CharField(max_length=20, label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

from django import forms
from .models import product

class productForm(forms.ModelForm):
    class Meta:
        model = product
        fields = ['art', 'name1', 'price', 'description', 'color', 'count', 'image']
        labels = {
            'art': 'Артикул',
            'name1': 'Название',
            'price': 'Цена',
            'description': 'Описание',
            'color': 'Цвет',
            'count': 'Количество',
            'image': 'Изображение',
        }

    def clean(self):
        cleaned_data = super().clean()
        art = cleaned_data.get('art')
        color = cleaned_data.get('color')

        if art is not None and color is not None:
            # Получаем QuerySet записей с такими же art и color
            qs = product.objects.filter(art=art, color=color)

            # Если это обновление (instance.pk не пустое), исключаем текущую запись
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            # Если в базе уже есть другая запись с тем же (art, color), вызываем ошибку
            if qs.exists():
                raise forms.ValidationError(
                    f"Продукт с артиклем '{art}' и цветом '{color}' уже существует."
                )

        return cleaned_data

