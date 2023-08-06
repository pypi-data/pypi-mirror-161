# (c) Roxy Corp. 2020-
# Roxy AI Monitor API
from __future__ import annotations
from pathlib import Path
import json5 as json
from logging import getLogger
from dataclasses import dataclass

log = getLogger(__name__)


# 共通のラベル情報定義
OK_LABEL_NAME = 'OK'
OK_LABEL_COLOR = 'R=256,G=256,B=256'
OTHER_LABEL_NAME = 'Other'
OTHER_LABEL_COLOR = 'R=127,G=127,B=127'


def _color2bgr(color: str) -> tuple[int, int, int]:
    """ カラー定義文字列からRGB値への変換
    Args:
        color:  RGB値定義文字列
            例) R=256,G=256,B=256
    Return:
        tuple[R, G, B]      変換値
        None:               変換失敗
    """
    try:
        rs, gs, bs = color.split(',')
        ri = int(rs.replace('R=', ''))
        gi = int(gs.replace('G=', ''))
        bi = int(bs.replace('B=', ''))
        ret = (bi, gi, ri)
    except Exception:
        ret = None
    return ret


@dataclass
class ModelLabelInfo():
    """ モデル毎のラベル情報
    """
    id: int
    name: str
    color: str

    def __post_init__(self):
        self.bgr = _color2bgr(self.color)

    def __str__(self) -> str:
        text = f'label ({self.id}): "{self.name}" {self.color}'
        return text

    @classmethod
    def OK(cls) -> ModelLabelInfo:
        return ModelLabelInfo(0, OK_LABEL_NAME, OK_LABEL_COLOR)


class ProductLabelInfo():
    """ 製品全体の統合ラベル情報
    """
    # ラベル情報（0番は利用しない）
    _label_list = []
    LABEL_ID_OK = 0

    # 違和感検知（その他の不良）用のラベル
    _other_label = None
    _ok_label = None

    @classmethod
    def clear(cls):
        cls._label_list = []
        cls._other_label = None
        # 正常ラベルはデフォルトで登録しておく
        cls._ok_label = ProductLabelInfo(
            cls.LABEL_ID_OK, OK_LABEL_NAME, OK_LABEL_COLOR
        )
        cls._label_list.append(cls._ok_label)

    @classmethod
    def set_info(
        cls, model_name: str, index: int, label_name: str, color: str
    ) -> int:
        """ ラベルを設定してIDを取得
        Args:
            model_name:     モデル名
            index:          モデルにおけるラベルのインデックス番号
            label_name:     ラベル名
            color:          色情報
        Returns:
            ラベルの統一番号
        """
        info = ProductLabelInfo(index, label_name, color)
        if info in cls._label_list:
            # 既に同じラベルがあればそれに差替え
            i = cls._label_list.index(info)
            info = cls._label_list[i]
            label_id = info._label_id
        else:
            # 新規なら追加登録
            label_id = len(cls._label_list)
            info._label_id = label_id
            cls._label_list.append(info)
        # モデル名を登録
        info._model_name.append(model_name)

        if cls._other_label:
            # OTHERラベルがある場合は最後のラベルとして設定
            cls._other_label._label_id = len(cls._label_list)

        return label_id

    @classmethod
    def set_other(cls, model_name: str, index: int):
        """ 違和感検知用に「その他の不良」のラベルを設定する
        Args:
            model_name:     モデル名
            index:          モデルにおけるOTHERラベルのインデックス番号
        Note:
            その他の不良ラベルは常にラベルリストの最後に設定
        """
        if not cls._other_label:
            # ラベルが未登録ならば新規作成
            cls._other_label = ProductLabelInfo(
                index, OTHER_LABEL_NAME, OTHER_LABEL_COLOR
            )
        # モデル名を登録
        cls._other_label._model_name.append(model_name)
        # 最後のラベルとしてIDを設定
        cls._other_label._label_id = len(cls._label_list)

    @classmethod
    def get(cls, label_id: int):
        """ ラベルIDから情報を取得
        Args:
            label_id:   ProductLabelInfoのラベルの統一番号
        """
        if (label_id < 0) or (len(cls._label_list) <= label_id):
            ret = cls._other_label
        else:
            ret = cls._label_list[label_id]
        return ret

    @classmethod
    def get_list(cls, include_ok: bool = False) -> list:
        """ その他の不良を含めた全てのリストを返す
        """
        if include_ok:
            # 正常ラベルを含める場合
            all_list = cls._label_list.copy()
        else:
            # 正常ラベルを含めない場合
            all_list = cls._label_list[1:].copy()

        if cls._other_label:
            # 違和感検知用に「その他の不良」ラベルがあれば追加
            all_list.append(cls._other_label)

        return all_list

    @classmethod
    def get_other_id(self) -> int:
        """ 違和感検知用のOTHERラベルの統一番号を取得
        Note:
            常に全モデルのラベルの最後に追加される
        """
        return len(self._label_list)

    def __init__(self, index: int, name: str, color: str):
        """ ラベル情報
        Args:
            index:             ラベル番号（モデル内の番号）
            name:           ラベル名
            color:          色情報
        """
        # 統合ラベル番号
        self._index = index
        self._name = name
        self._color = color

        # 統合ラベル番号
        self._label_id = 0
        # このラベルを含むモデル名
        self._model_name = []

    def __eq__(self, o: ProductLabelInfo) -> bool:
        return (
            (self._index == o._index)
            and (self._name == o._name)
            and (self._color == o._color)
        )

    @property
    def id(self) -> int:
        return self._label_id

    @property
    def model_name(self) -> int:
        return self._model_name

    @property
    def index(self) -> int:
        return self._index

    @property
    def name(self) -> str:
        return self._name

    @property
    def color(self) -> str:
        return self._color

    @property
    def bgr(self) -> tuple[int, int, int]:
        return _color2bgr(self._color)

    def __str__(self) -> str:
        text = f'label ({self._label_id}): "{self._model_name}" '
        text += f'{self._index:2d}) {self._name} {self._color}'
        return text


