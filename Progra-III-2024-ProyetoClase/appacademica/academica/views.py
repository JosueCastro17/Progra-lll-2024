from django.shortcuts import render
from django.http import HttpResponse
import json
from .models import alumno
from django.http import JsonResponse

# Create your views here.
def hola_mundo(request):
    return HttpResponse("Hola Mundo")

def saludo(request, nombre):
    return HttpResponse(f"Hola {nombre}, bienvenido a Programacion Computacional III")

def edad(request, edad):
    return HttpResponse("Tu edad es %s años" %edad)

def index(request):
    return render(request, 'index.html')

def vista(request, form):
    return render(request, f"{form}.html")

def alumnos(request):
    datos = alumno.objects.values('id', 'codigo', 'nombre', 'direccion', 'telefono')
    return JsonResponse(list(datos), safe=False)