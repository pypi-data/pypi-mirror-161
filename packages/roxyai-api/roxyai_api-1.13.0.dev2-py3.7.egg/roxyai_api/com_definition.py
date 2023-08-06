# (c) Roxy Corp. 2020-, CONFIDENTIAL
# Roxy AI Inspect-Server communication definition
from __future__ import annotations
from typing import NamedTuple, Union
from enum import IntEnum

# フレームのヘッダ定義
SIGN_CODE = 0x6941
HEADER_SIZE = 8


class CommandStatus(IntEnum):
    """ コマンドステータスの列挙クラス
    """
    NONE = -1
    STS_REQUEST = 0x00
    STS_REPLY_ACK = 0x01
    ERR_INVALID_SIGNATURE = 0x0B
    ERR_FIALED_PARSE_DATA = 0x0C
    ERR_INVALID_DATA_SIZE = 0x0D
    ERR_UNKNOWN_EXCEPTION = 0x0E
    ERR_INVALID_COMMAND = 0x0F
    ERR_NOT_FOUND_PRODUCT = 0x11
    ERR_NOT_FOUND_MODEL = 0x12
    ERR_DENIED_PRODUCT = 0x13
    ERR_FAILED_LOAD_CONFIG = 0x14
    ERR_FAILED_INITIALIZE = 0x15
    ERR_FAILED_LOGGING = 0x16

    ERR_INVALID_MODEL_ID = 0x21
    ERR_INVALID_IMG_FORMAT = 0x22
    ERR_INVALID_IMG_DATA = 0x23
    ERR_INVALID_JSON_DATA = 0x24
    ERR_UNINITIALIZED = 0x25
    ERR_OVERLAP_INSPECT_ID = 0x26
    ERR_FAILED_INSPECT = 0x27
    ERR_NOT_FOUND_PROB = 0x28
    ERR_NOT_FOUND_IMAGE = 0x29

    ERR_NOT_FOUND_SERVER = 0x31
    ERR_NOT_FOUND_CAMERA = 0x32
    ERR_NOT_FOUNT_MONITOR = 0x33
    ERR_NOT_DEFINED_PROC = 0x34
    ERR_INVALID_PRODUCT_CFG = 0x35
    ERR_INVALID_SHOT_NUMBER = 0x36
    ERR_DISCONNECTED_SERVER = 0x37
    ERR_FAILED_INIT_SERVER = 0x39

    ERR_FAILED_START_CAMERA = 0x41
    ERR_NOT_READY_CAMERA = 0x42
    ERR_FAILED_TRIGGER = 0x43
    ERR_FAILED_SETUP_CAMERA = 0x44
    ERR_FAILED_STOP_CAMERA = 0x45

    ERR_CDNT_NOT_ACTIVATED = 0x50

    ERR_INVALID_TARGET_WORK = 0x61
    ERR_RESULT_NOT_FOUND = 0x62

    @property
    def is_ack(self) -> bool:
        """ コマンド状態が正常応答か
        """
        return (self.value == self.STS_REPLY_ACK)

    @property
    def is_reply(self) -> bool:
        """ コマンド状態が応答コマンドか
        """
        return (self.value not in (
            self.STS_REQUEST,
            self.NONE,
        ))

    @property
    def is_error_reply(self) -> bool:
        """ コマンド状態がエラーの応答コマンドか
        """
        return (self.value not in (
            self.NONE,
            self.STS_REQUEST,
            self.STS_REPLY_ACK
        ))

    def __str__(self) -> str:
        message = _STATUS_DESCRIPTIONS.get(self.value, 'Unknown Status')
        return f"{message} (0x{self.value:02X})"


