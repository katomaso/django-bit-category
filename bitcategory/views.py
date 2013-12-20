#coding: utf-8
import json
from django.http import HttpResponse, HttpResponseBadRequest

from bitcategory.models import HierarchicalModel


def ajax(request, model):
    '''
    Should be called via ajax/get request. It expects two parameters in GET
    request: `id` the ID of a calling model and `caller` - an (HTML) ad attribute of
    the calling widget.

    :param: `model` has to be set in your urls.py with default argument - used model as
    `       `url(r"^cats/", 'categories_for', {"model": YourModel})
    :rvalue: returns all descendant of a caller in it's next level in JSON
                         {caller: id_of_caller (got from GET['caller'],
                          items: [(key, value), (key, value)]
                          level: <int> // item's level
                          } or HTTP 400
    '''
    if not issubclass(model, HierarchicalModel):
        raise ValueError("Given model has to be a subclass of a HierarchicalModel")
    try:
        pk = int(request.GET["id"])
        item = model.objects.get(id=pk)
    except (ValueError, KeyError):
        return HttpResponseBadRequest("The request has to contain an valid int 'id'")
    except model.DoesNotExist:
        return HttpResponseBadRequest("Wanted hierarchical model does not exist")
    items = item.descendants.filter(level=item.level+1).values_list("id", "name")
    data = {"caller": request.GET.get("caller", ""),
            "items": list(items),
            "level": item.level+1}
    return HttpResponse(json.dumps(data))
