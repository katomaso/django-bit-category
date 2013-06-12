# coding: utf-8
'''
Please include these !without namespace! and with your custom model.
The views included here usually serves for AJAX requests for forms.

The usual way is to put::

    from myapp.models import MyCategory

    urlpatterns = patterns('',
        url(r'', include('bitcategory.urls'), {"model": MyCategory})
    )

By using a namespace you can use more hierarchical models. Then you need to 
pass the namespace into a HierarchicalField associated with the custom model.
'''
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'bitcategory.views',
    url(r'^hierarchical_ajax$', 'ajax', name="hierarchical_ajax"),
)
