# (c) Roxy Corp. 2020-
# Roxy AI Analyze-Server API
from __future__ import annotations
import struct

from .connection import Connection
from .com_definition import (
    Probability,
    LabeledProbability,
    CommandCode,
    ProbabilityType,
)
from .com_base import BaseCommand


class GetProbabilitiesCommand(BaseCommand):

    _CODE = CommandCode.GET_PROBABILITIES
    PROB_SIZE = 13
    LABELED_PROB_SIZE = 14
    PROB_OFFSET = 3

    # ログの詳細出力
    verbose = False

    def __init__(
        self,
        inspect_id: int,
        connection: Connection = None,
        logging: bool = True,
    ):
        """ GetProbabilities コマンド制御
        Args:
            inspect_id:     取得対象の検査番号
            connection:     通信対象のTCP接続
            logging:        送受信時のログ出力フラグ
        """
        super().__init__(connection=connection, logging=logging)
        self.inspect_id = inspect_id
        self.data = struct.pack(f'< Q', inspect_id)

    def _decode_reply(self, reply: bytes):
        """ Inspect コマンドの応答内容確認

        Args:
            reply (bytes):      受信応答データ（ヘッダ以外）
        """
        prob_type, prob_len = struct.unpack(
            '< B H',
            reply[:self.PROB_OFFSET]
        )
        prob_data = reply[self.PROB_OFFSET:]

        # 受信データの格納
        self.prob_type = ProbabilityType(prob_type)
        self.prob_size = prob_len
        self.prob_list = []
        if prob_type == ProbabilityType.LABELED:
            prob_size = self.LABELED_PROB_SIZE
        else:
            prob_size = self.PROB_SIZE
        for offset in range(0, prob_len * prob_size, prob_size):
            if prob_type == ProbabilityType.LABELED:
                x1, y1, x2, y2, typ, label, prob = struct.unpack(
                    '< H H H H B B f',
                    prob_data[offset:offset + prob_size]
                )
                prob = LabeledProbability(x1, y1, x2, y2, typ, label, prob)
            else:
                x1, y1, x2, y2, typ, prob = struct.unpack(
                    '< H H H H B f',
                    prob_data[offset:offset + prob_size]
                )
                prob = Probability(x1, y1, x2, y2, typ, prob)
            self.prob_list.append(prob)

    def __str__(self):
        string = (
            f'{super().__str__()} '
            f'InspectID: {self.inspect_id}(=0x{self.inspect_id:#016X}) -> '
        )
        if self.is_received_ack:
            string += (
                f'ProbabilityList: {self.prob_size} items '
                f'({self.process_time} ms)'
            )
            if self.verbose:
                for prob in self.prob_list:
                    string += '\n    ' + str(prob)
        return string
