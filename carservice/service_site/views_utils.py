from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def group_required(group_name):
    def in_group(user):
        return user.is_authenticated and user.groups.filter(name=group_name).exists()
    return user_passes_test(in_group)

def render_htmx(request, template_full, template_partial, context):
    if request.htmx:
        return render(request, template_partial, context)
    else:
        return render(request, template_full, context)