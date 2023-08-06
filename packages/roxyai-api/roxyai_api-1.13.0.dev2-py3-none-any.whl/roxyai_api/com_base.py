# (c) Roxy Corp. 2020-
# Roxy AI Inspect-Server API
from __future__ import annotations
import time
from struct import pack, unpack
from io import BytesIO

from .connection import Connection
from .com_definition import (
    SIGN_CODE,
    HEADER_SIZE,
    CommandStatus,
    CommandCode,
)

from logging import getLogger
log = getLogger(__name__)


class BaseCommand():
    # デフォルトの検査サーバの定義
    HOST = "127.0.0.1"
    """ デフォルトの接続先IPアドレス """
    PORT = 6945
    """ デフォルトの接続先ポート番号 """
    _REPLAY_NONE = False

    _CODE = None
    _connection = None
    _last_connection = Connection(HOST, PORT)
    data = b""
    _logging = True

    def __init__(self, connection: Connection = None, logging: bool = True):
        """ 基底コマンドクラス
        Args:
            connection:     通信対象のTCP接続
            logging:        送受信時のログ出力フラグ
        """
        self._connection = connection or self._connection or BaseCommand._last_connection
        if connection:
            # 接続設定をクラス変数に記録
            BaseCommand._last_connection = connection

        self.status = CommandStatus.NONE
        self.__send_time = None
        self.__recv_time = None
        self.__rest_size = None
        self._logging = logging

    def send(self, extension: bytes = b'', timeout: float = None):
        """ コマンドの送信

        Args:
            extension
                (bytes, option):    拡張送信データ
            timeout
                (None, default):    None はタイムアウト無し
                (float, option):    タイムアウト時間[sec]

        Raises:
            送信タイムアウト（socket.timeout）を含む通信例外を送出

        Note:
            extension はコマンドの最後に、メモリコピーを伴わずに送信する
            拡張データを指定できます。
        """
        data = self.data
        sock = self._connection.sock

        code = self._CODE
        size = len(data) + len(extension)
        status = CommandStatus.STS_REQUEST

        buffer = pack(f"< H L B B {len(data)}s", SIGN_CODE, size, code, status, data)

        if self._logging:
            log.debug(f"Send [{size:3,d} bytes]: {self}")

        self.__send_time = time.time()
        self.__recv_time = None
        sock.settimeout(timeout)
        sock.sendall(buffer)
        if extension:
            # 残りのタイムアウト時間を再計算してブロッキングモードの範囲で設定
            if timeout is not None:
                timeout = max(0.000001, timeout - (time.time() - self.__send_time))
            sock.settimeout(timeout)
            # 拡張データの送信
            sock.sendall(extension)

    def recv(self, recv_size: int = None, timeout: float = None):
        """ コマンドの受信

        Args:
            recv_size
                (None, default):    応答コマンド全体を受信
                (int, option):      指定されたデータBytesまで受信
            timeout
                (None, default):    None はタイムアウト無し
                (float, option):    タイムアウト時間[sec]
        Raises:
            送信タイムアウト（socket.timeout）を含む通信例外を送出

        Note:
            下記の属性を設定
            status (int):           返信コマンドステータス
            code (int):             返信コマンド番号
            rest_size (int):        フレームの未受信データサイズ
        """
        sock = self._connection.sock
        # タイムアウト設定
        pre_time = time.time()
        sock.settimeout(timeout)
        # ヘッダの読み込み
        buf = sock.recv(HEADER_SIZE)
        self.__recv_time = time.time()
        if len(buf) == 0:
            # サーバによる切断
            raise ConnectionResetError

        if len(buf) < HEADER_SIZE:
            # ゴミ受信のため破棄
            self.status = CommandStatus.ERR_INVALID_DATA_SIZE
            dat = ' '.join(f'{b:02x}' for b in buf)
            raise RuntimeError(f"{self} Receive invalid header size data: {len(buf)} bytes\nData: {dat}  {buf}")

        sign, size, code, status = unpack("< H L B B", buf[0:HEADER_SIZE])
        if sign != SIGN_CODE:
            # パケット種別チェック
            self.status = CommandStatus.ERR_INVALID_SIGNATURE
            dat = f'sign: {sign:04x}, size: {size:,d}, code: {code:02x}, status: {status:02x}'
            raise RuntimeError(f"{self} Receive invalid signe code: 0x{sign:04x}\n{dat}")

        # 受信ヘッダデータの検証
        if code and (code != self._CODE):
            self.status = CommandStatus.ERR_INVALID_COMMAND
            dat = f'sign: {sign:04x}, size: {size:,d}, code: {code:02x}, status: {status:02x}'
            raise RuntimeError(f"{self} Received command code:0x{code:02X} is mismatched 0x{self._CODE:02X}\n{dat}")

        try:
            self.status = status
        except ValueError:
            self.status = CommandStatus.ERR_UNKNOWN_EXCEPTION
            dat = f'sign: {sign:04x}, size: {size:,}, code: {code:02x}, status: {status:02x}'
            raise RuntimeError(f"{self} Receive invalid status: 0x{status:02x}\n{dat}")

        if recv_size and (recv_size < size):
            # フレームサイズが指定受信サイズ以上の場合は途中までを受信
            self.__rest_size = size - recv_size
            size = recv_size
            log.warning(f'{self} Received larger size packet: {size:,} > expectation: {recv_size:,} bytes')
        else:
            self.__rest_size = 0

        # コマンドデータの読み込み
        reply_data = b''
        if size > 0:
            # データ受信開始の時間を記録
            rcv_dat_start = time.time()
            with BytesIO(b'\0' * size) as buffer:
                while buffer.tell() < size:
                    # 残りのタイムアウト時間を再計算してブロッキングモードの範囲で設定
                    if timeout is not None:
                        now = time.time()
                        timeout = max(0.000001, timeout - (now - pre_time))
                        pre_time = now
                    sock.settimeout(timeout)

                    fragment = sock.recv(size - buffer.tell())

                    # データ受信開始の時間を記録
                    rcv_dat_time = (time.time() - rcv_dat_start) * 1000
                    received_size = buffer.tell() + len(fragment)
                    if rcv_dat_time >= 500:
                        # 500ms 以上掛かっている場合は警告ログを出力
                        log.warning(
                            f'{self}\n Long receiving time: {rcv_dat_time:,} ms ({received_size:,} / {size:,} bytes) '
                        )
                    if received_size > size:
                        # バッファで最初に確保したサイズ以上のデータを受信した場合
                        log.warning(
                            f'{self}\n Received larger size data: {received_size:,} / {size:,} bytes'
                        )

                    if len(fragment) == 0:
                        # サーバによる切断
                        raise ConnectionResetError
                    buffer.write(fragment)
                reply_data = buffer.getvalue()

            # 受信コマンドデータのデコード
            try:
                self._decode_reply(reply_data)
            except Exception:
                self.status = CommandStatus.ERR_FIALED_PARSE_DATA
                log.exception('received invalid data')

        if self._logging:
            log.debug(f"Recv [{size:3,d} bytes]: {self}")

        if self._status.is_error_reply:
            reply_data = b''

    def _decode_reply(self, reply: bytes):
        if reply:
            # データが存在する場合は各コマンドでオーバライドする
            raise NotImplementedError

    def run(self, timeout: float = None):
        """ コマンドの送受信
        Args:
            timeout
                (None, default):    None はタイムアウト無し
                (float, option):    タイムアウト時間[sec]
        Raises:
            送信タイムアウト（socket.timeout）を含む通信例外を送出
        """
        pre_time = time.time()
        # コマンドの送信＆受信
        self.send(timeout=timeout)

        if self._REPLAY_NONE:
            # 応答不要コマンドは受信完了を設定する
            self.__recv_time = time.time()
            self.status = CommandStatus.STS_REPLY_ACK
            return b''

        if timeout is not None:
            # 残りのタイムアウト時間を再計算してブロッキングモードの範囲で設定
            now = time.time()
            timeout = max(0.000001, timeout - (now - pre_time))
            pre_time = now
        self.recv(timeout=timeout)

    @property
    def is_received(self) -> bool:
        """ 応答を受信しているかのフラグ
        """
        return (self.__recv_time is not None)

    @property
    def is_received_ack(self) -> bool:
        """ 正常応答を受信しているかのフラグ
        """
        return (self._status and self._status.is_ack)

    @property
    def process_time(self) -> float:
        """ コマンドの要求～応答の処理時間 [ms]
        """
        proc_time = None
        if self.is_received:
            proc_time = (self.__recv_time - self.__send_time) * 1000
            proc_time = round(proc_time, 3)
        return proc_time

    def __str__(self) -> str:
        string = f"{str(self.code)} "
        if not self.is_received:
            string += "<REQUEST>"
        else:
            string += "<REPLY"
            if self._status.is_error_reply:
                string += f"-{str(self.status)}"
            string += ">"
            if self.is_received:
                string += f" ({self.process_time} ms)"
        return string

    # 読み出し専用変数のアクセス定義

    @property
    def code(self) -> CommandCode:
        """ コマンドのコード番号
        """
        return CommandCode(self._CODE)

    @property
    def last_connection(self) -> Connection:
        """ 前回接続に利用した Connection
        """
        return self._last_connection

    @property
    def connection(self) -> Connection:
        """ 接続中の Connection
        """
        return self._connection

    @property
    def status(self) -> CommandStatus:
        """ コマンドの送信／返信状態
        """
        return CommandStatus(self._status)

    @status.setter
    def status(self, val: int):
        """ コマンドの送信／返信状態の設定
        """
        self._status = CommandStatus(val)

    @property
    def rest_size(self) -> int:
        """ 応答コマンドの未受信データの残りサイズ
        """
        self.__rest_size