_STATUS_DESCRIPTIONS = {
    CommandStatus.NONE: '<<None>>',
    CommandStatus.STS_REQUEST: 'Request',
    CommandStatus.STS_REPLY_ACK: 'ACK',
    CommandStatus.ERR_INVALID_SIGNATURE: 'ERR: Invalid command signature',
    CommandStatus.ERR_FIALED_PARSE_DATA: 'ERR: Failed to parse data content',
    CommandStatus.ERR_INVALID_DATA_SIZE: 'ERR: Invalid command data size',
    CommandStatus.ERR_UNKNOWN_EXCEPTION: 'ERR: Unknown exception',
    CommandStatus.ERR_INVALID_COMMAND: 'ERR: Unknown command',
    CommandStatus.ERR_NOT_FOUND_PRODUCT: 'ERR: Cannot find product folder',
    CommandStatus.ERR_NOT_FOUND_MODEL: 'ERR: Cannot find model data',
    CommandStatus.ERR_DENIED_PRODUCT: 'ERR: Denied open additional product',
    CommandStatus.ERR_FAILED_LOAD_CONFIG: 'ERR: Failed to load config file',
    CommandStatus.ERR_FAILED_INITIALIZE: 'ERR: Failed to initialize model',
    CommandStatus.ERR_FAILED_LOGGING: 'ERR: Failed to output inspection log',

    CommandStatus.ERR_INVALID_MODEL_ID: 'ERR: Invalid model id',
    CommandStatus.ERR_INVALID_IMG_FORMAT: 'ERR: Invalid image format id',
    CommandStatus.ERR_INVALID_IMG_DATA: 'ERR: Invalid image data',
    CommandStatus.ERR_INVALID_JSON_DATA: 'ERR: Invalid JSON data',
    CommandStatus.ERR_UNINITIALIZED: 'ERR: Uninitialized',
    CommandStatus.ERR_OVERLAP_INSPECT_ID: 'ERR: Overlapped inspect id',
    CommandStatus.ERR_FAILED_INSPECT: 'ERR: Failed to inspection',
    CommandStatus.ERR_NOT_FOUND_PROB: 'ERR: Cannot find probabilities list',
    CommandStatus.ERR_NOT_FOUND_IMAGE: 'ERR: Cannot find image data',

    CommandStatus.ERR_NOT_FOUND_SERVER: 'ERR: Cannot find Inspect-Sever',
    CommandStatus.ERR_NOT_FOUND_CAMERA: 'ERR: Cannot find camera device',
    CommandStatus.ERR_NOT_FOUNT_MONITOR: 'ERR: Cannot find Monitor',
    CommandStatus.ERR_NOT_DEFINED_PROC: 'ERR: Not defined inspect procedure',
    CommandStatus.ERR_INVALID_PRODUCT_CFG: 'ERR: Inivalid product config file',
    CommandStatus.ERR_INVALID_SHOT_NUMBER: 'ERR: Inivalid shot number',
    CommandStatus.ERR_DISCONNECTED_SERVER: 'ERR: Server is disconnected',
    CommandStatus.ERR_FAILED_INIT_SERVER: 'ERR: Failed to initialize server',

    CommandStatus.ERR_FAILED_START_CAMERA: 'ERR: Failed to start camera',
    CommandStatus.ERR_NOT_READY_CAMERA: 'ERR: Camera is not ready',
    CommandStatus.ERR_FAILED_TRIGGER: 'ERR: Software trigger failed',
    CommandStatus.ERR_FAILED_SETUP_CAMERA: 'ERR: Failed to setup camera',
    CommandStatus.ERR_FAILED_STOP_CAMERA: 'ERR: Failed to stop camera',

    CommandStatus.ERR_CDNT_NOT_ACTIVATED: 'ERR: Coordinator is not activated',

    CommandStatus.ERR_RESULT_NOT_FOUND: 'ERR: Cannot find results',
    CommandStatus.ERR_INVALID_TARGET_WORK: 'ERR: Invalid target work',
}


# コマンドの定義
class CommandCode(IntEnum):
    """ コマンド番号の列挙クラス
    """
    # コマンドの定義
    ECHO = 0x10
    INITIALIZE = 0x11
    TERMINATE = 0x12
    INSPECT = 0x13
    GET_PROBABILITIES = 0x1A
    GET_IMAGE = 0x1B

    def __str__(self) -> str:
        message = _COM_NAME_LIST.get(self.value, 'Unknown Command Code')
        return f"{message}(0x{self.value:02X})"


_COM_NAME_LIST = {
    CommandCode.ECHO: 'Echo',
    CommandCode.INITIALIZE: 'Initialize',
    CommandCode.TERMINATE: 'Terminate',
    CommandCode.INSPECT: 'Inspect',
    CommandCode.GET_PROBABILITIES: 'GetProbabilities',
    CommandCode.GET_IMAGE: 'GetImage',
}


