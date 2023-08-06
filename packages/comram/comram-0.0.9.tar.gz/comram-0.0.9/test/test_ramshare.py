from comram import ramshare
import unittest
import xml.etree.ElementTree as ET


class Test_ramshare(unittest.TestCase):
    def test_init_read_write(self):
        test = ramshare.RamShare("test_share_name", "test_structure")
        test.write_to_tag("tag_1", 99)
        test_2 = int(test.read_tag("tag_1"))
        self.assertEqual(test_2, 99)
        test.unlink()

    def test_length_exception(self):
        test = ramshare.RamShare("test_share_name", "test_structure")
        self.assertRaises(ValueError, test.write_to_tag, "tag_1", 99999999999)
        test.unlink()

    def test_no_data_type(self):
        test = ramshare.RamShare("test_share_name", "test_structure")
        test.write_to_tag("tag_1", 99)
        test.close()
        test_2 = ramshare.RamShare("test_share_name")
        test_3 = int(test_2.read_tag("tag_1"))
        self.assertEqual(test_3, 99)
        test_2.unlink()

    def test_data_type_path(self):
        data_type_path = "data_structures/test_structure.xml"
        test = ramshare.RamShare("test_share_name_2", data_type_path)
        test.write_to_tag("tag_1", 99)
        test_2 = int(test.read_tag("tag_1"))
        self.assertEqual(test_2, 99)
        test.unlink()

    def test_close(self):
        test = ramshare.RamShare("test_share_name", "test_structure")
        test.write_to_tag("tag_1", 99)
        test.close()
        test.unlink()

    def test_data_type_file(self):
        data_structure_path = "data_structures/test_structure.xml"
        data_type = ET.parse(data_structure_path)
        test = ramshare.RamShare("test_share_name_2", data_type_file=data_type)
        test.write_to_tag("tag_1", 99)
        test_2 = int(test.read_tag("tag_1"))
        self.assertEqual(test_2, 99)
        test.unlink()

    def test_len_1_read_write(self):
        test = ramshare.RamShare("test_share_name", "test_structure")
        test.write_to_tag("tag_3", 3)
        test_2 = int(test.read_tag("tag_3"))
        self.assertEqual(test_2, 3)
        test.unlink()

if __name__ == '__main__':
    unittest.main()






