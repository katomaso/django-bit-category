#coding: utf-8
import copy

from django.utils.encoding import force_text
from django.forms.widgets import Widget, Select
from django.template.defaultfilters import mark_safe


class HierarchicalSelect(Widget):

    class Media:
        js = ('bitcategory/hierarchicalwidget.js', )

    def __init__(self, attrs=None):
        '''
        :param: `url` url where to send the ajax request
        '''
        super(HierarchicalSelect, self).__init__(attrs)
        self.subwidget = Select
        self.model = None
        self.url = None

    def subwidgets(self, name, value, attrs=None):
        '''
        If there is a value, this creates widgets for all ancestors. If no value
        is given, create only one widget for root level (1)
        '''
        qs = None
        if value:
            qs = list(value.ancestors.order_by("id"))
            if value.first_child is not None:
                qs.append(value.first_child)
        else:
            qs = self.model.objects.filter(level=1)[0:1]

        for item in qs:
            newattrs = copy.copy(attrs)
            newattrs["id"] = "{0}_{1}".format(newattrs["id"], force_text(item.level))
            newattrs["name"] = "{0}_{1}".format(name, force_text(item.level))
            choices = [(None, "-------------"), ]
            choices.extend(list(item.neighbours.values_list("id", "name")))
            yield self.subwidget(attrs=newattrs, choices=choices)

    def subrenders(self, name, value, attrs=None):
        '''
        Grab all created subwidgets and render them using trick with value
        '''
        output = []
        for i, subwidget in enumerate(self.subwidgets(name, value, attrs)):
            if value:
                values = list(value.ancestors.order_by("id").values_list("id", flat=True))
                values.append(None)  # for one extra select when a value is specified
            else:
                values = [None, ]
            subrender = subwidget.render(name=subwidget.attrs["name"], value=values[i])
            output.append(subrender)
        # if there is a value, render one level more
        return "\n".join(output)

    def render(self, name, value=None, attrs=None):
        if value and isinstance(value, (int)):
            value = self.model.objects.get(id=value)
        attrs.update({"data:url": self.url, "class": "hierarchical_widget"})
        return mark_safe(self.subrenders(name, value, attrs))

    def value_from_datadict(self, data, files, name):
        '''
        Find the last name_X and return it's value
        '''
        last = None
        level = 1
        while data.get("{0}_{1}".format(name, level)):
            try:
                intval = int(data.get("{0}_{1}".format(name, level)))
                if intval == 0: break
                last = intval
                level += 1
            except ValueError:
                break
        return last
