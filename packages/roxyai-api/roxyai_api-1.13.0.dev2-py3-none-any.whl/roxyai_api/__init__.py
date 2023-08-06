# (c) Roxy Corp. 2020-
# Roxy AI Inspect-Server API
from .connection import Connection
from .com_definition import (
    SIGN_CODE,
    HEADER_SIZE,

    CommandCode,
    CommandStatus,
    Judgment,
    JudgmentCount,
    JudgmentCounter,
    Probability,
    LabeledProbability,
    InspectResult,
)
from .inspect_image import (
    ImageFormat,
    ColorOrder,
    ImageBuffer,
    InspectImage,
    ImageConvertionFailed,
    ImageRect,
)
from .inspect_buffer import InspectBuffer
from .com_base import BaseCommand
from .com_echo import EchoCommand
from .com_initialize import InitializeCommand
from .com_terminate import TerminateCommand
from .com_inspect import InspectCommand
from .com_get_probabilities import GetProbabilitiesCommand
from .com_get_image import GetImageCommand

from .svr_base_handler import ServerBaseHandler
from .svr_command_handler import ServerCommandManager

from .label_info import (
    ProductLabelInfo, ModelLabelInfo, LabelManager
)

# Deprecated
# 過去APIバージョン互換のために定義
LabelInfo = ProductLabelInfo

__all__ = [
    Connection,
    BaseCommand,

    EchoCommand,
    InitializeCommand,
    TerminateCommand,
    InspectCommand,
    GetProbabilitiesCommand,
    GetImageCommand,

    CommandCode,
    CommandStatus,
    Judgment,
    JudgmentCount,
    JudgmentCounter,
    Probability,
    LabeledProbability,
    InspectResult,

    ImageFormat,
    ColorOrder,
    ImageBuffer,
    InspectImage,
    ImageConvertionFailed,
    ImageRect,

    InspectBuffer,

    ServerBaseHandler,
    ServerCommandManager,

    ModelLabelInfo,
    ProductLabelInfo,
    LabelManager,

    SIGN_CODE,
    HEADER_SIZE,

    # Deprecated
    LabelInfo
]
