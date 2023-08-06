import abc
from dataclasses import dataclass
import enum
from getpass import getpass
import os
import re
import sys
from typing import Any, Callable, Dict, Generic, List, TypeVar
import colorama
from colorama import Back, Style
from prettytable import PrettyTable
import win32com.client

#sys.path.append("//pih/facade")
from pih.collection import CommandChainItem, CommandLinkItem, FieldItem, CommandItem, FullName, PasswordSettings
from pih.const import DATA_EXTRACTOR, FACADE, EXECUTOR, FIELD_NAME_COLLECTION, LOCAL_COMMAND_LIST_DICT, NAME_POLICY_CONST, FIELD_COLLECTION, PASSWORD
from pih.rpc import RPC
from pih.tools import DataTools, DataUnpack, PasswordTools


class NotImplemented(BaseException):
    pass


class NotFound(BaseException):
    pass


class UserInterruption(BaseException):
    pass


class CommandNameIsExistsAlready(BaseException):
    pass


class CommandFullFileNameIsExistAlready(Exception):
    pass


class CommandNameIsNotExists(Exception):
    pass


@dataclass
class Command:
    group: str
    command_name: str
    file: str
    description: str
    section: str
    cyclic: bool
    confirm_for_continue: bool = True


@dataclass
class CommandLink:
    command_name: str
    data_extractor_name: str


@dataclass
class CommandChain:
    name: str
    input_name: str
    description: str
    list: List[CommandLink]
    confirm_for_continue: bool = True
    enable: bool = True


T = TypeVar('T')


class GenericCommandList(Generic[T]):

    def __init__(self):
        self.command_list: List[T] = []
        self.name_dict: Dict[str, T] = {}
        self.index_dict: Dict[int, str] = {}
        self.index = 0

    def length(self) -> int:
        return len(self.command_list)

    def get_by_index(self, index: int) -> T:
        return self.name_dict[self.index_dict[index]]

    def get_by_name(self, name: str) -> T:
        name = name.lower()
        for key in self.name_dict:
            key_lower = key.lower()
            if key_lower == name:
                return self.name_dict[key]
        #raise KeyError
        return None

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if self.index > self.length():
            self.index = 0
            raise StopIteration
        return self.index, self.get_by_index(self.index - 1)


class CommandList(GenericCommandList[Command]):

    def register(self, command: Command) -> None:
        def get_command_file_name(command: Command) -> str:
            return command.group + command.file + command.section
        if command.command_name in map(lambda item: item.command_name, self.command_list):
            raise CommandNameIsExistsAlready()
        if get_command_file_name(command) in map(lambda item: get_command_file_name(item), self.command_list):
            raise CommandFullFileNameIsExistAlready(
                f"{command.command_name}: {get_command_file_name(command)}")
        self.command_list.append(command)
        self.name_dict[command.command_name] = command
        self.index_dict[self.length() - 1] = command.command_name


class CommandChainList(GenericCommandList[CommandChain]):

    def register(self, item: CommandChain) -> None:
        if item.name in map(lambda item: item.name, self.command_list):
            raise CommandNameIsExistsAlready()
        self.command_list.append(item)
        self.name_dict[item.name] = item
        self.index_dict[self.length() - 1] = item.name


class ICommandListStorage(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "get_command_list") and
                callable(subclass.get_command_list) or
                NotImplemented)

    @abc.abstractmethod
    def get_command_list(self) -> CommandList:
        raise NotImplemented


class IInfoOwner(metaclass=abc.ABCMeta):

    PARAMS: str = "--info"

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "get_info") and
                callable(subclass.get_info) or
                NotImplemented)

    @abc.abstractmethod
    def get_info(self) -> Dict:
        raise NotImplemented


