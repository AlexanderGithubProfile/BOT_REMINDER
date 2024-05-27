from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import parse_request_body

@csrf_exempt
def handle_incoming_message(request):
    if request.method == 'POST':
        parse_request_body(request)
        return HttpResponse('Выполнено')

# Заглушка для хоста
@csrf_exempt
def index(request):
    return HttpResponse('Стартовая страница, сервер работает!')