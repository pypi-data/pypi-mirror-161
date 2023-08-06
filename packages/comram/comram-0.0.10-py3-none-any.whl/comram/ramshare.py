import xml.etree.ElementTree as ET
import json
import hashlib
from multiprocessing import Process, resource_tracker
from multiprocessing import shared_memory


def remove_shm_from_resource_tracker():
    """Monkey-patch multiprocessing.resource_tracker so SharedMemory won't be tracked

    More details at: https://bugs.python.org/issue38119
    """

    def fix_register(name, rtype):
        if rtype == "shared_memory":
            return
        return resource_tracker._resource_tracker.register(self, name, rtype)
    resource_tracker.register = fix_register

    def fix_unregister(name, rtype):
        if rtype == "shared_memory":
            return
        return resource_tracker._resource_tracker.unregister(self, name, rtype)
    resource_tracker.unregister = fix_unregister

    if "shared_memory" in resource_tracker._CLEANUP_FUNCS:
        del resource_tracker._CLEANUP_FUNCS["shared_memory"]


def write_to_data_structure(self, tag_name, tag_data):
    tag_start_pos = (self.data_dict["tag_dict"][tag_name]["START_POS"]) + self.dict_end_pos
    tag_end_pos = (self.data_dict["tag_dict"][tag_name]["END_POS"]) + self.dict_end_pos + 1
    tag_len = (self.data_dict["tag_dict"][tag_name]["LENGTH"])
    tag_data_str = str(tag_data)

    if len(tag_data_str) <= tag_len:
        encoded_tag = bytes(f"{tag_data_str:<{tag_len}}".encode('utf-8'))
        self.shm.buf[tag_start_pos:tag_end_pos] = encoded_tag

    else:
        raise ValueError("Tag length exceed structure data size")


def read_data_structure(self):
    if self.data_type_file:
        tree = self.data_type_file

    else:
        test_path = self.data_type.split(".")
        if len(test_path) == 1:
            data_type_path = "data_structures/" + self.data_type + ".xml"
        else:
            data_type_path = self.data_type
        tree = ET.parse(data_type_path)

    data_structure_dict = {}
    combined_pos = 0

    root = tree.getroot()
    data_structure_dict["tag_dict"] = {}
    for child in root:
        data_structure_dict["tag_dict"][child.tag] = {}
        data_structure_dict["tag_dict"][child.tag]["LENGTH"] = int(child.attrib["LENGTH"])
        data_structure_dict["tag_dict"][child.tag]["START_POS"] = combined_pos
        data_structure_dict["tag_dict"][child.tag]["END_POS"] = combined_pos + (int(child.attrib["LENGTH"]) - 1)
        if 'INIT_VALUE' in child.attrib:
            data_structure_dict["tag_dict"][child.tag]['INIT_VALUE'] = child.attrib['INIT_VALUE']
        else:
            data_structure_dict["tag_dict"][child.tag]['INIT_VALUE'] = None

        if 'TYPE' in child.attrib:
            data_structure_dict["tag_dict"][child.tag]['TYPE'] = child.attrib['TYPE']
        else:
            data_structure_dict["tag_dict"][child.tag]['TYPE'] = None

        combined_pos = combined_pos + (int(child.attrib["LENGTH"]))
    data_structure_dict["tag_len"] = combined_pos
    return data_structure_dict


class RamShare:
    def __init__(self, share_name, data_type=None, data_type_file=None):
        self.share_name = share_name
        if data_type or data_type_file:
            self.data_type = data_type
            self.data_type_file = data_type_file
            self.data_dict = read_data_structure(self)
            self.data_dict_bytes = json.dumps(self.data_dict).encode('utf-8')
            self.data_dict_checksum = hashlib.md5(self.data_dict_bytes).hexdigest()
            data_dict_checksum_bytes = json.dumps(self.data_dict_checksum).encode('utf-8')
            self.dict_end_pos = len(self.data_dict_bytes) + 45
            shared_size = self.dict_end_pos + self.data_dict["tag_len"]
            encoded_end_dict_pos = f"{str(self.dict_end_pos):<{9}}".encode('utf-8')

            try:
                remove_shm_from_resource_tracker()
                self.shm = shared_memory.SharedMemory(create=True, size=shared_size, name=self.share_name)
                self.shm.buf[0:34] = data_dict_checksum_bytes
                self.shm.buf[35:44] = bytes(encoded_end_dict_pos)
                self.shm.buf[45:len(self.data_dict_bytes) + 45] = self.data_dict_bytes

                for key in self.data_dict["tag_dict"]:
                    if self.data_dict["tag_dict"][key]["INIT_VALUE"]:
                        write_to_data_structure(self, key, self.data_dict["tag_dict"][key]["INIT_VALUE"])


            except:
                remove_shm_from_resource_tracker()
                self.shm = shared_memory.SharedMemory(name=self.share_name)
                shared_checksum_bytes = bytes(self.shm.buf[0:34])
                shared_checksum = json.loads(shared_checksum_bytes.decode('utf-8'))
                if self.data_dict_checksum != shared_checksum:
                    raise ValueError("Data Structure Mismatch")
                pass

        else:
            try:
                remove_shm_from_resource_tracker()
                self.shm = shared_memory.SharedMemory(name=self.share_name)
                self.dict_end_pos = bytes(self.shm.buf[35:44])
                self.dict_end_pos = int(self.dict_end_pos.decode("utf-8"))
                self.dict_bytes = bytes(self.shm.buf[45:self.dict_end_pos])
                self.data_dict = json.loads(self.dict_bytes.decode('utf-8'))

            except:
                raise ValueError("Data Structure missing")
                pass

    def read_tag(self, tag_name):
        tag_start_pos = (self.data_dict["tag_dict"][tag_name]["START_POS"]) + self.dict_end_pos
        tag_end_pos = (self.data_dict["tag_dict"][tag_name]["END_POS"]) + self.dict_end_pos
        tag_output_bytes = bytes(self.shm.buf[tag_start_pos:tag_end_pos])
        tag_output = tag_output_bytes.decode('utf-8')

        if self.data_dict["tag_dict"][tag_name]["TYPE"]:
            if self.data_dict["tag_dict"][tag_name]["TYPE"] == "float":
                tag_output = float(tag_output)

            elif self.data_dict["tag_dict"][tag_name]["TYPE"] == "int":
                tag_output = int(tag_output)

            elif self.data_dict["tag_dict"][tag_name]["TYPE"] == "string":
                tag_output = str(tag_output)

        return tag_output

    def read_all_bytes(self):
        tag_start_pos = self.dict_end_pos
        tag_end_pos = self.data_dict["tag_len"] + self.dict_end_pos
        output_bytes = bytes(self.shm.buf[tag_start_pos:tag_end_pos])
        return output_bytes

    def write_to_tag(self, tag_name, tag_data):
        write_to_data_structure(self, tag_name, tag_data)

    def consume_write_all(self, consume_data):
        tag_start_pos = self.dict_end_pos
        tag_end_pos = self.data_dict["tag_len"] + self.dict_end_pos
        self.shm.buf[tag_start_pos:tag_end_pos] = consume_data

    def close(self):
        self.shm.close()

    def unlink(self):
        self.shm.unlink()
