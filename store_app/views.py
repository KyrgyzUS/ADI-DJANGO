from .decorators import role_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import aunth
from .forms import LoginForm
from .forms import productForm
from django.core.paginator import Paginator
from .models import product, orders
from django.views.decorators.csrf import csrf_exempt
from .models import debetors
from django.http import JsonResponse
import json
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, F
from django.utils.timezone import now, localdate
from django.contrib.auth.decorators import login_required  # Для проверки авторизации
from django.contrib.auth.models import User
from django.db import transaction

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['name']
            password = form.cleaned_data['password']


            try:
                user = aunth.objects.get(name=name)


                if user.check_password(password):

                    request.session['user_id'] = user.id
                    request.session['user_role'] = user.role
                    request.session['user_name'] = user.name

                    if user.role == 'owner':

                        return redirect('owner_page')
                    elif user.role == 'seller':

                        return redirect('seller_page')
                    else:

                        return redirect('user_page')
                else:

                    messages.error(request, 'Неверный пароль.')
            except aunth.DoesNotExist:

                messages.error(request, 'Пользователь не найден.')
        else:
            print("Форма не валидна")  # Логируем невалидную форму
            print(f"Ошибки формы: {form.errors}")  # Логируем ошибки формы
    else:

        form = LoginForm()


    return render(request, 'login.html', {'form': form})


@role_required('owner')
def owner_page(request):
    if request.session.get('user_role') != 'owner':
        return redirect('login')
    return render(request, 'admin.html')
@role_required('seller')
def seller_page(request):
    if request.session.get('user_role') != 'seller':
        return redirect('login')
    return render(request, 'editor.html')
@role_required('user')
def user_page(request):
    if request.session.get('user_role') != 'user':
        return redirect('login')
    return render(request, 'user.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')
@role_required('owner')
def upload_product(request):
    # Очистка сообщений перед началом работы
    storage = messages.get_messages(request)
    storage.used = True  # Помечаем все сообщения как использованные

    if request.method == 'POST':
        form = productForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Продукт успешно добавлен.')  # Успешное сообщение
            return redirect('owner_page')
        else:
            messages.error(request, 'Форма заполнена некорректно. Пожалуйста, исправьте ошибки.')  # Ошибка валидации формы
    else:
        form = productForm()
    return render(request, 'upload_product.html', {'form': form})


def product_list(request):
    query = request.GET.get('q')  # Получаем значение из поля поиска
    products = product.objects.all()

    if query:
        products = products.filter(art__icontains=query)  # Фильтрация по артиклю

    paginator = Paginator(products, 10)  # Пагинация: 10 продуктов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'product_list.html', {'page_obj': page_obj, 'query': query})

