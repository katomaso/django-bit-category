from django.shortcuts import render
from testapp.forms import CategoryForm


def index(request):
    ctx = {}
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        ctx = {"form": form}
        if form.is_valid():
            ctx.update(selected=form.cleaned_data['category'])
        return render(request, "index.html", ctx)

    ctx.update({"form": CategoryForm()})
    return render(request, "index.html", ctx)
