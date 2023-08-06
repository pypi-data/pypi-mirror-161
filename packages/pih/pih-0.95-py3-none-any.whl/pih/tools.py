import re
import string
import random
import json
import os
import sys
from typing import Any, List

sys.path.append("//pih/facade")
from pih.const import DATA_EXTRACTOR, FIELD_NAME_COLLECTION, PASSWORD_GENERATION_ORDER
from pih.collection import FieldItem, FieldItemList

class DataTools:

    @staticmethod
    def represent(data: FieldItemList) -> str:
        return json.dumps(data, cls=FieldItemListEncoder)

    @staticmethod
    def rpc_represent(data: dict) -> str:
        return json.dumps(data) if data is not None else ""

    @staticmethod
    def rpc_unrepresent(value: str) -> dict:
        return json.loads(value) if value is not None and value != "" else {}

    @staticmethod
    def unrepresent(value: str) -> dict:
        object: dict = json.loads(value)
        fields = object["fields"]
        data = object["data"]
        field_list: List = []
        for field_item in fields:
            for field_name in field_item:
                field_item_data = field_item[field_name]
                field_list.append(FieldItem(field_item_data["name"], field_item_data["caption"], bool(
                    field_item_data["visible"])))
        return DataPack.pack(FieldItemList(field_list), data)


class DataPack:

    @staticmethod
    def pack(fields: FieldItemList, data: Any) -> dict:
        return {"fields": fields, "data": data}

    @staticmethod
    def pack_with_fields_name(fields_name: FieldItemList, data: Any) -> dict:
        return {"fields": fields_name, "data": data}


class DataUnpack:

    @staticmethod
    def unpack(data: dict, name: str = DATA_EXTRACTOR.AS_IS) -> Any:
        data_fields = data["fields"]
        return data_fields, DataUnpack.unpack_data(data, name)

    @staticmethod
    def unpack_data(data: dict, name: str = DATA_EXTRACTOR.AS_IS):
        data_result = None
        data_data = data["data"]
        if name == DATA_EXTRACTOR.AS_IS:
            data_result = data_data
        elif name == DATA_EXTRACTOR.USER_NAME:
            data_result = str(
                data_data[FIELD_NAME_COLLECTION.NAME_FULL]).split(" ")[0],
        elif name == DATA_EXTRACTOR.USER_NAME_FULL:
            data_result = data_data[FIELD_NAME_COLLECTION.NAME_FULL]
        return data_result


class PathTools:

    @staticmethod
    def get_current_full_path(file_name: str) -> str:
        return os.path.join(sys.path[0], file_name)


class FieldItemListEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FieldItem):
            return {f"{obj.name}": obj.__dict__}
        if isinstance(obj, FieldItemList):
            return obj.list
        return json.JSONEncoder.default(self, obj)


class PasswordTools:

    @staticmethod
    def check_password(value: str, length: int, special_characters: str) -> bool:
        regexp_string = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[" + special_characters + "])[A-Za-z\d" + special_characters + "]{" + str(length) + ",}$"
        password_checker = re.compile(regexp_string)
        return re.fullmatch(password_checker, value) is not None

    @staticmethod
    def generate_random_password(length: int, special_characters: str, order_list: List[str], special_characters_count: int, alphabets_lowercase_count: int, alphabets_uppercase_count: int, digits_count: int, shuffled: bool):
        # characters to generate password from
        alphabets_lowercase = list(string.ascii_lowercase)
        alphabets_uppercase = list(string.ascii_uppercase)
        digits = list(string.digits)
        characters = list(string.ascii_letters +
                          string.digits + special_characters)
        characters_count = alphabets_lowercase_count + \
            alphabets_uppercase_count + digits_count + special_characters_count

        # check the total length with characters sum count
        # print not valid if the sum is greater than length
        if characters_count > length:
            print("Characters total count is greater than the password length")
            return

        # initializing the password
        password: List[str] = []

        PASSWORD_GENERATION_ORDER

        for order_item in order_list:
            if order_item == PASSWORD_GENERATION_ORDER.SPECIAL_CHARACTER:
             # picking random alphabets
                for i in range(special_characters_count):
                    password.append(random.choice(special_characters))
            elif order_item == PASSWORD_GENERATION_ORDER.LOWERCASE_ALPHABET:
                # picking random lowercase alphabets
                for i in range(alphabets_lowercase_count):
                    password.append(random.choice(alphabets_lowercase))
            elif order_item == PASSWORD_GENERATION_ORDER.UPPERCASE_ALPHABET:
                # picking random lowercase alphabets
                for i in range(alphabets_uppercase_count):
                    password.append(random.choice(alphabets_uppercase))
            elif order_item == PASSWORD_GENERATION_ORDER.DIGIT:
                # picking random digits
                for i in range(digits_count):
                    password.append(random.choice(digits))

        # if the total characters count is less than the password length
        # add random characters to make it equal to the length
        if characters_count < length:
            random.shuffle(characters)
            for i in range(length - characters_count):
                password.append(random.choice(characters))

        # shuffling the resultant password
        if shuffled:
            random.shuffle(password)

        # converting the list to string
        # printing the list
        return "".join(password)