@role_required('owner')
def product_redact(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        # Проверяем, передан ли идентификатор продукта
        if not product_id:
            return JsonResponse({'success': False, 'error': 'Идентификатор продукта не передан.'}, status=400)

        # Получаем продукт, если идентификатор передан
        try:
            product_instance = get_object_or_404(product, id=product_id)
        except product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Продукт не найден.'}, status=404)

        # Создаём форму с данными для редактирования
        form = productForm(request.POST, request.FILES, instance=product_instance)

        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': f'Продукт "{product_instance.name1}" успешно обновлён.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    # GET-запрос: отображаем страницу редактирования
    return render(request, 'product_redact.html')

def get_colors(request):
    art = request.GET.get('art', '').strip()
    include_count = request.GET.get('include_count', 'false').lower() == 'true'

    if not art:
        return JsonResponse([], safe=False)

    products = product.objects.filter(art=art).values('id', 'color', 'count')

    if include_count:
        # Если параметр include_count=true, возвращаем цвета с количеством
        colors_with_counts = [
            {'color': prod['color'], 'count': prod['count']}
            for prod in products
        ]
        return JsonResponse(colors_with_counts, safe=False)
    else:
        # Если include_count=false (или не указан), возвращаем только цвета
        colors = [{'id': prod['id'], 'color': prod['color']} for prod in products]
        return JsonResponse(colors, safe=False)


def get_product(request):
    product_id = request.GET.get('product_id')
    product_instance = get_object_or_404(product, id=product_id)
    product_data = {
        'id': product_instance.id,
        'art': product_instance.art,
        'name1': product_instance.name1,
        'price': product_instance.price,
        'count': product_instance.count,
        'color': product_instance.color,
        'description': product_instance.description,
        'image_url': product_instance.image.url if product_instance.image else None,
    }
    return JsonResponse(product_data)


def delete_product(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body.decode('utf-8'))
        product_id = data.get('product_id')

        if not product_id:
            return JsonResponse({'success': False, 'error': 'ID товара не передан.'}, status=400)

        try:
            product_instance = product.objects.get(id=product_id)
            product_instance.delete()  # Удаляем товар
            return JsonResponse({'success': True})
        except product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается.'}, status=405)

@role_required('owner')
def debetors_list(request):
    debetors_usage = debetors.objects.all()
    return render(request, 'debetors_list.html', {'debet': debetors_usage})

@csrf_exempt
def add_debtor(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        debet = request.POST.get('debet')

        if name and debet:
            debetors.objects.create(name=name, debet=debet)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Некорректные данные.'})
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается.'}, status=405)

@csrf_exempt
def update_debtor(request):
    if request.method == 'POST':
        debtor_id = request.POST.get('id')
        name = request.POST.get('name')
        debet = request.POST.get('debet')

        try:
            debtor = debetors.objects.get(id=debtor_id)
            debtor.name = name
            debtor.debet = debet
            debtor.save()
            return JsonResponse({'success': True})
        except debetors.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Должник не найден.'})
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается.'}, status=405)

@csrf_exempt
def delete_debtor(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body.decode('utf-8'))
        debtor_id = data.get('id')

        try:
            debetors.objects.get(id=debtor_id).delete()
            return JsonResponse({'success': True})
        except debetors.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Должник не найден.'})
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается.'}, status=405)

def orders_list(request):
    orders_queryset = orders.objects.all()

    # Фильтры
    payment = request.GET.get('payment')
    user = request.GET.get('user')
    data_creation_start = request.GET.get('data_creation_start')
    data_creation_end = request.GET.get('data_creation_end')
    status = request.GET.get('status')

    if payment:
        orders_queryset = orders_queryset.filter(payment=payment)
    if user:
        orders_queryset = orders_queryset.filter(user__icontains=user)
    if data_creation_start and data_creation_end:
        orders_queryset = orders_queryset.filter(
            data_creation__range=[data_creation_start, data_creation_end]
        )
    if status in ['True', 'False']:
        orders_queryset = orders_queryset.filter(status=status == 'True')

    return render(request, 'orders_list.html', {'orders': orders_queryset})

@role_required( 'owner', 'seller')
def create_order(request):
    # Список должников (для выпадающего списка)
    all_debtors = debetors.objects.all()

    if request.method == 'POST':
        user = request.POST.get('user', '').strip()
        payment = request.POST.get('payment', '').strip()
        discount_str = request.POST.get('discount', '0').strip()
        debtor_name = request.POST.get('debtor', '').strip()

        # Считываем массивы из формы
        arts = request.POST.getlist('art[]')
        colors = request.POST.getlist('colors[]')
        counts = request.POST.getlist('counts[]')

        # Преобразуем скидку в Decimal
        try:
            discount = Decimal(discount_str).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except:
            discount = Decimal('0.00')

        products_data = []
        total_price = Decimal('0.00')

        # Используем транзакцию, чтобы изменения были атомарными
        with transaction.atomic():
            for art_val, color_val, count_val in zip(arts, colors, counts):
                # Пропускаем пустые строки (вдруг кто-то нажал «Добавить», но не заполнил)
                if not art_val or not color_val or not count_val:
                    continue

                # Проверяем, что товар существует
                try:
                    prod = product.objects.get(art=art_val, color=color_val)
                except product.DoesNotExist:
                    messages.error(request, f"Товар с артикулом {art_val} и цветом {color_val} не найден!")
                    # Откатываем транзакцию и возвращаемся к форме
                    transaction.set_rollback(True)
                    return redirect('create_order')

                # Пробуем преобразовать количество
                try:
                    count_int = int(count_val)
                except ValueError:
                    messages.error(request, f"Некорректное количество: {count_val}")
                    transaction.set_rollback(True)
                    return redirect('create_order')

                if count_int <= 0:
                    messages.error(request, f"Количество должно быть больше нуля.")
                    transaction.set_rollback(True)
                    return redirect('create_order')

                # Считаем сумму по строке
                line_price = prod.price * count_int
                total_price += line_price

                #(Опционально) Проверяем остаток на складе (если нужно)
                if prod.count < count_int:
                    messages.error(request, f"Недостаточно {art_val} (цвет {color_val}) на складе.")
                    transaction.set_rollback(True)
                    return redirect('create_order')
                prod.count -= count_int
                prod.save()

                # Заполняем структуру для JSON
                products_data.append({
                    'art': art_val,
                    'name': prod.name1,
                    'color': color_val,
                    'count': str(count_int),
                    'unit_price': str(prod.price),
                    'line_total': str(line_price),
                    'debetor': str(debtor_name),
                })

            # Применяем скидку
            total_price -= discount
            if total_price < 0:
                total_price = Decimal('0.00')

            # Создаём заказ
            new_order = orders.objects.create(
                products_in_order=json.dumps(products_data, ensure_ascii=False),
                status=False,
                payment=payment,
                user=user,
                data_payment=None,
                discount=discount,
                total_price=total_price
            )

            # Если "Должник" – обновим долг
            if payment == 'Должник' and debtor_name:
                try:
                    debtor_obj = debetors.objects.get(name=debtor_name)
                    # Если в debet нужно складывать как целые, округляем
                    debtor_obj.debet += int(total_price.to_integral_value(rounding=ROUND_HALF_UP))
                    debtor_obj.save()
                except debetors.DoesNotExist:
                    messages.error(request, f"Должник '{debtor_name}' не найден!")
                    transaction.set_rollback(True)
                    return redirect('create_order')

            messages.success(request, f"Заказ #{new_order.id} успешно создан.")
            return redirect('orders_list')

    # GET-запрос
    return render(request, 'create_order.html', {
        'debtors': all_debtors
    })

def delete_order(request):
    if request.method == 'POST':
        order_id = json.loads(request.body).get('id')
        try:
            order = orders.objects.get(id=order_id)

            with transaction.atomic():  # Используем транзакцию для сохранения целостности
                # Возвращаем товары на склад
                products_in_order = json.loads(order.products_in_order)  # Декодируем JSON в список продуктов
                for item in products_in_order:  # Используем другое имя переменной, чтобы избежать конфликта
                    art = item.get('art')
                    color = item.get('color')
                    count = int(item.get('count'))

                    try:
                        prod = product.objects.get(art=art, color=color)  # Модель product
                        prod.count += count  # Возвращаем количество товара
                        prod.save()
                    except product.DoesNotExist:
                        # Если товар отсутствует в базе, пропускаем
                        continue

                # Если способ оплаты был "Должник", уменьшаем долг
                if order.payment == 'Должник':
                    debtor_name = products_in_order[0].get('debetor')  # Имя должника берём из первого товара
                    if debtor_name:
                        try:
                            debtor = debetors.objects.get(name=debtor_name)
                            debtor.debet -= order.total_price  # Уменьшаем долг на сумму заказа
                            debtor.save()
                        except debetors.DoesNotExist:
                            return JsonResponse({'success': False, 'error': f"Должник {debtor_name} не найден."})

                # Удаляем заказ
                order.delete()

            return JsonResponse({'success': True})
        except orders.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Заказ не найден.'})
    else:
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается.'})


def edit_order(request, order_id):
    order = get_object_or_404(orders, id=order_id)

    if order.status:
        return JsonResponse({'success': False, 'error': 'Редактирование завершённого заказа невозможно.'})

    if request.method == 'POST':
        with transaction.atomic():
            # Сохраняем старое состояние для расчётов
            old_products = json.loads(order.products_in_order)  # Список товаров до изменений
            old_payment = order.payment  # Способ оплаты до изменений
            old_total_price = order.total_price  # Итоговая сумма до изменений

            # Обновляем данные заказа
            order.payment = request.POST.get('payment')
            order.user = request.POST.get('user')
            order.status = request.POST.get('status') == 'on'
            order.discount = Decimal(request.POST.get('discount', '0.00'))

            arts = request.POST.getlist('art[]')  # Список артикулов
            colors = request.POST.getlist('colors[]')  # Список цветов
            counts = request.POST.getlist('counts[]')  # Список количеств

            new_products = []  # Список обновлённых товаров
            new_total_price = Decimal('0.00')  # Итоговая сумма после изменений

            # Получаем имя должника из существующего заказа (оно не меняется)
            debtor_name = old_products[0].get('debetor') if old_products else None
            debtor = None

            if debtor_name:
                try:
                    debtor = debetors.objects.get(name=debtor_name)
                except debetors.DoesNotExist:
                    messages.error(request, f"Должник {debtor_name} не найден.")
                    return redirect('edit_order', order_id=order.id)

            # Возврат старого количества товаров на склад
            for old_product in old_products:
                prod = product.objects.get(art=old_product['art'], color=old_product['color'])
                prod.count += int(old_product['count'])  # Возвращаем количество
                prod.save()

            # Пересчитываем новое количество и списываем со склада
            for art, color, count in zip(arts, colors, counts):
                try:
                    count = int(count)
                    prod = product.objects.get(art=art, color=color)

                    # Проверяем доступное количество
                    if count > prod.count:
                        messages.error(
                            request,
                            f"Недостаточно товара {art} ({color}) на складе. Доступно: {prod.count}."
                        )
                        return redirect('edit_order', order_id=order.id)

                    # Списываем новое количество со склада
                    prod.count -= count
                    prod.save()

                    # Считаем общую стоимость товара
                    line_total = prod.price * count
                    new_total_price += line_total

                    # Обновляем список товаров
                    new_products.append({
                        'art': art,
                        'color': color,
                        'count': count,
                        'unit_price': str(prod.price),
                        'line_total': str(line_total),
                        'debetor': debtor_name,  # Имя должника остаётся неизменным
                    })
                except product.DoesNotExist:
                    messages.error(request, f"Товар {art} ({color}) не найден.")
                    return redirect('edit_order', order_id=order.id)

            # Применяем скидку
            new_total_price -= order.discount
            order.total_price = max(new_total_price, Decimal('0.00'))  # Итоговая сумма после скидки

            # Пересчёт долга для должника
            if debtor:
                if old_payment == 'Должник':  # Уменьшаем долг на старую сумму заказа
                    debtor.debet -= old_total_price

                if order.payment == 'Должник':  # Увеличиваем долг на новую сумму заказа
                    debtor.debet += order.total_price

                debtor.save()

            # Сохраняем изменения заказа
            order.products_in_order = json.dumps(new_products, ensure_ascii=False)
            order.save()

            messages.success(request, f"Заказ #{order.id} успешно обновлён.")
            return redirect('orders_list')

    # Преобразуем JSON-строку продуктов в список
    products = json.loads(order.products_in_order)

    return render(request, 'edit_order.html', {
        'order': order,
        'products': products,
    })




@csrf_exempt
def update_order_status(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        order_id = data.get('id')

        if not order_id:
            return JsonResponse({'success': False, 'error': 'ID заказа не передан.'}, status=400)

        # Ищем заказ
        try:
            order = orders.objects.get(id=order_id)
        except orders.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Заказ не найден.'}, status=404)

        # Обновляем статус
        order.status = True
        order.data_payment = now()
        order.save()


        return JsonResponse({'success': True, 'message': f'Статус заказа #{order_id} обновлён на "Завершён".'})
    else:
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается.'}, status=405)

def analiz(request):
    report_type = request.GET.get('type')

    if not report_type:
        return render(request, 'analiz.html')

    if report_type == 'sales_today':
        # Продажи за текущий день
        today = localdate()
        orders_today_qs = orders.objects.filter(
            data_payment__date=today,
            status=True
        )

        # Суммируем по каждому способу оплаты
        payment_agg = (
            orders_today_qs
            .values('payment')
            .annotate(total_price=Sum('total_price'))
        )

        # Преобразуем в список
        payment_summary = []
        for row in payment_agg:
            payment_summary.append({
                'payment': row['payment'],
                'total_price': float(row['total_price']) if row['total_price'] else 0
            })

        # Детализация по должникам
        # Для всех заказов, где payment = 'Должник'
        debtors_map = {}
        debtors_orders = orders_today_qs.filter(payment='Должник')
        for o in debtors_orders:
            prods = json.loads(o.products_in_order)
            for p in prods:
                # Если при создании заказа мы сохраняли имя должника в поле 'debetor'
                debtor_name = p.get('debetor')
                line_total = float(p.get('line_total', 0))  # Сумма для конкретного товара
                if debtor_name:
                    debtors_map[debtor_name] = debtors_map.get(debtor_name, 0) + line_total

        debtor_summary = [
            {'debtor': k, 'sum': v} for k, v in debtors_map.items()
        ]

        return JsonResponse({
            'paymentSummary': payment_summary,
            'debtorSummary': debtor_summary
        }, safe=False)

    elif report_type == 'art_sales':
        # Продажи art за период
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        orders_in_period = orders.objects.filter(
            data_payment__date__range=[start_date, end_date],
            status=True
        ).values('products_in_order')

        sales = {}
        for order in orders_in_period:
            products = json.loads(order['products_in_order'])
            for product in products:
                art = product.get('art')
                sales[art] = sales.get(art, 0) + int(product.get('count', 0))

        chart_data = [{'label': art, 'value': count} for art, count in sales.items()]
        return JsonResponse(chart_data, safe=False)

    elif report_type == 'art_color_sales':

        # Продажи цветов для конкретного артикула за период

        art = request.GET.get('art')

        start_date = request.GET.get('start_date')

        end_date = request.GET.get('end_date')

        if not art or not start_date or not end_date:
            return JsonResponse({'error': 'Параметры art, start_date и end_date обязательны'}, status=400)

        # Фильтруем заказы по артикулу и периоду

        orders_in_period = orders.objects.filter(

            data_payment__date__range=[start_date, end_date],

            status=True

        ).values('products_in_order')

        # Считаем количество продаж по цветам

        color_sales = {}

        for order in orders_in_period:

            products = json.loads(order['products_in_order'])

            for product in products:

                if str(product.get('art')) == art:  # Сравниваем артикул

                    color = product.get('color')

                    count = int(product.get('count', 0))

                    color_sales[color] = color_sales.get(color, 0) + count

        # Подготавливаем данные для таблицы

        result = [{'color': color, 'count': count} for color, count in sorted(color_sales.items(), key=lambda x: -x[1])]

        return JsonResponse(result, safe=False)

    else:
        return JsonResponse({'error': 'Неверный тип отчёта'}, status=400)

def order_details(request, order_id):
    try:
        order_obj = orders.objects.get(id=order_id)
    except orders.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Заказ не найден.'}, status=404)

    products_data = json.loads(order_obj.products_in_order)

    # Если платёж "Должник", предполагаем, что должник указан в поле 'debetor' (к примеру, у первого товара).
    debtor_name = None
    if order_obj.payment == 'Должник' and len(products_data) > 0:
        # Берём из первого (или проверяем все, если нужно)
        debtor_name = products_data[0].get('debetor', None)

    # Формируем структуру для ответа
    response_data = {
        'success': True,
        'order_id': order_obj.id,
        'payment': order_obj.payment,
        'debtor': debtor_name,
        'products': [
            {
                'art': p.get('art'),
                'color': p.get('color'),
                'count': p.get('count'),
                'unit_price': p.get('unit_price'),
                'line_total': p.get('line_total'),
            }
            for p in products_data
        ]
    }
    return JsonResponse(response_data, safe=False)

def get_all_products(request):
    products = product.objects.all().values('id', 'art', 'name1', 'price', 'count', 'color', 'description')
    return JsonResponse(list(products), safe=False)


