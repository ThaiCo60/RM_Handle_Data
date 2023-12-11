"""
Definition of news view.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rm_handle_data.apps.news.service import NewsService


@csrf_exempt
def handle_data_news_past(request):
    """
    Get list unit
    :param request:
    :return:
    """
    news_service = NewsService()

    response = news_service.handle_data_news_past()

    return JsonResponse(response.__dict__, status=response.status)


@csrf_exempt
def handle_data_news_daily(request):
    """
    Get list unit
    :param request:
    :return:
    """
    news_service = NewsService()

    response = news_service.handle_data_news_daily()

    return JsonResponse(response.__dict__, status=response.status)

@csrf_exempt
def get_test_sentence_weight(request):
    """
    Get list unit
    :param request:
    :return:
    """
    news_service = NewsService()
    request_params = {
        "content": request.GET.get('content', request.POST.get('content', None))
    }
    response = news_service.test_sentence_weight(request_params)

    return JsonResponse(response.__dict__, status=response.status)
