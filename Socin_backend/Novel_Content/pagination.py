# pagination.py
from rest_framework.pagination import PageNumberPagination

# IF YOU WANT TO MAKE CUSTOME PAGINATION CLASSES
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
