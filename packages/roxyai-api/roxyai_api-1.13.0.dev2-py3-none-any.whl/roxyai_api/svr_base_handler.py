# (c) Roxy Corp. 2020-
# Roxy AI Coordinator
from __future__ import annotations
from typing import Callable, Any
from logging import getLogger
from time import perf_counter_ns

from .com_definition import CommandStatus

log = getLogger(__name__)


class ServerBaseHandler():
    code = None
    name = None

    # コマンド送受信ログ出力用
    last_command = None
    repeat_count = 0

    def __init__(
        self,
        reply_func: Callable[[CommandStatus, bytes, bytes], None],
        context: Any = None,
    ):
        """ 基底ハンドラクラス
        Args:
            reply_func:         応答処理関数
            context:            コマンド処理に必要な情報
        """
        # # ログ出力に手続き名を設定
        self._status = CommandStatus.STS_REQUEST
        self._reply_func = reply_func
        self.__start_time = None
        self.__end_time = None
        self._context = context

    def proceed(self):
        """ コマンドの処理呼び出し
        """
        try:
            # コマンド処理開始時刻の記録
            self.__start_time = perf_counter_ns()
            self.__end_time = None

            # 具象クラスの処理を呼び出し
            self.status = self.run()

            if self._status.is_ack:
                # 正常応答ならば具象クラスのデータ構築を呼び出し
                send_data = self.encode()
            else:
                send_data = b''

            # コマンド処理完了時間の記録
            self.__end_time = perf_counter_ns()

        except Exception:
            # コマンド処理中に例外が発生(TBD)
            self.status = CommandStatus.ERR_UNKNOWN_EXCEPTION
            send_data = b''
            log.exception(
                f"{self.__class__.__name__}: "
                f"Exception on command {self.code:02X}x procedure"
            )
        finally:
            # 応答処理
            self._reply_func(self._status, send_data)

        log.debug(f'command {self.__class__.__name__} replies {repr(self._status)}\n')

    def decode(self, payload: bytes):
        """ コマンド要求の受信データ解釈
        Note:
            要求パラメータのデコードを各具象クラスでオーバーライドする
        """
        # 処理するパラメータが無い場合は何も実施しない。
        pass

    def run(self):
        """ コマンドの処理実行
        Note:
            各具象クラスでオーバーライドする
        """
        raise NotImplementedError

    def encode(self):
        """ コマンド応答の送信データ構築
        Note:
            応答パラメータのデコードを各具象クラスでオーバーライドする
        """
        return b''

    @property
    def process_time(self) -> float:
        """ ハンドラの処理時間 [ms]
        """
        time_ms = None
        if self.__end_time and self.__start_time:
            time_ms = (self.__end_time - self.__start_time) / 1000000
        return time_ms

    def com_info(self):
        """ コマンドの情報文字列取得
        Note:
            各ハンドラの __str__ での利用を想定。
        """
        string = f"0x{self.code:02X}({self.code:d})"
        if self._status.is_reply:
            # コマンド応答時
            string += (
                f' [{str(self._status)}]'
            )
            if self._status.is_ack:
                # 正常応答時
                string += f'({self.process_time:,.2f} ms)'

        return string

    @property
    def status(self) -> CommandStatus:
        return CommandStatus(self._status)

    @status.setter
    def status(self, val: int):
        """ コマンドの送信／返信状態の設定
        """
        self._status = CommandStatus(val)
