import enum
from typing import List

from pih.collection import CommandLinkItem, CommandChainItem, FieldItem, FieldItemList, CommandItem, LogCommand, ParamItem, PasswordSettings

class DATA_EXTRACTOR:

    USER_NAME_FULL: str = "user_name_full"
    USER_NAME: str = "user_name"
    AS_IS: str = "as_is"


LOCAL_COMMAND_LIST_DICT: dict = {
    #name : [prefix, command, description]
    "Log":                               CommandItem("Log", "log.lnk", "Log a message", enable=False),
    "Log2":                              CommandItem("Log", "logClient.py", "Log a message", enable=False),
    #
    "Printer_list":                      CommandItem("Printer", "list.py", "Display all printers", cyclic=False),
    "Printer_report":                    CommandItem("Printer", "report.py", "Reports all printers", cyclic=False),
    "Printer_cleanQueue":                CommandItem("Printer", "printer_queue_clean_as_user.ps1", "Clear printer queue", cyclic=False, confirm_for_continue=False),
    #
    "AD_createTemplate":                 CommandItem("ActiveDirectory", "template/createTemplate.py", "Fill template", cyclic=False),
    "AD_findByLogin":                    CommandItem("ActiveDirectory", "findBy.py", "Find user by login", "samAccountName"),
    "AD_findByName":                     CommandItem("ActiveDirectory", "findBy.py", "Find user by name",  "name"),
    "AD_setUserStatus":                  CommandItem("ActiveDirectory", "setUserProperty.py", "Enable or disable user", "userStatus"),
    "AD_setUserPassword":                CommandItem("ActiveDirectory", "setUserProperty.py", "Set user password", "password"),
    "AD_setUserTelephone":               CommandItem("ActiveDirectory", "setUserProperty.py", "Set user telephone", "telephoneNumber"),
    "AD_findByLogin2":                   CommandItem("ActiveDirectory", "findByLogin.ps1", "Find user by login (PowerShell version)", enable=False),
    "AD_findBySurname2":                 CommandItem("ActiveDirectory", "findBySurname.ps1", "Find user by surname (PowerShell version)", enable=False),
    "AD_checker":                        CommandItem("ActiveDirectory", "checker.ps1", "Check by rules (PowerShell version)", enable=False),
    "AD_checkOrAddDeadUser":             CommandItem("ActiveDirectory", "checkOrAddDeadUser.ps1", "Find by login (PowerShell version)", enable=False),
    #
    "Orion_AD_getUserByTabNumber":       CommandChainItem("tab_number", "Description", [CommandLinkItem("Orion_findByTabNumber", DATA_EXTRACTOR.USER_NAME),
                                                                                        CommandLinkItem("AD_findByName", DATA_EXTRACTOR.AS_IS)], enable=False),
    #
    "Polibase_ping":                     CommandItem("Polibase", "ping.lnk", "Ping Polibase [message]", cyclic=False, enable=False),
    "Polibase_dbDump":                   CommandItem("Polibase", "dbDump.lnk", "Create Polibase database Dump", cyclic=False, enable=False),
    "Polibase_set_main_settings":        CommandItem("Polibase", "polibase_main_settings.vbs", "Set main settings for Polibase", cyclic=False, confirm_for_continue=False),
    "Polibase_set_test_settings":        CommandItem("Polibase", "polibase_test_settings.vbs", "Set test settings for Polibase", cyclic=False, confirm_for_continue=False),
    #
    "Orion_findByTabNumber":             CommandItem("Orion", "findByTabNumber.lnk", "Find orion person by tab number"),
    "Orion_findByName":                  CommandItem("Orion", "findByName.lnk", "Find orion person by name"),
    "Orion_removeByTabNumber":           CommandItem("Orion", "removeByTabNumber.lnk", "Find orion person by tab number and ask to remove"),
    "Orion_checker":                     CommandItem("Orion", "checker.lnk", "Check all orion person by rules", cyclic=False),
    "Orion_show_free_marks":             CommandItem("Orion", "showFreeMarks.lnk", "Show free marks", cyclic=False),
    "Orion_show_free_marks_group_statiscics":   CommandItem("Orion", "showFreeMarksGroupStatistics.lnk", "Show free marks group statistics", cyclic=False),
    "Orion_create_empty_person":                CommandItem("Orion", "createEmptyPerson.lnk", "Create empty orion person")

}