class Judgment(IntEnum):
    """ 判定結果の列挙クラス
    """
    NONE = 0x00         # 未判定
    OK = 0x1
    NOK = 0x2
    GRAY = 0x3
    UNK = 0x3           # deprecated
    FAILED = 0xFF

    def __and__(self, other) -> Judgment:
        """ 論理演算 OK < GRAY < NOK < FAILED の順で優先
        """
        priority = (self.FAILED, self.NOK, self.GRAY, self.OK, self.NONE)
        try:
            hi = min(priority.index(self), priority.index(other))
        except ValueError:
            return self.NONE
        return priority[hi]

    def __or__(self, other) -> Judgment:
        """ 論理演算 OK > GRAY > NOK > FAILED の順で優先
        """
        priority = (self.NONE, self.FAILED, self.NOK, self.GRAY, self.OK)
        try:
            hi = max(priority.index(self), priority.index(other))
        except ValueError:
            return self.NONE
        return priority[hi]

    def __str__(self) -> str:
        return f"{self.name:3s}(0x{self.value:02X})"


class JudgmentCount(NamedTuple):
    """ 判定結果のカウントクラス
    """
    ok: int = 0
    nok: int = 0
    gray: int = 0
    failed: int = 0

    @property
    def total(self) -> int:
        """ カウントの合計
        """
        return sum(self)


class JudgmentCounter():
    """ 判定結果のカウンタークラス
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.ok = 0
        self.nok = 0
        self.gray = 0
        self.failed = 0

    def set(self, judge: Judgment):
        if judge == Judgment.OK:
            self.ok += 1
        elif judge == Judgment.NOK:
            self.nok += 1
        elif judge == Judgment.GRAY:
            self.gray += 1
        elif judge == Judgment.FAILED:
            self.failed += 1

    def get_count(self) -> JudgmentCount:
        return JudgmentCount(self.ok, self.nok, self.gray, self.failed)

    def __str__(self) -> str:
        output = f'OK: {self.ok:,d}, NOK: {self.nok:,d}, GRAY: {self.gray:,d}'
        if self.failed:
            output += f', FAILED: {self.failed}'
        return output


class ProbabilityType(IntEnum):
    """ エリア確信度の型
    """
    SIMPLE = 0x01
    LABELED = 0x02

    def __str__(self) -> str:
        return f"{self.name:s}(0x{self.value:02X})"


class Probability():
    """ 判定結果の確信度クラス
    """
    def __init__(self, x1: int, y1: int, x2: int, y2: int, typ: int, prob: float):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.typ = typ
        self.prob = prob
        self.judge = Judgment(typ)

    def __str__(self) -> str:
        return (
            f'{self.judge.name:3s} '
            f'({self.x1:4d}, {self.y1:4d})-({self.x2:4d}, {self.y2:4d}) '
            f'{self.prob:6f}'
        )


class LabeledProbability(Probability):
    """ 不良種別情報付きの判定結果の確信度クラス
    """
    def __init__(self, x1, y1, x2, y2, typ, label, prob):
        super().__init__(x1, y1, x2, y2, typ, prob)
        self.label = label

    def __str__(self) -> str:
        return super().__str__() + f', label={self.label}'


class InspectResult():
    def __init__(
        self,
        model_name: str,
        group_name: str,
        judge: Judgment,
        prob_list: list[Union[Probability, LabeledProbability]],
        product_name: str = '',
    ):
        """ AI検査結果詳細
        """
        self.product_name = product_name
        self.model_name = model_name
        self.group_name = group_name
        self.judge = judge
        self.prob_list = prob_list

    @staticmethod
    def merge(all_results: list) -> InspectResult:
        """ AI検査結果詳細の統合
        Note:
            記録用に複数の検査結果をまとめる
        """
        model_name = '+'.join(sorted(list(set(r.model_name for r in all_results))))
        group_name = '+'.join(sorted(list(set(r.group_name for r in all_results))))
        judge = Judgment.NONE
        prob_list = []
        for result in all_results:
            judge &= result.judge
            prob_list.extend(result.prob_list)
        merged = InspectResult(
            model_name=model_name,
            group_name=group_name,
            judge=judge,
            prob_list=prob_list
        )

        return merged

    @property
    def model_group(self) -> str:
        """ モデル名（グループ名）の取得
        Note:
            グループがデフォルトの場合は表示しない
        """
        if self.group_name:
            return f'{self.model_name}({self.group_name})'
        else:
            return self.model_name
