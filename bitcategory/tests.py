from __future__ import absolute_import
from django.test import TestCase

from .models import Category


class UnitTests(TestCase):

    def test_bit_mask(self):
        """We can't use HierarchicalModel here.

        Since django 1.6. one can't instantiate an abstract model with foreign key.
        """
        hm = Category(parent=None, level=1, name="dummy")
        self.assertEqual(hm._mask_for(1), 0b11111000000000000000000000000000)
        self.assertEqual(hm._mask_for(2), 0b11111111110000000000000000000000)
        self.assertEqual(hm._mask_for(3), 0b11111111111111100000000000000000)
        self.assertEqual(hm._mask_for(4), 0b11111111111111111111000000000000)
        self.assertEqual(hm._mask_for(5), 0b11111111111111111111111110000000)
        self.assertEqual(hm._mask_for(6), 0b11111111111111111111111111111100)

    def test_bit_offset(self):
        hm = Category(parent=None, level=1, name="dummy")
        self.assertEqual(hm._get_left_offset(), 5)
        self.assertEqual(hm._get_left_offset(1), 5)
        self.assertEqual(hm._get_left_offset(2), 10)

        self.assertEqual(hm._get_right_offset(), 27)
        self.assertEqual(hm._get_right_offset(2), 22)

    def test_min_max(self):
        hm = Category(parent=None, level=1, name="dummy")
        self.assertEqual(hm.min, 0b00001000000000000000000000000000)
        self.assertEqual(hm.max, 0b11111000000000000000000000000000)


class ModelTest(TestCase):

    def test_get_free_id(self):
        Category.objects.all().delete()  # WTF why!?
        # empty db
        cat1 = Category(parent=None, level=1, name="cat1")
        self.assertEqual(cat1.get_free_id(), 0b00001000000000000000000000000000)
        cat1.save()
        # root
        cat2 = Category(parent=None, level=1, name="cat2")
        self.assertEqual(cat2.get_free_id(), 0b00010000000000000000000000000000)
        cat2.save()
        cat3 = Category(parent=None, level=1, name="cat3")
        self.assertEqual(cat3.get_free_id(), 0b00011000000000000000000000000000)
        cat3.save()
        # non-root
        cat21 = Category(parent=cat2, level=2, name="cat21")
        self.assertEqual(cat21.get_free_id(), 0b00010000010000000000000000000000)
        cat21.save()
        cat22 = Category(parent=cat2, level=2, name="cat22")
        self.assertEqual(cat22.get_free_id(), 0b00010000100000000000000000000000)
        cat22.save()
        # counts
        self.assertEqual(cat22.descendants.count(), 1)  # itself
        self.assertEqual(cat22.ancestors.count(), 2)  # itself, root
        self.assertEqual(cat22.ancestors[0], cat2)  # the last one has to be the root
        self.assertEqual(cat22.ancestors[1], cat22)  # the last one has to be the root
        self.assertEqual(cat22.root, cat2)  # the last one has to be the root
        # spaces in ids line
        cat23 = Category(parent=cat2, level=2, name="cat23")
        self.assertEqual(cat23.get_free_id(), 0b00010000110000000000000000000000)
        cat23.save()
        cat22.delete()
        self.assertFalse(Category.objects.filter(id=0b00010000100000000000000000000000).exists())

        cat22 = Category(parent=cat2, level=2, name="cat22")
        self.assertEqual(cat22.get_free_id(), 0b00010000100000000000000000000000)
        cat22.save()
        # counts
        cat221 = Category(parent=cat22, level=3, name="cat221")
        self.assertEqual(cat221.get_free_id(), 0b00010000100000100000000000000000)
        cat221.save()
        self.assertEqual(cat22.descendants.count(), 2)  # itself
        self.assertEqual(cat22.descendants[0], cat22)  # the last one has to be the root
        self.assertEqual(cat22.descendants[1], cat221)  # the last one has to be the root
        self.assertEqual(cat22.ancestors.count(), 2)  # itself, root
        self.assertEqual(cat22.ancestors[0], cat2)  # the last one has to be the root
        self.assertEqual(cat22.ancestors[1], cat22)  # the last one has to be the root
        self.assertEqual(cat22.root, cat2)  # the last one has to be the root

    def test_gt(self):
        hm1 = Category(parent=None, level=1, name="cat1")
        hm1.save()
        hm11 = Category(parent=hm1, level=2, name="cat11")
        hm11.save()
        hm2 = Category(parent=None, level=1, name="cat2")
        hm2.save()
        self.assertTrue(hm1 > hm11)
        self.assertTrue(hm1 > hm1)  # this might feel akward
        self.assertFalse(hm1 > hm2)
        self.assertFalse(hm11 > hm1)

    def test_contains(self):
        hm1 = Category(parent=None, level=1, name="cat1")
        hm1.save()
        hm11 = Category(parent=hm1, level=2, name="cat11")
        hm11.save()
        hm12 = Category(parent=hm1, level=2, name="cat12")
        hm12.save()
        hm2 = Category(parent=None, level=1, name="cat2")
        hm2.save()
        hm22 = Category(parent=hm2, level=2, name="cat22")
        hm22.save()
        hm121 = Category(parent=hm12, level=3, name="cat121")
        hm121.save()
        self.assertTrue(hm1 in hm1)
        self.assertTrue(hm11 in hm1, "{:b} in {:b} when mask {:b}".format(hm11.id, hm1.id, hm1._mask_for(hm1.level)))
        self.assertTrue(hm12 in hm1)
        self.assertTrue(hm121 in hm1)
        self.assertTrue(hm22 in hm2)
        self.assertTrue(hm2 in hm2)
        self.assertFalse(hm1 in hm2)
        self.assertFalse(hm1 in hm11)
        self.assertFalse(hm1 in hm12)
        self.assertFalse(hm1 in hm121)
        self.assertFalse(hm22 in hm1)

    def test_relations(self):
        Category.objects.all().delete()  # WTF why!?
        cat1 = Category.objects.create(parent=None, name="cat1")
        cat2 = Category.objects.create(parent=None, name="cat2")
        cat3 = Category.objects.create(parent=None, name="cat3")
        cat21 = Category.objects.create(parent=cat2, name="cat21")
        cat22 = Category.objects.create(parent=cat2, name="cat22")
        cat23 = Category.objects.create(parent=cat2, name="cat23")
        cat24 = Category.objects.create(parent=cat2, name="cat24")
        cat31 = Category.objects.create(parent=cat3, name="cat31")
        cat32 = Category.objects.create(parent=cat3, name="cat32")
        cat221 = Category.objects.create(parent=cat22, name="cat221")
        cat222 = Category.objects.create(parent=cat22, name="cat222")

        self.assertEqual(cat1.neighbours.count(), 3)

        self.assertEqual(cat21.neighbours.count(), 4)
        self.assertEqual(cat22.neighbours.count(), 4)
        self.assertEqual(cat23.neighbours.count(), 4)
        self.assertEqual(cat24.neighbours.count(), 4)

        self.assertEqual(cat31.neighbours.count(), 2)
        self.assertEqual(cat32.neighbours.count(), 2)

        self.assertEqual(cat221.neighbours.count(), 2)
        self.assertEqual(cat222.neighbours.count(), 2)
