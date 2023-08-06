# (c) Roxy Corp. 2020-
# Roxy AI Inspect/Analyze-Server API
from __future__ import annotations
from .connection import Connection
from .com_definition import CommandCode
from .com_base import BaseCommand


class EchoCommand(BaseCommand):
    _CODE = CommandCode.ECHO

    def __init__(self, data: bytes, connection: Connection = None, logging: bool = True):
        """ ECHO コマンド制御

        Args:
            data:           送受信データ
            connection:     通信対象のTCP接続
            logging:        送受信時のログ出力フラグ
        """
        super().__init__(connection=connection, logging=logging)
        # 要求データの設定
        self.data = data

    def _decode_reply(self, reply: bytes):
        """ Inspect コマンドの応答内容確認

        Args:
            reply (bytes):      受信応答データ（ヘッダ以外）
        """
        # 応答データの妥当性チェック
        if self.data != reply:
            raise RuntimeError('mismatched echo reply data')

    def __str__(self) -> str:
        string = (
            f'{super().__str__()} '
            f'<-> Data: {self.data[:min(len(self.data), 128)]} '
            f'{len(self.data):,} '
        )
        return string
