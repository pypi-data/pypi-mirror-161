# (c) Roxy Corp. 2020-
# Roxy AI Coordinator
from __future__ import annotations
from typing import Any
from struct import pack, unpack
from time import perf_counter_ns
from io import BytesIO
from socket import socket
from logging import getLogger

from .com_definition import (
    SIGN_CODE,
    HEADER_SIZE,
    CommandStatus,
)
from .svr_base_handler import ServerBaseHandler

log = getLogger(__name__)


class ServerCommandManager:

    def __init__(
        self,
        sock: socket,
        handlers: dict[int, ServerBaseHandler],
        context: Any = None,
    ):
        """ 逐次コマンド処理クラス
        Args:
            connection:     接続管理クラス
            handlers:       ハンドラ辞書
            context:        ハンドラに渡すオプション情報
        """
        self._socket = sock
        self.handlers = handlers
        self.context = context

        self._cur_code = None
        self._cur_handler = None
        self._last_handler = None
        self._recv_data = None
        self._repeat_count = 0

        self.__recv_time = None
        self.__send_time = None

    def start(self):
        """ 処理開始
        Note:
            この関数は複数コマンドの並列処理には対応していない
        """
        while True:
            self._recv()
            self._dispatch()

    def _recv(self):
        """ コマンドの受信
        Note:
            下記のクラス属性を設定
            code (int)      受信要求コマンド番号
        """
        # 受信開始時刻の記録
        self.__recv_time = perf_counter_ns()
        self.__send_time = None

        # ヘッダの読み込み
        buf = self._socket.recv(HEADER_SIZE)
        if len(buf) == 0:
            # クライアントによる切断
            raise ConnectionResetError

        if len(buf) < HEADER_SIZE:
            # ゴミ受信のため破棄
            log.warning(f"Receive invalid header size data: {len(buf)} bytes")

        sign, size, code, status = unpack("< H L B B", buf[0:HEADER_SIZE])
        if sign != SIGN_CODE:
            # パケット種別チェック
            raise RuntimeWarning(f"Receive invalid signe code: 0x{sign:04x}")

        if status != CommandStatus.STS_REQUEST:
            # 不正なステータス受信
            raise RuntimeWarning(f"Receive invalid status: 0x{status:02x}")

        self._cur_code = code

        # コマンドデータの読み込み
        with BytesIO(b"\0" * size) as buffer:
            while buffer.tell() < size:
                fragment = self._socket.recv(size - buffer.tell())
                if len(fragment) == 0:
                    # クライアントによる切断
                    raise ConnectionResetError
                buffer.write(fragment)
            self._recv_data = buffer.getvalue()

        return

    def _dispatch(self):
        """ コマンドによってリクエスト処理を振り分ける
        """
        status = None
        try:
            code = self._cur_code
            hdl_cls = self.handlers.get(code)
            if hdl_cls:
                # コマンド処理ハンドラのインスタンス生成
                self._cur_handler: ServerBaseHandler = hdl_cls(
                    self._reply, self.context
                )
                # 各コマンドハンドラのデコード呼び出し
                self._cur_handler.decode(self._recv_data)
                log.debug(f">> Dispatch command {self._cur_handler}")
                # ハンドラ処理の実行
                self._cur_handler.proceed()
            else:
                log.warning(f">> Unkonw command ({code:02X}x)")
                status = CommandStatus.ERR_INVALID_COMMAND

        except Exception:
            # コマンド処理で未処理の例外発生の場合はエラー返信
            status = CommandStatus.ERR_UNKNOWN_EXCEPTION
            log.exception(f"Faild command {code:02X}x")

        if status is not None:
            # エラーで即時返信の場合
            self._reply(CommandStatus(status))

    def _reply(self, status: CommandStatus, data: bytes = b"", extension: bytes = b""):
        """ 応答コマンドの送信
        Args:
            status (CommandStatus): 応答ステータス
            data (bytes):           応答コマンドデータ
            extension (bytes):      応答コマンド追加送信データ
        """
        code = self._cur_code
        handler = self._cur_handler

        # 返信ステータスの確認
        if status.is_error_reply:
            # エラー応答はデータ無し
            data = b""
            extension = b""
        size = len(data) + len(extension)

        # 応答コマンドのデータ生成
        buffer = pack(f"< H L B B {len(data)}s", SIGN_CODE, size, code, status, data)

        self._socket.sendall(buffer)
        if extension:
            self._socket.sendall(extension)

        # 送信完了時間の記録
        self.__send_time = perf_counter_ns()

        # コマンド完了のログ出力
        last_handler = self._last_handler
        if (code, status) == last_handler:
            log.debug(f"<< Complete command {handler}")
            self._repeat_count += 1
        else:
            if self._repeat_count > 0:
                # 連続で同じコマンドは出力しない
                log.info(
                    f"<< Complete command {last_handler} " f"x {self._repeat_count} times"
                )
            log.info(f"<< Complete command {handler}")
            self._last_handler = handler
            self._repeat_count = 0

    @property
    def process_time(self) -> float:
        """ コマンドの要求～応答の処理時間 [ms]
        """
        time_ms = None
        if self.__send_time and self.__recv_time:
            time_ms = (self.__send_time - self.__recv_time) / 1000000
        return time_ms
