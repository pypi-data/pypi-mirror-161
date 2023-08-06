from unittest import TestCase
from lib.utils.inventory_tag import parse_inventory_tag_literal, InventoryTagDict

class TestInventoryTag(TestCase):

    def test_parse_inventory_tag_literal(self):
        inventory_tag = 'tag1; tag2=val2; =tag3; tag4= '
        dt = parse_inventory_tag_literal(inventory_tag)
        self.assertEqual(dt['tag1'], None)
        self.assertEqual(dt['tag2'], 'val2')
        self.assertNotIn('tag3', dt)
        self.assertEqual(dt['tag4'], '')

    def test_InventoryTagDict(self):
        inventory_tag = 'tag1; tag2=val2; =tag3; tag4= '
        itd = InventoryTagDict(inventory_tag)
        self.assertEqual(itd['tag1'], None)
        self.assertEqual(itd['tag2'], 'val2')
        self.assertNotIn('tag3', itd)
        self.assertEqual(itd['tag4'], '')

        itd['tag5'] = 'val5'
        itd['tag6'] = None
        self.assertEqual(itd['tag5'], 'val5')
        self.assertEqual(itd['tag6'], None)

        # 当value的值不为str或者None时，抛出TypeError
        with self.assertRaises(TypeError):
            itd['tag7'] = ['1', '2']

    def test_InventoryTagDict_str(self):
        itd = InventoryTagDict()
        itd['tag1'] = 'val1'
        itd['tag2'] = None

        self.assertEqual(str(itd), 'tag1=val1;tag2;')

        itd2 = InventoryTagDict()
        itd2['tag;1'] = 'val1'
        itd2['tag2='] = None
        self.assertEqual(str(itd2), r'tag\3B1=val1;tag2\3D;')
