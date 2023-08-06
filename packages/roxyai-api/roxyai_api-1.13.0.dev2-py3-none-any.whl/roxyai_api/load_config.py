# (c) Roxy Corp. 2020-
# Roxy AI Inspect-Server API
from __future__ import annotations
from typing import Any, Union
import os
from pathlib import Path
import json5 as json
import re
from termcolor import cprint
from shutil import copy2
from logging import getLogger

log = getLogger(__name__)


class BaseConfig():
    _path = None
    _items = {}

    ROOT_PATH = Path(os.environ.get('Roxy_AI', 'C:/RoxyAI')) / 'roxy-ai-runtime'
    DEFAULT_FOLDER = ROOT_PATH / 'config/default'
    DEFAULT_PATH = None

    def __init__(self, src: dict[str, Any]):
        self._items = {}
        self.update(src)

    def update(self, src: dict[str, Any]):
        """ 設定値の内容を辞書から更新
        Args:
            src (dict):     値を読み込む辞書
        """
        for key in src.keys():
            if key in dir(self):
                if (
                    # 定数や内部変数、メソッド、プロパティなら無視する
                    key[0] == "_"
                    or key.isupper()
                    or callable(getattr(self, key))
                    or key in ('path', 'items')
                ):
                    continue

                val = src[key]
                setattr(self, key, val)
                self._items[key] = val
                # 開発中のデバグ用
                # print(f'>>>>>>>>> self: {self}, attr: {key}, val: {val}')

    @classmethod
    def load(cls, path: Union[str, Path] = None) -> BaseConfig:
        """ 行コメントを含むJSONファイルの読み込み
        Args:
            path (str)      JSON形式の設定ファイルパス
        Returns:
            dict            読み込んだ設定ファイルの辞書
        """
        if path:
            path = Path(path).expanduser().resolve().absolute()
        else:
            if not cls.DEFAULT_PATH:
                raise NotImplementedError()
            path = Path(cls.DEFAULT_PATH)

        if not path.exists():
            log.warning(f'{cls.__name__}: not found configuration file: {path}')
            default_file = cls.DEFAULT_FOLDER / path.name
            if default_file.exists():
                try:
                    copy2(default_file.as_posix(), path)
                    cprint(
                        f'Created a config file "{path}" '
                        f'by coping it from "{default_file}".',
                        color='yellow'
                    )
                except Exception as e:
                    log.error(
                        f'{cls.__name__}: cannot create a config file '
                        f'because copy from {default_file} failed.\n'
                        f'{e}'
                    )
                    raise
            else:
                raise RuntimeError(
                    f'{cls.__name__}: not found configuration file: {path}'
                )
        try:
            data = path.read_text(encoding="utf_8")
            dic = json.loads(data)
            instance = cls(dic)
            instance._path = path
        except Exception as e:
            raise RuntimeError(
                f'failed to load configuration file: {path}\n{e}'
            )
        return instance

    @property
    def items(self) -> dict[str, Any]:
        """ 設定ファイル情報の一覧取得
        """
        return self._items

    @property
    def path(self) -> Path:
        """ 設定ファイルのパス
        """
        return self._path

    def dump_items(
        self, dumper, prefix: str, max_length: int = 255, default=True, exclusion=[]
    ):
        """ ユーザが設定したデータの一覧をログ出力
        """
        if default:
            # デフォルト値を含む場合
            base_attrs = dir(super())
            items = {
                attr: getattr(self, attr) for attr in dir(self)
                if (
                    attr not in base_attrs
                    and attr[:1].islower()
                    and not callable(getattr(self, attr))
                    and attr not in ('path', 'items')
                )
            }

        else:
            items = self._items

        for name, val in items.items():
            if name in exclusion:
                # 除外のキーは除く
                continue
            text = f'{prefix}{name:25}: {val}'
            if len(text) >= max_length - 3:
                text = text[:(max_length - 3)] + '...'
            dumper(text)

    def __str__(self) -> str:
        name = self.__class__.__name__.replace('Config', '')
        text = f'{name} : {self._path}'
        return text


class CommonConfig(BaseConfig):
    """ 共通設定ファイル
    """
    # 定数定義
    ROOT_PATH = BaseConfig.ROOT_PATH
    DEFAULT_PATH = ROOT_PATH / 'config/common.json'

    # デフォルト設定値
    product_top = str(ROOT_PATH / 'roxy-ai-runtime/fixed_model')

    @classmethod
    def load(cls, path: Union[str, Path] = None) -> CommonConfig:
        return super().load(path)


class ServerConfig(BaseConfig):
    """ 共通サーバ設定ファイル
    """
    # 定数定義
    ROOT_PATH = BaseConfig.ROOT_PATH
    DEFAULT_PATH = ROOT_PATH / 'config/server.json'

    def __init__(self, dic: dict[str, Any]):
        super().__init__(dic)
        for item, val in dic.items():
            if type(val) is list:
                hosts = []
                ports = []
                for v in val:
                    mr = re.match(r'(?P<host>(\d+\.\d+\.\d+\.\d+))\:(?P<port>(\d+))', v)
                    if mr:
                        hosts.append(mr['host'])
                        ports.append(int(mr['port']))
                setattr(self, item + '_host', hosts)
                setattr(self, item + '_port', ports)
            self._items[item] = val

    @classmethod
    def load(cls, path: Union[str, Path] = None) -> ServerConfig:
        return super().load(path)
