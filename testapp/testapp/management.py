from bitcategory import models
from django.dispatch import receiver
from django.db.models.signals import post_syncdb


@receiver(post_syncdb, sender=models)
def load_test_categories(sender, **kwargs):
    r1, c = models.Category.objects.get_or_create(name="root1")
    r2, c = models.Category.objects.get_or_create(name="root2")

    c11, c = models.Category.objects.get_or_create(name="cat11", parent=r1)
    c12, c = models.Category.objects.get_or_create(name="cat12", parent=r1)

    c111, c = models.Category.objects.get_or_create(name="cat111", parent=c11)
    c112, c = models.Category.objects.get_or_create(name="cat112", parent=c11)
    c113, c = models.Category.objects.get_or_create(name="cat113", parent=c11)

    c21, c = models.Category.objects.get_or_create(name="cat21", parent=r2)
    c22, c = models.Category.objects.get_or_create(name="cat22", parent=r2)
