from django.shortcuts import render

def notfound(request, exception):
    return render(request, "404.html",status=404)

def error(request):
    return render(request, "500.html", status=500)