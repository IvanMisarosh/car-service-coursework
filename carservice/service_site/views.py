from django.shortcuts import render
from . import models

# Create your views here.
def index(request):
    color = models.Color(color_name='British Racing Green')
    color.save()
    