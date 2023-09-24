import datetime

from abc import ABCMeta, abstractmethod
import re
from typing import Union, List

from checkuser.data.executor import CommandExecutor


class Driver(metaclass=ABCMeta):
    @abstractmethod
    def get_id(self, username: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_expiration_date(self, username: str) -> Union[datetime.datetime, None]:
        raise NotImplementedError

    @abstractmethod
    def get_connection_limit(self, username: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_users(self) -> List[str]:
        raise NotImplementedError


class FormatDate(metaclass=ABCMeta):
    @abstractmethod
    def format(self, date: str) -> datetime.datetime:
        raise NotImplementedError


class FormatDateUS(FormatDate):
    def format(self, date: str) -> datetime.datetime:
        return datetime.datetime.strptime(date, '%b %d, %Y')


class FormatDateBR(FormatDate):
    def format(self, date: str) -> datetime.datetime:
        return datetime.datetime.strptime(date, '%b %d, %Y')


class DriverImpl(Driver):
    def __init__(self, executor: CommandExecutor, format_date: FormatDate):
        self.executor = executor
        self.format_date = format_date

    def get_id(self, username: str) -> int:
        command = 'id -u {}'.format(username)
        return int(self.executor.execute(command))

    def get_expiration_date(self, username: str) -> Union[datetime.datetime, None]:
        try:
            command = 'chage -l {}'.format(username)
            output = self.executor.execute(command)
            search = re.search(r'Account expires\s*:\s*(.*)', output)
            expiration_date = self.format_date.format(search.group(1)) if search else None
            return expiration_date
        except Exception:
            return None

    def get_connection_limit(self, username: str) -> int:
        try:
            archive = '/root/usuarios.db'
            data = open(archive).read()
            search = re.search(r'{}\s+(\d+)'.format(username), data)
            return int(search.group(1)) if search else 0
        except FileNotFoundError:
            return 0

    def get_users(self) -> List[str]:
        command = 'cat /etc/passwd'
        output = self.executor.execute(command)
        return re.findall(r'^([^:]+):', output, re.MULTILINE)
