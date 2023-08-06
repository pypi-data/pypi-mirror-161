# (c) Roxy Corp. 2020-
# Roxy AI Inspect-Server API
from __future__ import annotations

from .connection import Connection
from .com_definition import CommandCode
from .com_base import BaseCommand


class TerminateCommand(BaseCommand):
    _CODE = CommandCode.TERMINATE

    def __init__(self, connection: Connection = None, logging: bool = True):
        """ Terminate コマンド制御
        Args:
            connection:     通信対象のTCP接続
            logging:        送受信時のログ出力フラグ
        """
        super().__init__(connection=connection, logging=logging)
        # 要求データの設定
        self.data = b''