SITE: str = "pacifichosp.com"
MAIL_PREFIX: str = "mail"
SITE_FULL: str = f"https://{SITE}"
MAIL_ADDRESS: str = f"{MAIL_PREFIX}.{SITE}"


class AD_CONST:

    DOMAIN: str = "fmv"
    DN_MAIN_UNIT: str = f"OU=Users,OU=Unit,DC={DOMAIN},DC=lan"
    DN_DEADLIST_UNIT: str = f"OU=deadUsers,OU=Unit,DC={DOMAIN},DC=lan"
    USER_HOME_FOLDER: str = f"//{DOMAIN}/homes"


class NAME_POLICY_CONST:

    FULL_NAME_PARTS_LIST_MIN_LENGTH: int = 3
    FULL_NAME_PART_ITEM_MIN_LENGTH: int = 3


class FIELD_NAME_COLLECTION:

    NAME_FULL: str = "Name"
    GROUP_NAME: str = "GroupName"
    GROUP_ID: str = "GroupID"
    COMMENT: str = "Comment"
    TAB_NUMBER: str = "TabNumber"
    NAME: str = "Name"


class USER_PROPERTY:
    TELEPHONE: str = "telephoneNumber"
    DN: str = "distinguishedName"
    LOGIN: str = "samAccountName"
    DESCRIPTION: str = "description"
    PASSWORD: str = "password"
    USER_STATUS: str = "userStatus"
    NAME: str = "name"


class FIELD_COLLECTION:

    INDEX: FieldItem = FieldItem("__Index__", "Index", True)

    class ORION:

        GROUP_BASE: FieldItemList = FieldItemList(
            FieldItem(FIELD_NAME_COLLECTION.GROUP_NAME, "Access Name"),
            FieldItem(FIELD_NAME_COLLECTION.COMMENT, "Comment")
        )

        TAB_NUMBER_BASE: FieldItemList = FieldItemList(
            FieldItem(FIELD_NAME_COLLECTION.TAB_NUMBER, "Tab Number"),
            GROUP_BASE)

        TAB_NUMBER: FieldItemList = FieldItemList(
            TAB_NUMBER_BASE,
            FieldItem(FIELD_NAME_COLLECTION.NAME_FULL, "Full name"),
        ).position(FIELD_NAME_COLLECTION.NAME_FULL, 1)

        NAME: FieldItemList = FieldItemList(
            TAB_NUMBER,
            FieldItem("pID", "Person ID", False),
            FieldItem("mID", "Mark ID", False)
        ).visible(FIELD_NAME_COLLECTION.COMMENT, True)

        GROUP: FieldItemList = FieldItemList(
            GROUP_BASE,
            FieldItem("GroupID", "Group id", True)
        )

        GROUP_STATISTICS: FieldItemList = FieldItemList(
            GROUP,
            FieldItem("Count", "Count"),
        ).visible(FIELD_NAME_COLLECTION.COMMENT, False)

    class AD:

        MAIN: FieldItemList = FieldItemList(FieldItem(USER_PROPERTY.NAME, "Name"),
                                            FieldItem(
                                                USER_PROPERTY.LOGIN, "Login"),
                                            FieldItem(
                                                USER_PROPERTY.TELEPHONE, "Telephone"),
                                            FieldItem(
                                                USER_PROPERTY.DN, "Location"),
                                            FieldItem(
                                                USER_PROPERTY.DESCRIPTION, "Description"),
                                            FieldItem("userAccountControl", "Account Control"))

        CONTAINER: FieldItemList = FieldItemList(FieldItem(USER_PROPERTY.LOGIN, "Name"), FieldItem(
            USER_PROPERTY.DESCRIPTION, "Description")
        )


LINK_EXT = "lnk"


