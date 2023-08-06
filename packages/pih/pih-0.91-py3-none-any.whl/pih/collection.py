from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


@dataclass
class FieldItem:
    name: str
    caption: str
    visible: bool = True


@dataclass
class FullName:
    last_name: str = None
    first_name: str = None
    middle_name: str = None

    def to_string(self) -> str:
        return "".join([self.last_name, self.first_name, self.middle_name])


@dataclass
class LoginPasswordPair:
    login: str = None
    password: str = None


class FieldItemList:

    list: List[FieldItem]

    def __init__(self, *args):
        self.list = []
        arg_list = list(args)
        for arg_item in arg_list:
            if isinstance(arg_item, FieldItem):
                item: FieldItem = FieldItem(
                    arg_item.name, arg_item.caption, arg_item.visible)
                self.list.append(item)
            elif isinstance(arg_item, FieldItemList):
                for item_list in arg_item.list:
                    item: FieldItem = FieldItem(
                        item_list.name, item_list.caption, item_list.visible)
                    self.list.append(item)
            elif isinstance(arg_item, List):
                self.list.extend(arg_item)

    def get_list(self) -> List[FieldItem]:
        return self.list

    def get_item_and_index_by_field_item_name(self, value: str):
        index: int = -1;
        result: FieldItem = None
        for item in self.list:
            index += 1
            if item.name == value:
                result = item
                break
        return result, -1 if result is None else index

    def position(self, name: str, position: int):
        _, index = self.get_item_and_index_by_field_item_name(name)
        if index != -1:
            self.list.insert(position, self.list.pop(index))
        return self

    def get_name_list(self):
        return list(map(lambda x: str(x.name), self.list))

    def get_caption_list(self):
        return list(map(lambda x: str(x.caption), filter(lambda y: y.visible, self.list)))

    def visible(self, name: str, value: bool):
        item, _ = self.get_item_and_index_by_field_item_name(name)
        if item is not None:
            item.visible = value
        return self

@dataclass
class PasswordSettings:
    length: int
    special_characters: str
    order_list: List[str]
    special_characters_count: int
    alphabets_lowercase_count: int
    alphabets_uppercase_count: int
    digits_count: int = 1
    shuffled: bool = False


@dataclass
class CommandItem:
    group: str
    file_name: str
    description: str
    section: str = ""
    cyclic: bool = True
    confirm_for_continue: bool = True
    enable: bool = True


@dataclass
class CommandLinkItem:
    command_name: str
    data_extractor_name: str


@dataclass
class CommandChainItem:
    input_name: str
    description: str
    list: List[CommandLinkItem]
    confirm_for_continue: bool = True
    enable: bool = True


@dataclass
class LogCommand():
    message: str
    log_channel: Enum
    log_level: Enum
    params: Tuple = None


@dataclass
class ParamItem:
    name: str
    caption: str
    description: str = None
