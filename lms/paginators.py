from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Кастомный класс пагинации для API.

    Используется для разделения больших списков объектов (курсов, уроков)
    на отдельные страницы для удобства просмотра и снижения нагрузки на сервер.

    Настройки:
        page_size (int): Количество объектов на странице по умолчанию (5).
        page_size_query_param (str): Название GET-параметра, с помощью которого
            клиент может указать желаемое количество элементов на странице.
        max_page_size (int): Максимально допустимое количество элементов на странице (10).
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
