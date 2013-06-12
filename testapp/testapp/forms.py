from django import forms
from bitcategory.fields import HierarchicalField
from bitcategory.models import Category


class CategoryForm(forms.Form):
    category = HierarchicalField(queryset=Category.objects.all())