class CommandTools:

    @staticmethod
    def get_command_group_path(command: Command) -> str:
        return f"{FACADE.PATH}{command.group}{FACADE.COMMAND_SUFFIX}"

    @staticmethod
    def get_file_extension(file: str) -> str:
        return "" if file.find(".") == -1 else file.split(".")[-1]

    @staticmethod
    def convert_command_to_command_file_path(command: Command) -> str:
        shell = win32com.client.Dispatch("WScript.Shell")
        return shell.CreateShortCut(command.file).Targetpath if CommandTools.get_file_extension(command.file) == "lnk" else command.file

    @staticmethod
    def get_executor_path(path: str) -> str:
        return EXECUTOR.get(CommandTools.get_file_extension(path))

    @staticmethod
    def convert_command_file_path_for_executor(path: str, executor: str) -> str:
        if executor == EXECUTOR.POWERSHELL_EXECUTOR or executor == EXECUTOR.VBS_EXECUTOR:
            path = f".\\{path}"
        return path

    @staticmethod
    def set_cwd(path: str) -> None:
        os.chdir(path)

    @staticmethod
    def check_for_command_paths_exsit(command: Command):
        command_group_directory_path = CommandTools.get_command_group_path(
            command)
        if not os.path.exists(command_group_directory_path):
            return CommandPathExsitsStatus.COMMAND_GROUP_DIRECTORY_IS_NOT_EXSITS
        CommandTools.set_cwd(command_group_directory_path)
        command.file = CommandTools.convert_command_to_command_file_path(
            command)
        if not os.path.exists(command.file):
            return CommandPathExsitsStatus.COMMAND_FILE_IS_NOT_EXSITS
        command.file = CommandTools.convert_command_file_path_for_executor(
            command.file, CommandTools.get_executor_path(command.file))
        return CommandPathExsitsStatus.OK
#


class CommandPathExsitsStatus(enum.Enum):
    OK: int = 0
    COMMAND_GROUP_DIRECTORY_IS_NOT_EXSITS: int = 1
    COMMAND_FILE_IS_NOT_EXSITS: int = 2


class LocalCommandListStorage(ICommandListStorage):

    def __init__(self, command_list_dict: dict = LOCAL_COMMAND_LIST_DICT):
        self.command_list_dict = command_list_dict
        self.command_list: CommandList = CommandList()
        self.command_chain_list: CommandChainList = CommandChainList()
        for command_name in self.command_list_dict:
            command_item_obj: Any = self.command_list_dict[command_name]
            if isinstance(command_item_obj, CommandItem):
                command_item: CommandItem = command_item_obj
                if command_item.enable:
                    command: Command = self.convert_to_command(
                        command_name, command_item)
                    try:
                        command_paths_exsits_check_status = CommandTools.check_for_command_paths_exsit(
                            command)
                        if command_paths_exsits_check_status == CommandPathExsitsStatus.COMMAND_GROUP_DIRECTORY_IS_NOT_EXSITS:
                            PR.red(
                                f"Command {command.command_name}: group directory is not exsits!")
                        elif command_paths_exsits_check_status == CommandPathExsitsStatus.COMMAND_FILE_IS_NOT_EXSITS:
                            PR.red(
                                f"Command {command.command_name}: file is not exsits!")
                        elif command_paths_exsits_check_status == CommandPathExsitsStatus.OK:
                            self.command_list.register(command)
                    except CommandFullFileNameIsExistAlready:
                        PR.red(
                            f"Command: {command.command_name} is already exsits!")
        for command_name in self.command_list_dict:
            command_item_obj: Any = self.command_list_dict[command_name]
            if isinstance(command_item_obj, CommandChainItem):
                command_chain_item: CommandChainItem = self.command_list_dict[command_name]
                if command_chain_item.enable:
                    if self.command_list.get_by_name(command_name) is None:
                        try:
                            self.command_chain_list.register(
                                self.convert_to_command_chain(command_name, command_chain_item))
                        except CommandNameIsNotExists as error:
                            PR.red(
                                f"Command {command_name}: command link: {error} is not exsits!")
                    else:
                        PR.red(
                            f"Command: {command_chain_item.name} is already exsits!")

    def convert_to_command(self, name: str, command_item: CommandItem) -> Command:
        if name not in self.command_list_dict:
            raise CommandNameIsNotExists
        return Command(command_item.group, name,
                       command_item.file_name,
                       command_item.description,
                       command_item.section,
                       command_item.cyclic)

    def convert_to_command_chain(self, name: str, command_chain_item: CommandChainItem) -> CommandChain:
        if name not in self.command_list_dict:
            raise CommandNameIsNotExists
        list_command_chain: List[CommandChain] = []
        for link_item_obj in command_chain_item.list:
            link_item: CommandLinkItem = link_item_obj
            if self.command_list.get_by_name(link_item.command_name) is not None:
                list_command_chain.append(CommandLink(
                    link_item.command_name, link_item.data_extractor_name))
            else:
                raise CommandNameIsNotExists(link_item.command_name)
        return CommandChain(name,
                            command_chain_item.input_name,
                            command_chain_item.description,
                            list_command_chain,
                            command_chain_item.confirm_for_continue,
                            command_chain_item.enable)

    def get_command_list(self) -> CommandList:
        return self.command_list

    def get_command_chain_list(self) -> CommandChainList:
        return self.command_chain_list

