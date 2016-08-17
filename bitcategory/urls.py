# coding: utf-8
"""Please include these !without namespace! and with your custom model.

The views included here usually serves for AJAX requests for forms.

The usual way is to put::

    from myapp.models import MyCategory

    urlpatterns = [
        url(r'', include('bitcategory.urls'), {"model": MyCategory})
    ]

By using a namespace you can use more hierarchical models. Then you need to
pass the namespace into a HierarchicalField associated with the custom model.
"""
import six

from django.conf.urls import url
from bitcategory.views import ajax


def patterns(*args):
    try:
        from django.conf.urls import patterns
        if isinstance(args[0], (six.text_type, six.binary_type)):
            return patterns(*args)
        return patterns('', *args)
    except ImportError:
        return args

urlpatterns = patterns(
    url(r'^hierarchical_ajax$', ajax, name="hierarchical_ajax"),
)