class LabelManager():
    """ ラベルとモデルの関連を管理する
    """
    _LABELS_FILE = 'labels.txt'
    _MODEL_CONFIG_FILE = 'config.json'
    _INSPECT_CONFIG_FILE = 'inspect_config.json'

    @classmethod
    def get(cls, product_folder: str, model_list: list[str] = None) -> LabelManager:
        """ 製品全体のラベル情報を取得する
        Args:
            product_folder:     製品情報フォルダ
            model_list:         使用モデル名のリスト
        Return:
            LabelManager
        """
        try:
            ProductLabelInfo.clear()
            label_info = cls(product_folder, model_list)
        except Exception as e:
            log.exception(f'{cls.__name__}: failed to load label info\n{e}')
            label_info = None
        return label_info

    def __init__(self, product_folder: str, model_list: list[str] = None):
        """ モデル毎のラベル情報を管理するクラス
        Args:
            product_folder (str or Path):   製品フォルダ
            model_list:         使用モデル名のリスト
        Note:
            製品名フォルダ配下のinspect_config.jsonからモデル名を取得し、
        """
        self._product_path = Path(product_folder)

        self._label_set = set()
        self._model_list = model_list
        # モデル毎の統合ラベル番号辞書
        self._product_label_dict: dict[str, dict[int, ProductLabelInfo]] = {}
        # モデル毎のラベル番号辞書
        self._model_label_dict: dict[str, ModelLabelInfo] = {}

        if not self._product_path.exists():
            # ファイルが存在しない
            log.error(f'Not found inspect_config.json. {self._product_path}')
            raise RuntimeError
        self._load_all_model_label()

    def _load_all_model_label(self):
        """ 製品フォルダ配下の全てのモデルのラベル情報を読込
        """
        model_path_list = list(
            path for path in self._product_path.iterdir()
            if path.is_dir()
        )
        labels_path_list = list(
            md / self._LABELS_FILE for md in model_path_list
        )

        # 違和感検知用のOTHERラベルのインデックス（全てのモデルで共通化のため別管理）
        other_label = {}

        for label_path in labels_path_list:
            if not label_path.exists():
                # ラベルファイルが無ければ無効フォルダとしてスキップ
                continue
            model_name = label_path.parent.name
            if self._model_list and (model_name not in self._model_list):
                # 未使用のモデルならスキップ
                continue

            # モデルラベル情報の生成または取得
            model_dict = self._model_label_dict.get(
                model_name, {0: ModelLabelInfo.OK()}
            )
            # モデル毎のラベル情報の読み出し
            try:
                data = label_path.read_text(encoding='utf_8_sig', errors='ignore')
                labels = {}
                # OKがラベルID=0となるため不良ラベルは1開始
                index = 1
                for line in data.rstrip('\n').split('\n'):
                    # ラベル定義の行から値を取得
                    parts = line.rstrip('\n').split('\t')
                    # ラベル定義のindexは無視
                    # index = int(parts[0])
                    name = parts[1]
                    color = parts[2]
                    used = parts[3]

                    if used == 'unused':
                        # 未使用ラベルはindexの対象外
                        continue

                    # 読み込んだ情報を登録
                    label_info = ProductLabelInfo.set_info(
                        model_name, index, name, color
                    )
                    labels[index] = label_info
                    model_dict[index] = ModelLabelInfo(index, name, color)
                    index += 1

            except Exception as e:
                log.warning(f'Failed to load: {label_path}, {e}')
                # 失敗したファイルは無視して処理継続

            # 違和感検知の有効／無効読み出し
            cfg_path = label_path.parent / self._MODEL_CONFIG_FILE
            try:
                if cfg_path.exists():
                    # モデル設定から Anomal の有効／無効を取得
                    data = cfg_path.read_text(encoding='utf_8_sig ', errors='ignore')
                    dic: dict = json.loads(data)
                    if dic.get('anormal_param', {}).get('enable_anormal', False):
                        # 違和感検知が有効ならばOTHERラベルを登録
                        ProductLabelInfo.set_other(model_name, index)
                        other_label[model_name] = index
                        model_dict[index] = ModelLabelInfo(
                            index, OTHER_LABEL_NAME, OTHER_LABEL_COLOR
                        )
            except Exception as e:
                log.warning(f'Failed to load model config: {cfg_path}, {e}')

            # モデル毎の辞書に登録
            self._product_label_dict[model_name] = labels
            self._model_label_dict[model_name] = model_dict
            log.debug(f'Loaded {len(labels)} labels for model "{model_name}".')

        # 違和感検知用のラベル番号を各モデルに登録
        for model_name, index in other_label.items():
            self._product_label_dict[model_name][index] = ProductLabelInfo.get_other_id()

        log.debug(f'loaded total {len(ProductLabelInfo.get_list())} labels.')

    def get_info_json(self) -> str:
        """ 統合ラベルの情報取得
        Returns:
            全モデルの統合ラベル情報を表すJSONデータ
        """
        # モニター設定情報の取得
        conf_path = (self._product_path / self._INSPECT_CONFIG_FILE).resolve().absolute()
        try:
            data = conf_path.read_text(encoding='utf-8', errors='ignore')
            dic: dict = json.loads(data)
            monitor_conf = dic.get('monitor', {})
        except Exception as e:
            log.warning(f'failed to load monitor config: {conf_path}\n{repr(e)}')

        # モニター情報の読込
        title_list = []
        screen_list = monitor_conf.get('screen', [])
        for screen in screen_list:
            sc_id = screen.get('screen_id')
            sc_title = screen.get('title')
            if sc_title:
                title_list.append(sc_title)
            else:
                log.debug(f'{self}: screen {sc_id} does not have "title"')

        # 全ラベルの情報リスト
        label_list = []
        for label in ProductLabelInfo.get_list():
            label_list.append({
                'label_id': label.id,
                'label_name': label.name,
                'color': label.color,
            })

        all_label_info = {
            'label': label_list
        }

        label_json = json.dumps(all_label_info, ensure_ascii=False)
        return label_json

    def get_id(self, model_name: str, label_index: int) -> int:
        """ モデル名とモデル定義のラベル番号から統合のラベル番号取得
        Args:
            model_name:     モデル名
            label_index:    モデルデータ内に定義されたラベル番号
        Returns:
            全モデルで統一化されたラベル番号
        """
        labels = self._product_label_dict.get(model_name, {})
        label_id = labels.get(label_index)
        return label_id

    def get_model_label(self, model_name: str) -> dict[int, ModelLabelInfo]:
        """ モデル名からモデル毎のラベル情報辞書を取得する
        Args:
            model_name:     モデル名
        Returns:
            モデル毎のラベル情報辞書
        """
        return self._model_label_dict.get(model_name, {})

    @property
    def label_list(self) -> list[ProductLabelInfo]:
        return ProductLabelInfo.get_list()
