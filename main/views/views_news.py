from django.shortcuts import render
from main.models import NewsMessage


def news_view(request):
    news_data = NewsMessage.objects.all().order_by('-news_time')
    return render(request, "main/news/news_view.html", {'news_data': news_data})