class NamePolicy:
    
    @staticmethod
    def convert_to_login(full_name: FullName) -> FullName:
        from transliterate import translit
        return FullName(
            translit(full_name.last_name[0], 'ru', reversed=True).lower(),
            translit(full_name.first_name[0], 'ru', reversed=True).lower(),
            translit(full_name.middle_name[0], 'ru', reversed=True).lower())

    @staticmethod
    def convert_to_alternative_login(login_list: FullName) -> FullName:
        return FullName(login_list.first_name, login_list.middle_name, login_list.last_name)


class PIH:

    version: str = "0.91"

    class DATA:

        @staticmethod
        def represent(data: dict) -> str:
            return DataTools.represent(data)

        @staticmethod
        def generate_password(settings: PasswordSettings = None) -> str:
            settings = settings or PASSWORD.SETTINGS.DEFAULT
            return PasswordTools.generate_random_password(settings.length, settings.special_characters,
             settings.order_list, settings.special_characters_count, 
             settings.alphabets_lowercase_count, settings.alphabets_uppercase_count, 
             settings.digits_count, settings.shuffled)

        def generate_login(full_name: FullName) -> (str | None):
            login: FullName = NamePolicy.convert_to_login(full_name)
            result = login.to_string()
            if PIH.CHECK.user_is_exsits_by_login(result):
                PR.red(f"Login {result} is not free")
                login = NamePolicy.convert_to_alternative_login(
                    login)
                result = login.to_string()
                if PIH.CHECK.user_is_exsits_by_login(result):
                    PR.red(f"Login {result} is not free")
                    return None
                else:
                    PR.green(f"\nAlternative login {result} is free")
            else:
                PR.green(f"Login {result} is free")
            return result

        @staticmethod
        def mark_by_tab_number(value: str) -> dict:
            return DataTools.unrepresent(RPC.ORION.get_mark_by_tab_number(value))

        @staticmethod
        def mark_by_person_name(value: str) -> dict:
            return DataTools.unrepresent(RPC.ORION.get_mark_by_person_name(value))

        @staticmethod
        def free_marks() -> dict:
            return DataTools.unrepresent(RPC.ORION.get_free_marks())

        @staticmethod
        def free_marks_by_group(group: Dict) -> dict:
            return DataTools.unrepresent(RPC.ORION.get_free_marks_by_group(group))

        @staticmethod
        def free_marks_group_statistics() -> dict:
            return DataTools.unrepresent(RPC.ORION.get_free_marks_group_statistics())

    class INPUT:


        @staticmethod
        def login():
            return input("Enter login:")

        @staticmethod
        def index(caption: str, length: int, pre_action: Callable = None) -> int:
            selected_index = -1
            while True:
                if pre_action is not None:
                    pre_action()
                if length == 1:
                    return 0
                selected_index = input(PR.green_str(caption + f" (from 1 to {length}):", "", " "))
                if selected_index == "":
                    selected_index = 1
                selected_index = int(selected_index) - 1
                if selected_index >= 0 and selected_index < length:
                    return selected_index
               
        @staticmethod
        def tab_number(check: bool = True) -> str:
            while True:
                PR.green("Enter tab number:")
                tab_number = input()
                if check:
                    if PIH.CHECK.tab_number(tab_number):
                        return tab_number
                    else:
                        PR.red("Wrong tab number")
                return tab_number

        @staticmethod
        def password(secret: bool = True, check: bool = False, settings: PasswordSettings = None) -> str:
            PR.cyan("Set password:")
            while True:
                value = getpass(" ") if secret else input()
                if not check:
                    return value
                elif PIH.CHECK.password(value, settings):
                    return value
                else:
                    PR.red("Password not pass checking")

        @staticmethod
        def generate_password(settings: PasswordSettings = None) -> str:
            while True:  
                password = PIH.DATA.generate_password(settings)
                PR.blue(f"Generated password is {password}")
                if PIH.INPUT.yes_no("Use this password?"):
                    return password
                else:
                    pass

        @staticmethod
        def same_if_empty(caption: str, src_value: str) -> str:
            value = input(caption)
            if value == "":
                value = src_value
            return value

        @staticmethod
        def name() -> str:
            PR.green("Enter part of name:")
            return input()

        @staticmethod
        def full_name() -> FullName:
            full_name: FullName = FullName()
            while(True):
                last_name: str = input("Введите фамилию:")
                last_name = last_name.strip()
                if PIH.CHECK.name_length(last_name):
                    full_name.last_name = last_name
                    break
                else:
                    pass
            while(True):
                first_name: str = input("Введите имя:")
                first_name = first_name.strip()
                if PIH.CHECK.name_length(first_name):
                    full_name.first_name = first_name
                    break
                else:
                    pass
            while(True):
                middle_name: str = input("Введите отчество:")
                middle_name = middle_name.strip()
                if PIH.CHECK.name_length(middle_name):
                    full_name.middle_name = middle_name
                    break
                else:
                    pass
            return full_name

        @staticmethod
        def yes_no(text: str = " ") -> bool:
            answer = input(
                f"{text}{' ' if text != '' else ''}{PR.red_str('Yes (Yes|Y|1)')} {PR.green_str('No (Enter|Another)')}:")
            answer = answer.lower()
            return answer == "y" or answer == "yes" or answer == "1"

        @staticmethod
        def free_mark() -> dict:
            mark: dict = None
            group: dict = None
            while True:
                if PIH.INPUT.yes_no("Select group for free mark by search person's group by person name?"):
                    result = PIH.DATA.mark_by_person_name(PIH.INPUT.name())
                    data = DataUnpack.unpack_data(result)
                    length = len(data)
                    if length > 0:
                        PIH.VISUAL.show_table_with_caption_first_title_is_centered(
                        result, "Search by name: ", True)
                        selected_index = PIH.INPUT.index(
                            "Choose group by enter index", length)
                        group = data[selected_index]
                    else:
                        PR.red("No person with enterd name")
                else:
                    result = PIH.DATA.free_marks_group_statistics()
                    data = DataUnpack.unpack_data(result)
                    length = len(data)
                    if length > 0:
                        PIH.VISUAL.show_free_marks_group_statistics_for_data(
                            result, True)
                        selected_index = PIH.INPUT.index(
                            "Choose group by enter index", length)
                        group = data[selected_index]
                    else:
                        PR.red("No free marks!")
                        return None
                if group is not None: 
                    result = PIH.DATA.free_marks_by_group(group)
                    data = DataUnpack.unpack_data(result)
                    length = len(data)
                    if length > 0:
                        PIH.VISUAL.show_free_marks_by_group_for_data(
                            group, result, True)
                        selected_index = PIH.INPUT.index(
                            "Choose mark by enter index", length)
                        mark = data[selected_index]
                        return mark
                    else:
                        PR.red(f"No free marks for group {group[FIELD_NAME_COLLECTION.GROUP_NAME]}!")
                else:
                    pass

    class CHECK:

        @staticmethod
        def  user_is_exsits_by_login(value: str) -> bool:
            return RPC.AD.user_is_exsits_by_login(value)

        @staticmethod
        def tab_number(value: str) -> bool:
            return re.fullmatch(r"[0-9]+", value) is not None

        @staticmethod
        def name_length(value: str) -> bool:
            return len(value) >= NAME_POLICY_CONST.FULL_NAME_PART_ITEM_MIN_LENGTH

        @staticmethod
        def password(value: str, settings: PasswordSettings = None) -> bool:
            settings = settings or PASSWORD.SETTINGS.DEFAULT
            return PasswordTools.check_password(value, settings.length, settings.special_characters)

    class VISUAL:

        @staticmethod
        def init() -> None:
            PR.init()

        @staticmethod
        def SHOW_FACADE_HEADER() -> None:
            PR.init()
            PR.cyan("█▀█ ▄▀█ █▀▀ █ █▀▀ █ █▀▀   █ █▄░█ ▀█▀ █▀▀ █▀█ █▄░█ ▄▀█ ▀█▀ █ █▀█ █▄░█ ▄▀█ █░░   █░█ █▀█ █▀ █▀█ █ ▀█▀ ▄▀█ █░░")
            PR.cyan("█▀▀ █▀█ █▄▄ █ █▀░ █ █▄▄   █ █░▀█ ░█░ ██▄ █▀▄ █░▀█ █▀█ ░█░ █ █▄█ █░▀█ █▀█ █▄▄   █▀█ █▄█ ▄█ █▀▀ █ ░█░ █▀█ █▄▄")
            print(f"Version: {PIH.version}")

        @staticmethod
        def SHOW_SERVER_HEADER(server_name: str) -> None:
            PR.init()
            PR.cyan("█▀█ █ █░█")
            PR.cyan("█▀▀ █ █▀█")
            print(f"Version: {PIH.version}")
            PR.green(f"Server {server_name}")

        @staticmethod
        def show_free_marks() -> None:
            PIH.VISUAL.show_table_with_caption_first_title_is_centered(
                PIH.DATA.free_marks(), "Free marks:")

        @staticmethod
        def show_mark_by_tab_number(value: str) -> None:
            PIH.VISUAL.show_mark_by_tab_number_for_data(PIH.DATA.mark_by_tab_number(value))

        @staticmethod
        def show_mark_by_tab_number_for_data(data: dict) -> None:
            PIH.VISUAL.show_table_with_caption_first_title_is_centered(
                data, "Mark by tab number:")

        @staticmethod
        def show_free_marks_group_statistics(use_index: bool) -> None:
            PIH.VISUAL.show_free_marks_group_statistics_for_data(
                PIH.DATA.free_marks_group_statistics(), use_index)

        @staticmethod
        def show_free_marks_by_group(group: Dict, use_index: bool = False) -> None:
            PIH.VISUAL.show_free_marks_by_group_for_data(
                PIH.DATA.free_marks_by_group(group), use_index)

        @staticmethod
        def show_free_marks_group_statistics_for_data(data: dict, use_index: bool) -> None:
            PIH.VISUAL.show_table_with_caption_last_title_is_centered(data, "Free mark group statistics:", use_index)

        @staticmethod
        def show_free_marks_by_group_for_data(group: Dict, data: dict, use_index: bool) -> None:
            group_name = group[FIELD_NAME_COLLECTION.GROUP_NAME]
            PIH.VISUAL.show_table_with_caption_last_title_is_centered(
                data, f"Free mark for group {group_name}:", use_index)


        @staticmethod
        def show_table_with_caption_first_title_is_centered(data: Dict, caption: str, use_index: bool = False) -> None:
            def modify_table(table: PrettyTable, caption_list: List[str]):
                table.align[caption_list[int(use_index)]] = "c"
            PIH.VISUAL.show_table_with_caption(
                data, caption, modify_table, use_index)


        @staticmethod
        def show_table_with_caption_last_title_is_centered(data: Dict, caption: str, use_index: bool = False) -> None:
            def modify_table(table: PrettyTable, caption_list: List[str]):
                table.align[caption_list[-1]] = "c"
            PIH.VISUAL.show_table_with_caption(
                data, caption, modify_table, use_index)

        @staticmethod
        def show_table_with_caption(data: Dict, caption: str = None, modify_table_handler: Callable = None, use_index: bool = False) -> None:
            PIH.VISUAL.init()
            if caption is not None:
                PR.cyan(caption)
            field_list, result = DataUnpack.unpack(data, DATA_EXTRACTOR.AS_IS)
            if use_index:
                field_list.list.insert(0, FIELD_COLLECTION.INDEX)
            caption_list: List = field_list.get_caption_list()
            def create_table(caption_list: List[str]) -> PrettyTable:
                table: PrettyTable = PrettyTable(caption_list)
                table.align = "l"
                if use_index:
                    table.align[caption_list[0]] = "c"
                return table
            table: PrettyTable = create_table(caption_list)
            if modify_table_handler is not None:
                modify_table_handler(table, caption_list)
            if len(result) == 0:
                PR.red("Not found!")
            else:
                for index, item in enumerate(result):
                    row_data = []
                    for field_item_obj in field_list.get_list():
                        field_item: FieldItem = field_item_obj
                        if field_item.name == FIELD_COLLECTION.INDEX.name:
                            row_data.append(str(index + 1))
                        elif field_item.visible and field_item.name in item:
                            row_data.append(item[field_item.name])
                    table.add_row(row_data)
                print(table)


