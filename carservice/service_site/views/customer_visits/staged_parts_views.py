from django.shortcuts import render, get_object_or_404
from .. import models
from ... import views_utils
from django.http import HttpResponse, HttpResponseBadRequest
import uuid
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from datetime import datetime
from django.views.decorators.http import require_http_methods
from ...domain import visit_services as visit_domain

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.view_visitservice'], raise_exception=True)
def add_staged_part(request):
    part_id = request.POST.get('part_id')
    v_service_id = request.POST.get('visit_service_id')

    part_in_station = models.PartInStation.objects.select_related('part', 'part__part_brand', 'part__part_type').get(pk=part_id)
    part = part_in_station.part

    temp_id = str(uuid.uuid4())

    staged_parts = request.session.get(f'staged_parts_{v_service_id}', [])

    staged_part = {
        'temp_id': temp_id,
        'part_id': part_id,
        'part_name': part.part_name,
        'part_brand_name': part.part_brand.brand_name if part.part_brand else 'Unknown',
        'part_type_name': part.part_type.part_type_name if part.part_type else 'Unknown',
        'quantity_per_package': part.quantity_per_package,
        'avaliable_units': part_in_station.quantity,
        'price_per_package': float(part.price_per_package),
        'description': part.description,
        'quantity': 1,
        'price_per_unit': float(part.get_price_per_unit()),
    }

    staged_parts.append(staged_part)
    request.session[f'staged_parts_{v_service_id}'] = staged_parts
    request.session.modified = True

    context = {
        "staged_part": staged_part,
    }

    return render(request, "service_site/visits/_staged_required_part.html", context)

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.view_visitservice'], raise_exception=True)
def update_staged_part(request):
    temp_id = request.POST.get('temp_id')
    v_service_id = request.POST.get('visit_service_id')
    quantity = int(request.POST.get('quantity', 1))

    staged_parts = request.session.get(f'staged_parts_{v_service_id}', [])

    for part in staged_parts:
        if part['temp_id'] == temp_id:
            # Check if quantity is greater than available units
            if quantity > part['avaliable_units']:
                messages.error(request, f"Кількість перевищує доступну ({part['avaliable_units']}).")
                return HttpResponse("")
            elif  quantity < 0:
                messages.error(request, f"Кількість запчастин має бути більшою за 0.")
                return HttpResponse("")
            else:
                part['quantity'] = quantity
            break

    request.session[f'staged_parts_{v_service_id}'] = staged_parts
    request.session.modified = True

    return HttpResponse("")

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.view_visitservice'], raise_exception=True)
def remove_staged_part(request):
    temp_id = request.POST.get('temp_id')
    v_service_id = request.POST.get('visit_service_id')

    staged_parts = request.session.get(f'staged_parts_{v_service_id}', [])
    staged_parts = [p for p in staged_parts if p['temp_id'] != temp_id]

    request.session[f'staged_parts_{v_service_id}'] = staged_parts
    request.session.modified = True

    return HttpResponse("")

@login_required
@require_http_methods(["POST"])
@permission_required(['service_site.change_providedservice', 'service_site.add_providedservice'], raise_exception=True)
def save_staged_parts(request):
    v_service_id = request.POST.get('visit_service_id')
    staged_parts = request.session.get(f'staged_parts_{v_service_id}', [])
    visit_service = models.VisitService.objects.get(pk=v_service_id)
    employee = request.user.employee

    if models.ProvidedService.objects.filter(visit_service=visit_service).exists():
        provided_service = models.ProvidedService.objects.get(visit_service=visit_service)
    else:
        provided_service = models.ProvidedService.objects.create(
            visit_service=visit_service,
            employee=employee,
            provided_date=datetime.now(),
        )

    for staged in staged_parts:
        part_in_station = models.PartInStation.objects.select_related("part").get(pk=staged['part_id'])
        if part_in_station.quantity < staged['quantity']:
            messages.error(request, f'При збереженні запчастини ({part_in_station.part.part_name}) для використання сталась помилка (в наявності: {part_in_station.quantity}, ви запросили: {staged['quantity']}). Додавання цієї запчастини пропущено') 
        else:
            models.RequiredPart.objects.create(
                provided_service=provided_service,
                part_in_station=part_in_station,
                quantity=staged['quantity']
            )
            part_in_station.quantity -= staged['quantity']
            part_in_station.save()

    if f'staged_parts_{v_service_id}' in request.session:
        del request.session[f'staged_parts_{v_service_id}']
        request.session.modified = True

    context = views_utils.get_visit_service_with_part_search_context(request, v_service_id)
    rendered = render_to_string("service_site/visits/_required_parts_search_widget.html", context, request=request)
    response = HttpResponse(rendered)
    response['HX-Trigger'] = 'update-visit-services'
    messages.success(request, "Дані послуги оновлені.")
    return response

@login_required
@require_http_methods(["DELETE"])
@permission_required(['service_site.delete_requiredpart'], raise_exception=True)
def delete_required_part(request, required_part_id):
    required_part = get_object_or_404(
        models.RequiredPart.objects.select_related("provided_service__visit_service", "part_in_station"),
        pk=required_part_id
    )

    try:
        visit_domain.delete_required_part(required_part)

        context = views_utils.get_visit_service_with_part_search_context(
            request, required_part.provided_service.visit_service.pk
        )
        rendered = render_to_string("service_site/visits/_required_parts_search_widget.html", context, request=request)

        response = HttpResponse(rendered)
        response['HX-Trigger'] = 'update-visit-services'
        messages.success(request, "Запчастину успішно видалено.")
        return response

    except Exception:
        messages.error(request, "Сталася помилка при видаленні.")
        return HttpResponseBadRequest()
    

@login_required
@require_http_methods(["GET"])
@permission_required(['service_site.change_providedservice'], raise_exception=True)
def visit_service_with_part_search(request, visit_service_id):
    context = views_utils.get_visit_service_with_part_search_context(request, visit_service_id)

    if f'staged_parts_{visit_service_id}' in request.session:
        del request.session[f'staged_parts_{visit_service_id}']
        request.session.modified = True

    return render(request, "service_site/visits/_required_parts_search_widget.html", context)
    