class EXECUTOR:

    PYTHON_EXECUTOR: str = "python"
    POWERSHELL_EXECUTOR: str = "powershell"
    VBS_EXECUTOR: str = "cscript"
    DEFAULT_EXECUTOR: str = PYTHON_EXECUTOR

    @staticmethod
    def get(ext: str) -> str:
        return {
            "": EXECUTOR.DEFAULT_EXECUTOR,
            "py": EXECUTOR.PYTHON_EXECUTOR,
            "ps1": EXECUTOR.POWERSHELL_EXECUTOR,
            "vbs": EXECUTOR.VBS_EXECUTOR
        }[ext]


class FACADE:

    COMMAND_SUFFIX: str = "Core"
    PATH: str = "//pih/facade/"


class RPC_CONST:

    @staticmethod
    def PORT() -> int:
        return 50051


class HOST_COLLECTION:

    class PRINTER_SERVER:

        @staticmethod
        def HOST_NAME() -> str:
            return "fmvdc1.fmv.lan"

    class ORION:

        @staticmethod
        def HOST_NAME() -> str:
            return "orion"

    class AD:

        @staticmethod
        def HOST_NAME() -> str:
            return "fmvdc2.fmv.lan"


class PASSWORD_GENERATION_ORDER:
    
        SPECIAL_CHARACTER: str = "s"
        LOWERCASE_ALPHABET: str = "a"
        UPPERCASE_ALPHABET: str = "A"
        DIGIT: str = "d"
        DEFAULT_ORDER_LIST: List[str] = [SPECIAL_CHARACTER,
                                        LOWERCASE_ALPHABET, UPPERCASE_ALPHABET, DIGIT]


class PASSWORD:

   
    class SETTINGS:

        NORMAL: PasswordSettings = PasswordSettings(
            8, "!@#", PASSWORD_GENERATION_ORDER.DEFAULT_ORDER_LIST, 3, 3, 1, 1, False)
        STRONG: PasswordSettings = PasswordSettings(
            10, "#%+\-!=@()_",  PASSWORD_GENERATION_ORDER.DEFAULT_ORDER_LIST, 3, 3, 2, 2, True)
        DEFAULT: PasswordSettings = NORMAL
        PC: PasswordSettings = NORMAL
        MAIL: PasswordSettings = NORMAL
        

class LogType(enum.Enum):
    MESSAGE: str = "message"
    COMMAND: str = "command"
    DEFAULT: str = MESSAGE


class LogChannel(enum.Enum):
    BACKUP: str = "backup"
    NOTIFICATION: str = "notification"
    DEFAULT: str = NOTIFICATION


#: dict[LogChannel, str]
# config files for telegram are located in folder named "telegram_send_config" in api location
LOG_CHANNEL_DICT = {
    LogChannel.BACKUP: "backup.conf",
    LogChannel.NOTIFICATION: "notification.conf"
}


class LogLevel(enum.Enum):
    NORMAL: str = "normal"
    ERROR: str = "error"
    EVENT: str = "normal"
    DEBUG: str = "debug"
    DEFAULT: str = NORMAL


class LogCommandName(enum.Enum):
    DEBUG: str = "debug"
    LOG_IN_FACADE: str = "facade:log_in"
    #
    POLIBASE_DB_BACKUP_START: str = "polibase:db_backup_start"
    POLIBASE_DB_BACKUP_COMPLETE: str = "polibase:db_backup_complete"
    #


#: dict[LogCommandName, LogCommand]
LOG_COMMAND_LIST = {
    LogCommandName.DEBUG: LogCommand("It is a debug command", LogChannel.NOTIFICATION, LogLevel.DEBUG),
    #
    LogCommandName.LOG_IN_FACADE: LogCommand(
        "User {name} ({computer_name}) log in", LogChannel.NOTIFICATION, LogLevel.NORMAL, (ParamItem("name", "Name of user"), ParamItem("computer_name", "Name of computer"))),
    #
    LogCommandName.POLIBASE_DB_BACKUP_START: LogCommand(
        "Start Polibase DataBase Dump backup",  LogChannel.BACKUP, LogLevel.NORMAL),
    LogCommandName.POLIBASE_DB_BACKUP_COMPLETE: LogCommand(
        "Complete Polibase DataBase Dump backup",  LogChannel.BACKUP, LogLevel.NORMAL)
    #
}