class PR:

    @staticmethod
    def init() -> None:
        colorama.init()

    @staticmethod
    def color_str(color: int, string: str, before_text: str = "", after_text: str = "") -> str:
        return f"{before_text}{color}{string}{Back.RESET}{after_text}"

    @staticmethod
    def color(string: str) -> None:
        print(string)

    @staticmethod
    def green_str(string: str, before_text: str = "", after_text: str = "") -> str:
        return PR.color_str(Back.GREEN, string, before_text, after_text)

    @staticmethod
    def green(string: str, before_text: str = "", after_text: str = "") -> None:
        PR.color(PR.green_str(string, before_text, after_text))

    @staticmethod
    def yellow_str(string: str, before_text: str = "", after_text: str = "") -> str:
        return PR.color_str(Back.YELLOW, string, before_text, after_text)

    @staticmethod
    def yellow(string: str, before_text: str = "", after_text: str = "") -> None:
        PR.color(PR.yellow_str(string, before_text, after_text))

    @staticmethod
    def cyan(string: str, before_text: str = "", after_text: str = "") -> None:
        PR.color(PR.cyan_str(string, before_text, after_text))

    @staticmethod
    def cyan_str(string: str, before_text: str = "", after_text: str = "") -> str:
        return PR.color_str(Back.CYAN, string, before_text, after_text)

    @staticmethod
    def red(string: str, before_text: str = "", after_text: str = "") -> None:
        PR.color(PR.red_str(string, before_text, after_text))

    @staticmethod
    def red_str(string: str, before_text: str = "", after_text: str = "") -> str:
        return PR.color_str(Back.RED, string, before_text, after_text)

    @staticmethod
    def blue(string: str, before_text: str = "", after_text: str = "") -> None:
        PR.color(PR.blue_str(string, before_text, after_text))

    @staticmethod
    def blue_str(string: str, before_text: str = "", after_text: str = "") -> str:
        return PR.color_str(Back.BLUE, string, before_text, after_text)

    @staticmethod
    def bright(string: str, before_text: str = "", after_text: str = "") -> None:
        PR.color(PR.bright_str(string, before_text, after_text))

    @staticmethod
    def bright_str(string: str, before_text: str = "", after_text: str = "") -> str:
        return PR.color_str(Style.BRIGHT, string, before_text, after_text)
