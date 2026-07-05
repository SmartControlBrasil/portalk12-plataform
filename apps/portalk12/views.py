from django.shortcuts import render


def home(request):
    return render(request, 'portalk12/pages/home.html')
