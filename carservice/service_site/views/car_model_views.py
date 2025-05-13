from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..views_utils import render_htmx
from .. import models
from .. import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponse
import json
from crispy_forms.templatetags.crispy_forms_filters import as_crispy_field
from django.contrib import messages
from django.db.models import ProtectedError

class CarModelsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = []
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get("page", 1)
        items_per_page = int(request.GET.get("items_per_page", 12))
        search_query = request.GET.get("search", '')

        search_terms = search_query.split()
        query = Q()

        for term in search_terms:
            query |= Q(model_name__icontains=term) | \
                    Q(car_brand__brand_name__icontains=term) | \
                    Q(body_type__body_type_name__icontains=term) | \
                    Q(engine_type__engine_type_name__icontains=term) | \
                    Q(transmission_type__transmission_type_name__icontains=term) | \
                    Q(drive_type__drive_type_name__icontains=term)

        # Get car models with their related entities
        car_models = models.CarModel.objects.select_related(
            'car_brand',
            'body_type',
            'engine_type',
            'transmission_type',
            'drive_type',
            'suspension_type'
        ).filter(query).order_by('-model_name')

        paginator = Paginator(car_models, items_per_page)
        page_obj = paginator.get_page(page_number)

        context = {
            "car_models": page_obj,
            'car_brands': models.CarBrand.objects.all(),
            'body_types': models.BodyType.objects.all(),
            'engine_types': models.EngineType.objects.all(),
            'transmission_types': models.TransmissionType.objects.all(),
            'drive_types': models.DriveType.objects.all(),
            'suspension_types': models.SuspensionType.objects.all(),
        }

        return render_htmx(request, "car_model/car_models.html", "car_model/_car_model_list.html", context)
    
    def delete(self, request, car_model_id):
        car_model = get_object_or_404(models.CarModel, pk=car_model_id)
        try:
            name = car_model.model_name
            car_model.delete()
            messages.success(request, f"Модель авто '{name}' успішно видалено.")
        except ProtectedError:
            messages.error(request, f"Неможливо видалити модель '{car_model.model_name}', оскільки вона використовується в інших записах.")
        except Exception:
            messages.error(request, f"Сталася невідома помилка при видаленні моделі.")
        finally:
            return self.get(request)
    
def add_car_model(request):
    if request.method == "GET":
        context = {
            "form": forms.CarModelForm()
        }
        return render(request, 'car_model/_car_model_add_form.html', context)
    elif request.method == "POST":
        form = forms.CarModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Модель {form.instance.model_name} була успішно додана")
            response = HttpResponse("")
            response['HX-Trigger'] = 'update-model-list'

            return response
    
def check_model_name(request):
    form = forms.CarModelForm(request.GET)
    return HttpResponse(as_crispy_field(form['model_name']))
    
def view_car_model(request, pk):
    car_model = get_object_or_404(models.CarModel, pk=pk)
    context = {"car_model": car_model}
    return render(request, "car_model/_car_model_card.html", context)

def edit_car_model(request, pk):
    car_model = get_object_or_404(models.CarModel, pk=pk)
    if request.method == "POST":
        form = forms.CarModelForm(request.POST, instance=car_model)
        if form.is_valid():
            form.save()
            messages.success(request, f"Модель {form.instance.model_name} була успішно змінена")
            return render(request, 'car_model/_car_model_card.html', {'car_model': car_model})
    elif request.method == "GET":
        form = forms.CarModelForm(instance=car_model)
        return render(request, 'car_model/_car_model_form.html', {'form': form, 'car_model': car_model})
    
