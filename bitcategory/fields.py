#coding: utf-8
from django.core.urlresolvers import reverse_lazy
from django.forms.models import ModelChoiceField
from bitcategory.widgets import HierarchicalSelect


class HierarchicalField(ModelChoiceField):
    '''
    Field which can handles hierarchical structure using multiple
    selects as widgets. All the magic is in `bitcategory/hierarchicalwidget.js`
    so don't forget to include that into form.media when constructing form.
    '''
    def __init__(self, queryset, label=None, initial=None, namespace=None,
                 *args, **kwargs):
        '''
        Ignore queryset - we have to take all options into account.
        The selects are generated via javascript, otherwise it bounds the validation.

        :param: `namespace` is an URL namespace for current Model
        '''
        queryset = queryset.model.objects.all()
        super(HierarchicalField, self).__init__(
            widget=HierarchicalSelect, queryset=queryset, initial=initial,
            label=label, *args, **kwargs)
        # set up own widget instance
        self.widget.model = queryset.model
        if namespace:
            self.widget.url = reverse_lazy("{0}:hierarchical_ajax".format(namespace))
        else:
            self.widget.url = reverse_lazy("hierarchical_ajax")
