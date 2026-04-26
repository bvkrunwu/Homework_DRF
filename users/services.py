import stripe

from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def create_stripe_price(amount, product_id):
    """
    Создаёт объект цены (Price) в Stripe для указанного продукта.

    Эта функция используется для связывания денежного эквивалента с
    ранее созданным продуктом. В Stripe сумма должна передаваться в
    минимальных единицах валюты (копейках), поэтому перед созданием
    происходит умножение на 100.

    Args:
        amount (int): Сумма платежа в рублях (будет сконвертирована в копейки).
        product_id (str): Идентификатор продукта (Product) в Stripe, для которого создаётся цена.

    Returns:
        stripe.Price: Объект цены, созданный API Stripe. Содержит уникальный id цены.
    """

    return stripe.Price.create(
        currency="rub",
        unit_amount=amount * 100,
        product=product_id,
    )


def create_stripe_session(price):
    """
    Создаёт Checkout Session в Stripe для проведения платежа.

    Функция формирует сессию оплаты, которая генерирует уникальную
    ссылку для перехода пользователя на защищённую страницу оплаты.

    Args:
        price (stripe.Price): Объект цены, полученный от Stripe. Используется для
            определения стоимости и валюты платежа.

    Returns:
        tuple: Кортеж, содержащий два элемента:
            - session_id (str): Уникальный идентификатор созданной сессии в Stripe.
            - payment_url (str): Ссылка (URL), по которой пользователь должен перейти
              для завершения оплаты.
    """

    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        line_items=[{"price": price.id, "quantity": 1}],
        mode="payment",
    )
    return session.id, session.url
