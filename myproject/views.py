from django.http import HttpResponse
from django.shortcuts import render


def homePage(request):
    return render(request, "home.html")


def homepagewithname(request,name):
    return HttpResponse(f"Welcome to home page {name}")