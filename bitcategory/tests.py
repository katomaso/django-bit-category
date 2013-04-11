from __future__ import absolute_import
from django.test import TestCase

from .models import Category, HierarchicalModel


class UnitTests(TestCase):

    def test_bit_mask(self):
        hm = HierarchicalModel(parent=None, level=1)
        self.assertEqual(hm._mask_for(1), 0b11111000000000000000000000000000)
        self.assertEqual(hm._mask_for(2), 0b11111111110000000000000000000000)
        self.assertEqual(hm._mask_for(3), 0b11111111111111100000000000000000)
        self.assertEqual(hm._mask_for(4), 0b11111111111111111111000000000000)
        self.assertEqual(hm._mask_for(5), 0b11111111111111111111111110000000)
        self.assertEqual(hm._mask_for(6), 0b11111111111111111111111111111100)

    def test_bit_offset(self):
        hm = HierarchicalModel(parent=None, level=1)
        self.assertEqual(hm._get_left_offset(), 5)
        self.assertEqual(hm._get_left_offset(1), 5)
        self.assertEqual(hm._get_left_offset(2), 10)

        self.assertEqual(hm._get_right_offset(), 27)
        self.assertEqual(hm._get_right_offset(2), 22)

    def test_min_max(self):
        hm = HierarchicalModel(parent=None, level=1)
        self.assertEqual(hm.min, 0b00001000000000000000000000000000)
        self.assertEqual(hm.max, 0b11111000000000000000000000000000)


class ModelTest(TestCase):

    def test_get_free_id(self):
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
