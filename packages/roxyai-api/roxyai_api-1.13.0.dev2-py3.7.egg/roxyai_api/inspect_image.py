# (c) Roxy Corp. 2020-
# Roxy AI Coordinator
from __future__ import annotations
from typing import Optional, Tuple, Union, NamedTuple
from enum import IntEnum
import numpy as np
from mmap import mmap
import struct
import cv2
import traceback
from pathlib import Path
from io import BytesIO
from urllib.parse import quote, urlparse, parse_qs, urlencode

from .inspect_buffer import InspectBuffer

from logging import getLogger
log = getLogger(__name__)


class ImageRect(NamedTuple):
    """ 領域指定用NamedTupleクラス
    """
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0

    def __bool__(self) -> bool:
        """ 面積があればTrueを返す
        """
        return (self.x1 - self.x2) and (self.y1 - self.y2)


class ImageConvertionFailed(RuntimeWarning):
    """ 画像変換エラー
    """
    def __init__(self, src_fmt, dst_fmt, order, exception):
        if type(src_fmt) is int:
            src_fmt = ImageFormat(src_fmt)
        self.src_fmt = src_fmt

        if type(dst_fmt) is int:
            dst_fmt = ImageFormat(dst_fmt)
        self.dst_fmt = dst_fmt

        if type(order) is int:
            order = ColorOrder(order)
        self.order = order

        self.exception = exception

    def __str__(self):
        return (
            f'image conversion failed '
            f'from [{self.src_fmt.name}] '
            f'to [{self.dst_fmt.name}] '
            f'color order: {self.order.name}'
        )


class ImageFormat(IntEnum):
    """ イメージフォーマット値の定義クラス
    """
    NONE = 0x00
    RAW = 0x01
    JPEG = 0x02
    PNG = 0x03
    BMP = 0x04
    # URL形式の外部データ場所指定
    URL = 0xFE
    # 内部利用のフォーマット形式
    NDARRAY = 0xFF

    RAW_HADER_SIZE = 5

    def __str__(self):
        return f'{self.name}(0x{self.value:02X})'

    @property
    def suffix(self) -> str:
        return IMG_FORMAT_SUF(self.value)

    @staticmethod
    def all_suffix(header: str = None) -> tuple[str]:
        if header is None:
            return IMG_SUFFIX_LIST
        return tuple(header + s for s in IMG_SUFFIX_LIST)

    @classmethod
    def from_suffix(cls, suffix: str) -> ImageFormat:
        """ 拡張子からフォーマット値を取得
        Args:
            suffix (str)    拡張子文字列
        Returns:
            ImageFormat:    拡張子に対応するフォーマット値
            None:           拡張子が不正
        """
        suf = suffix.lower()
        if suf and suf[0] != '.':
            suf = '.' + suf
        val = IMG_SUFFIX_FMT.get(suf)
        if val:
            return cls(val)
        return None

    @classmethod
    def check_header(cls, data: memoryview):
        """ 画像データのヘッダからフォーマットを取得
        Args:
            data:   画像データのヘッダ
        Returns:
            ImageFormat:    解析成功
            None:           解析失敗
        Note:
            data は bytes でも良い。
        """
        size = len(data)

        # PNGフォーマット(http://www.w3.org/TR/PNG/)の読み取り
        # ※ 古いPNGフォーマットは非対応
        if (size >= 8) and (data[:8] == b'\x89PNG\r\n\x1A\n'):
            return cls.PNG
        if (size > 2) and (data[:2] == b'BM'):
            return cls.BMP
        if (size > 4) and (data[:2] == b'\xFF\xD8'):
            return cls.JPEG
        if size > cls.RAW_HADER_SIZE:
            # RAWフォーマットとサイズ一致ならRAWと判定
            width, height, order = struct.unpack('< H H B', data[:5])
            depth = ColorOrder(order).depth
            if size == (cls.RAW_HADER_SIZE + (width * height * depth)):
                return cls.RAW
        return None

    @staticmethod
    def set_raw_image(buffer: memoryview, width: int, height: int, order: ColorOrder) -> np.ndarray:
        """ バッファにRAWフォーマットのヘッダを設定する
        Args:
            buffer:     データバッファ
            width:      イメージの幅
            height:     イメージの高さ
            orger:      カラーフォーマット
        Returns:
            None:       設定失敗
            np.ndarray: 画像データの ndarray
        """
        data = None
        if len(buffer) > 5:
            buffer[0:2] = struct.pack('<H', width)
            buffer[2:4] = struct.pack('<H', height)
            buffer[4] = order.value
            # データ領域のndarrayへの変換
            dt = np.dtype('uint8')
            dt = dt.newbyteorder('<')
            data: np.ndarray = np.frombuffer(
                buffer, dtype=dt, offset=ImageFormat.RAW_HADER_SIZE
            )
            data = data.reshape(height, width, order.depth)
        return data


class ColorOrder(IntEnum):
    """ Rawイメージの色データバイト順の定義クラス
    """
    GRAY = 1
    BGR = 2
    RGB = 3
    BGRA = 4

    BAYER_RG = 10
    BAYER_BG = 11

    @property
    def depth(self):
        """ 色順序による色深度（ピクセルあたりバイト数）
        """
        if self == ColorOrder.GRAY:
            ret = 1
        elif self in (
            ColorOrder.BGR, ColorOrder.RGB,
            ColorOrder.BAYER_BG, ColorOrder.BAYER_RG,
        ):
            ret = 3
        elif self == ColorOrder.BGRA:
            ret = 4
        return ret

    def __str__(self):
        return f'{self.name}({self.value:d})'


# フォーマット変換の定義
IMG_FORMAT_SUF = {
    ImageFormat.RAW: '.bin',
    ImageFormat.JPEG: '.jpg',
    ImageFormat.PNG: '.png',
    ImageFormat.BMP: '.bmp',
}

IMG_SUFFIX_LIST = tuple(IMG_FORMAT_SUF.values())

IMG_SUFFIX_FMT = {
    **{v: ImageFormat(k) for k, v in IMG_FORMAT_SUF.items()},
    '.jpeg': ImageFormat(ImageFormat.JPEG),
}

# CVの変換用パラメータ定義
__JPEG_PARAMS = (cv2.IMWRITE_JPEG_QUALITY, 95)
__PNG_PARAMS = (cv2.IMWRITE_PNG_COMPRESSION, 1)


def _bin_to_ndarary(src) -> tuple[np.ndarray, ColorOrder]:
    # 構造情報の設定
    width, height, order = struct.unpack('< H H B', src[:5])
    dt = np.dtype('uint8')
    dt = dt.newbyteorder('<')
    dst: np.ndarray = np.frombuffer(src, dtype=dt, offset=5)
    depth = ColorOrder(order).depth
    if depth == 1:
        dst = dst.reshape((height, width))
    else:
        dst = dst.reshape((height, width, depth))
    return dst, ColorOrder(order)


def _image_to_ndarary(src) -> tuple[np.ndarray, ColorOrder]:
    dt = np.dtype('uint8')
    dt = dt.newbyteorder('<')
    buf = np.frombuffer(src, dtype=dt, offset=0)
    dst: np.ndarray = cv2.imdecode(buf, cv2.IMREAD_IGNORE_ORIENTATION | cv2.IMREAD_UNCHANGED)
    if len(dst.shape) == 2:
        order = ColorOrder.GRAY
    elif dst.shape[2] == 3:
        # CVは24bitをBGRの色順で保持
        order = ColorOrder.BGR
    elif dst.shape[2] == 4:
        # CVは32bitをBGRAの色順で保持
        order = ColorOrder.BGRA
    return dst, ColorOrder(order)


def _ndarary_to_bin(src: np.ndarray, order: ColorOrder) -> bytes:
    shape = (src.shape[1], src.shape[0], order)
    dst = struct.pack('< H H B', *shape)
    dst += src.tobytes()
    return dst


def _ndarary_to_jpeg(src, order: ColorOrder) -> bytes:
    if order == ColorOrder.RGB:
        # CV2の色順に変換
        src = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    ret, dst = cv2.imencode('.jpg', src, params=__JPEG_PARAMS)
    if not ret:
        RuntimeWarning('imencode for jpg failed')
    return bytes(np.frombuffer(dst, dtype=np.uint8))


def _ndarary_to_png(src, order: ColorOrder) -> bytes:
    if order == ColorOrder.RGB:
        # CV2の色順に変換
        src = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    ret, dst = cv2.imencode('.png', src, params=__PNG_PARAMS)
    if not ret:
        RuntimeWarning('imencode for png failed')
    return bytes(np.frombuffer(dst, dtype=np.uint8))


def _ndarary_to_bmp(src, order: ColorOrder) -> bytes:
    if order == ColorOrder.RGB:
        # CV2の色順に変換
        src = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    ret, dst = cv2.imencode('.bmp', src)
    if not ret:
        RuntimeWarning('imencode for bmp failed')
    return bytes(np.frombuffer(dst, dtype=np.uint8))


class ImageBuffer(BytesIO):
    name = 'Buffer'

    def __init__(self, *args, **kwargs):
        """ 分割受信用有りの画像専用バッファ
        """
        super().__init__(*args, **kwargs)

    def close(self, release: bool = None):
        # 通常の書き込み完了時にはクローズさせない
        if release:
            super().close()
        return


class InspectImage():
    """ 検査に利用するイメージデータのキャッシュ機能付き管理クラス
    """
    DECODER = {
        ImageFormat.RAW: _bin_to_ndarary,
        ImageFormat.JPEG: _image_to_ndarary,
        ImageFormat.PNG: _image_to_ndarary,
        ImageFormat.BMP: _image_to_ndarary,
    }

    ENCODER = {
        ImageFormat.RAW: _ndarary_to_bin,
        ImageFormat.JPEG: _ndarary_to_jpeg,
        ImageFormat.PNG: _ndarary_to_png,
        ImageFormat.BMP: _ndarary_to_bmp,
    }

    def __init__(
        self,
        fmt: ImageFormat,
        data: Union[bytes, np.ndarray],
        path: Optional[Path] = None,
        order: ColorOrder = None,
        name: str = '',
    ):
        """ 検査用の画像データ管理
        Args:
            fmt     data で渡す画像のフォーマット
                    不明は場合は None で指定
            data:   画像データ
            path    読み込んだ元ファイルのパス
            order:  画像の色データバイト順
            name:   画像の識別名称
        """
        self._org_fmt = ImageFormat(fmt)
        self._data = {self._org_fmt: data}

        self._path = Path(path) if path else None
        self._name = str(name)
        if not name:
            # 名前の指定が無ければ自動で定義
            path_name = None
            try:
                path_name = Path(path).name
            except Exception:
                pass
            if path_name:
                # 名称が未指定でパスがある場合はファイル名を設定
                self._name = path_name
            else:
                self._name = f'image[{self._org_fmt.name}]'
        self._keep_count = 1

        # カラーオーダーを設定
        if order is None:
            if fmt == ImageFormat.NDARRAY:
                if len(data.shape) == 2:
                    order = ColorOrder.GRAY
                elif data.shape[2] == 3:
                    # CVは24bitをBGRの色順で保持
                    order = ColorOrder.BGR
                elif data.shape[2] == 4:
                    # CVは32bitをBGRAの色順で保持
                    order = ColorOrder.BGRA
        self._order = order
        # キャッシュ管理情報
        self._parent: InspectImage = None
        self._children: list[InspectImage] = []
        self._zoom: float = None
        self._clip: ImageRect = None
        # バッファ管理情報
        self._src_buffer: BytesIO = None
        self._src_view: memoryview = None
        self._src_size = 0
        self._mmap_path = None

    @classmethod
    def get_empty(
        cls,
        width: int = 1,
        height: int = 1,
        color: Union[tuple[int, int, int], tuple[int, int, int, int], int] = (0, 0, 0)
    ) -> InspectImage:
        """ 空のイメージを取得する
        Args:
            width:      画像の幅ピクセル数
            height:     画像の高さピクセル数
            colose:     塗りつぶし色
                (int, int, int):         RGB画像として作成(3ch)
                (int, int, int, int):    RGBA画像として作成(4ch)
                int:                     Gray画像として作成(1ch)
        """
        if (type(color) is int):
            order = ColorOrder.GRAY
        elif len(color) == 1:
            color = color[0]
            order = ColorOrder.GRAY
        elif len(color) == 3:
            order = ColorOrder.RGB
        elif len(color) == 4:
            order = ColorOrder.BGRA
        else:
            raise TypeError(f'{cls.__name__}: invalid color parameter {color}')

        if order == ColorOrder.GRAY:
            data = np.full((height, width), color, np.uint8)
        else:
            data = np.full((height, width, order.depth), color, np.uint8)
        instance = InspectImage(ImageFormat.NDARRAY, data, order=order)
        return instance

    @classmethod
    def from_buffer(
        cls,
        buffer: Union[BytesIO, mmap, memoryview],
        name: str = None,
        path: Path = None,
        width: int = None,
        height: int = None,
        order: ColorOrder = None,
    ) -> InspectImage:
        """ バッファから画像を取得する
        Args:
            buffer:     データバッファ
            name:       ファイル名（パス指定）
            path:       ファイルパス
            width:      画像の幅ピクセル数
            height:     画像の高さピクセル数
            order:      画像の色データバイト順
        Notes:
            バッファへの読み込みが完了していない場合は
            バッファへの書き込み後に flush_buffer する必要がある。
        """
        instance = None

        if isinstance(buffer, BytesIO):
            completed = None
            with buffer.getbuffer() as view:
                completed = cls.check_data(view)
            if completed:
                # 読み込み完了済みならば初期化
                view = buffer.getbuffer()
                fmt = ImageFormat.check_header(view)
                instance = cls(fmt, view, name=name)
                instance._src_buffer = buffer
                instance._src_size = len(view)
                instance._src_view = view
        else:
            try:
                # 画像フォーマットと読込状態の確認
                fmt = cls.check_data(buffer)
                if fmt:
                    # 読み込み完了済みならば初期化
                    instance = cls(fmt, buffer, name=name, path=path)
                    instance._src_buffer = None
                    instance._src_size = len(buffer)
                    instance._src_view = buffer
                    if isinstance(buffer, mmap):
                        # メモリマップドファイルならパスを設定
                        instance._mmap_path = path
            except Exception as e:
                log.warning(
                    f'{cls.__name__}: failed to create an image from buffer\n{e}'
                )

        return instance

    @classmethod
    def from_url(cls, url: Union[str, bytes]) -> InspectImage:
        """ URLから画像を取得する
        Args:
            url:    URL
        """
        instance = None
        if type(url) is bytes:
            try:
                # URLデータの解析
                url = url.decode('utf-8', errors='ignore')
            except Exception as e:
                log.warning(f'{cls.__name__} url decode error: {e}')
        try:
            url_info = urlparse(url)
            url_prams = parse_qs(url_info.query)
        except Exception as e:
            log.warning(f'{cls.__name__} url parse error: {url}\n{e}')
            url_info = None
            url_prams = {}

        # URLパラメータを取得
        try:
            width = int(url_prams.get('width', 0))
            height = int(url_prams.get('height', 0))
            order_param = url_prams.get('order')
            order = ColorOrder(order_param)
            clip_x1 = int(url_prams.get('clip_x1', 0))
            clip_y1 = int(url_prams.get('clip_y1', 0))
            clip_x2 = int(url_prams.get('clip_x2', 0))
            clip_y2 = int(url_prams.get('clip_y2', 0))
            clip_area = ImageRect(clip_x1, clip_y1, clip_x2, clip_y2)
        except Exception as e:
            log.warning(f'{cls.__name__} url parameters error: {url_prams}\n{e}')
            url_info = None

        if url_info:
            if url_info.scheme == 'file':
                # ファイルからデータの読み込み
                instance = cls.load(url_info.path)
            elif url_info.scheme == 'mmap':
                # メモリマップドファイルから画像データを取得
                buf = InspectBuffer(url_info.path)
                if None not in (width, height, order):
                    # サイズが全てパラメーター指定されている場合は ndarray として読込
                    data = ImageFormat.set_raw_image(buf.mmap, width, height, order)
                    instance = InspectImage(
                        ImageFormat.NDARRAY,
                        data=data,
                        path=url_info.path,
                        order=order,
                    )
                    pass
                else:
                    # サイズ指定が無い場合はRAWなどの画像フォーマットとして読込
                    instance = cls.from_buffer(
                        buf.mmap,
                        path=url_info.path,
                    )

            if clip_area:
                # 画像データのクリップ処理
                instance = instance.get_clipped(clip_area)

        return instance

    @classmethod
    def load(cls, path) -> InspectImage:
        """ ファイルから画像を読み込む
        """
        instance = None
        imgfile = Path(path)
        if imgfile.exists():
            data = imgfile.read_bytes()
            fmt = cls.check_data(data)
            if fmt:
                instance = cls(fmt, data, path=imgfile)
        return instance

    def save(self, path: Union[str, Path]) -> bool:
        """ ファイルに画像を書き込む
        Returns:
            True:   書き込み成功
            False:  書き込み失敗
        Note:
            ファイル名の拡張子で画像フォーマットを決定する
        """
        imgfile = Path(path)
        fmt = IMG_SUFFIX_FMT.get(imgfile.suffix)
        if fmt:
            data = self.get_image(fmt)
            if data:
                imgfile.write_bytes(data)
                if not self._path:
                    # ファイルパスが未登録ならばパス登録
                    self._path = imgfile
                return True
        return False

    def get_tf_image(self) -> np.ndarray:
        """ TensorFlow用のデータ取得
        """
        img = self.get_image()
        if img.size > 0:
            # 画像が存在する場合のみ変換実施
            # ndarrayがTF形式RGB(24bit)でなければ変換
            if self._order == ColorOrder.GRAY:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif self._order == ColorOrder.BGR:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            elif self._order == ColorOrder.BGRA:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            elif self._order == ColorOrder.BAYER_BG:
                img = cv2.cvtColor(img, cv2.COLOR_BAYER_BG2RGB)
            elif self._order == ColorOrder.BAYER_RG:
                img = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB)
        return img

    def get_image(
        self, fmt: ImageFormat = ImageFormat.NDARRAY,
    ) -> Union[np.ndarray, bytes, None]:
        """ 指定フォーマトの画像データを取得
        """
        img = self._data.get(fmt)
        if img is not None:
            # 対象フォーマットがキャッシュにあればそれを返す
            return img
        # 無ければ画像変換してそれを返す
        self.__convert(fmt)
        img = self._data.get(fmt)
        return img

    def get_size(self, fmt: ImageFormat = None) -> int:
        """ 指定フォーマットのデータサイズを取得
        """
        fmt = ImageFormat(fmt)
        img = self.get_image(fmt)
        if img is None:
            return None
        if fmt == ImageFormat.NDARRAY:
            return img.size
        else:
            return len(img)

    def __convert(self, fmt: ImageFormat = ImageFormat.NDARRAY):
        """ 画像フォーマット変換
        """
        if self._data.get(fmt) is not None:
            # 変換済みなら何もしない
            return

        if self._order is None:
            # 基準データ(ndarray)の作成
            src = self._data.get(self._org_fmt)
            try:
                if (src is None) and self._src_buffer:
                    # バッファからの読み込み途中の場合はビューから変換
                    self._src_buffer.flush()
                    with self._src_buffer.getbuffer() as view:
                        fmt = ImageFormat.check_header(view)
                        converter = self.DECODER[fmt]
                        dst, order = converter(view)
                else:
                    converter = self.DECODER[self._org_fmt]
                    dst, order = converter(src)
            except Exception as e:
                log.warning(traceback.format_exc())
                raise ImageConvertionFailed(self._org_fmt, ImageFormat.NDARRAY, None, e)
            self._data[ImageFormat.NDARRAY] = dst
            self._order = order

        if fmt != ImageFormat.NDARRAY:
            # 基準データ(ndarray)から変換先の画像データの作成
            src = self._data[ImageFormat.NDARRAY]
            converter = self.ENCODER[fmt]
            try:
                dst = converter(src, self._order)
            except Exception as e:
                log.warning(traceback.format_exc())
                raise ImageConvertionFailed(ImageFormat.NDARRAY, fmt, self._order, e)
            self._data[fmt] = dst

    def keep(self):
        """ 画像データを保持する(TBD)
        """
        self._keep_count += 1

    def release(self):
        """ 画像データを全て破棄する(TBD)
        """
        self._keep_count -= 1
        if self._keep_count > 0:
            # まだ保持している処理があるので破棄しない
            return
        self._data.clear()
        self._org_fmt = None
        if self._fnc_buf_release:
            # バッファの解放コールバックの呼び出し
            try:
                self._fnc_buf_release()
            except Exception as e:
                log.warning(
                    f'{e}: in callback for release image buffer: '
                    f'{self._fnc_buf_release()} '
                    f'<{self._name}>'
                )
            self._fnc_buf_release = None

    def get_clipped(
        self,
        area: ImageRect,
    ) -> InspectImage:
        """ 領域をクリップしたイメージオブジェクトを返す
        """
        area = ImageRect(*area)
        # キャッシュ探索
        che = [i for i in self._children if i._clip == area]
        if che:
            return che[0]
        # 画像生成
        org = self.get_image()
        buf = org[area.y1:area.y2, area.x1:area.x2]
        img = InspectImage(ImageFormat.NDARRAY, buf)
        # キャッシュ情報登録
        img._parent = self
        img._clip = area
        img._mmap_path = self._mmap_path
        self._children.append(img)
        return img

    def get_resized(self, width: int, height: int) -> InspectImage:
        """ 画像をリサイズしたイメージオブジェクトを返す
        """
        # キャッシュの探索
        target_shape = (height, width)
        che = [i for i in self._children if i.get_image().shape == target_shape]
        if che:
            return che[0]
        # 画像生成
        org = self.get_image()
        buf = cv2.resize(org, (width, height))
        img = InspectImage(ImageFormat.NDARRAY, buf)
        # キャッシュ情報登録
        img._parent = self
        self._children.append(img)
        return img

    def get_grayed(self) -> InspectImage:
        """ 画像をグレースケール化したイメージオブジェクトを返す
        """
        if self.order is ColorOrder.GRAY:
            # グレースケール画像ならばそのまま利用
            img = self
        else:
            # キャッシュの探索
            che = [i for i in self._children if i._order is ColorOrder.GRAY]
            if che:
                return che[0]
            # 画像生成
            org = self.get_image()
            if self._order is ColorOrder.RGB:
                cvt_code = cv2.COLOR_RGB2GRAY
            elif self._order is ColorOrder.BGR:
                cvt_code = cv2.COLOR_BGR2GRAY
            elif self._order is ColorOrder.BGRA:
                cvt_code = cv2.COLOR_BGRA2GRAY
            elif self._order is ColorOrder.BAYER_BG:
                cvt_code = cv2.COLOR_BAYER_BG2GRAY
            elif self._order is ColorOrder.BAYER_RG:
                cvt_code = cv2.COLOR_BAYER_RG2GRAY
            else:
                log.warning(f'invalid color order {self._order} in <{self._name}>')
                cvt_code = None
            try:
                buf = cv2.cvtColor(org, cvt_code)
                img = InspectImage(ImageFormat.NDARRAY, buf)
                # キャッシュ情報登録
                img._parent = self
                self._children.append(img)
            except Exception as e:
                log.warning(traceback.format_exc())
                raise ImageConvertionFailed(
                    self._org_fmt, ImageFormat.NDARRAY, ColorOrder.GRAY, e
                )
        return img

    def get_rgb_image(self) -> InspectImage:
        """ 画像をRGBカラー化したイメージオブジェクトを返す
        """
        if self.order is ColorOrder.RGB:
            # RGB画像ならばそのまま利用
            img = self
        else:
            # キャッシュの探索
            che = [i for i in self._children if i._order is ColorOrder.RGB]
            if che:
                return che[0]
            # 画像生成
            org = self.get_image()
            if self._order is ColorOrder.GRAY:
                cvt_code = cv2.COLOR_GRAY2RGB
            elif self._order is ColorOrder.BGR:
                cvt_code = cv2.COLOR_BGR2RGB
            elif self._order is ColorOrder.BGRA:
                cvt_code = cv2.COLOR_BGRA2RGB
            elif self._order is ColorOrder.BAYER_BG:
                cvt_code = cv2.COLOR_BAYER_BG2RGB
            elif self._order is ColorOrder.BAYER_RG:
                cvt_code = cv2.COLOR_BAYER_RG2RGB
            else:
                log.warning(f'invalid color order {self._order} in <{self._name}>')
                cvt_code = None
            try:
                buf = cv2.cvtColor(org, cvt_code)
                img = InspectImage(ImageFormat.NDARRAY, buf)
                # キャッシュ情報登録
                img._parent = self
                self._children.append(img)
            except Exception as e:
                log.warning(traceback.format_exc())
                raise ImageConvertionFailed(
                    self._org_fmt, ImageFormat.NDARRAY, ColorOrder.RGB, e
                )
        return img

    def get_bgr_image(self) -> InspectImage:
        """ 画像をRGBカラー化したイメージオブジェクトを返す
        """
        if self.order is ColorOrder.BGR:
            # BGR画像ならばそのまま利用
            img = self
        else:
            # キャッシュの探索
            che = [i for i in self._children if i._order is ColorOrder.BGR]
            if che:
                return che[0]
            # 画像生成
            org = self.get_image()
            if self._order is ColorOrder.GRAY:
                cvt_code = cv2.COLOR_GRAY2BGR
            elif self._order is ColorOrder.RGB:
                cvt_code = cv2.COLOR_RGB2BGR
            elif self._order is ColorOrder.BGRA:
                cvt_code = cv2.COLOR_BGRA2BGR
            elif self._order is ColorOrder.BAYER_BG:
                cvt_code = cv2.COLOR_BAYER_GB2BGR
            elif self._order is ColorOrder.BAYER_RG:
                cvt_code = cv2.COLOR_BAYER_RG2BGR
            else:
                log.warning(f'invalid color order {self._order} in <{self._name}>')
                cvt_code = None
            try:
                buf = cv2.cvtColor(org, cvt_code)
                img = InspectImage(ImageFormat.NDARRAY, buf)
                # キャッシュ情報登録
                img._parent = self
                self._children.append(img)
            except Exception as e:
                log.warning(traceback.format_exc())
                raise ImageConvertionFailed(
                    self._org_fmt, ImageFormat.NDARRAY, ColorOrder.BGR, e
                )
        return img

    def get_url(self) -> str:
        """ 画像のURLを返す
        """
        url = None
        if self._mmap_path:
            # メモリマップ画像の場合は対応するURLを生成
            url = quote(f'mmap://{self._mmap_path}')
            if self._org_fmt == ImageFormat.NDARRAY:
                # NDARRAY画像の場合は画像形状をパラメータに追加
                param_dict = {
                    'width': self.width,
                    'height': self.height,
                    'order': self._order,
                }
        elif self._path:
            # ファイル画像の場合はURLにファイルパスを設定
            url = quote(f'file://{self._path}')

        if url and self._clip:
            # クリップされている場合はクリップ情報を付加
            clip_dict = {
                'clip_x1': self._clip.x1,
                'clip_y1': self._clip.y1,
                'clip_x2': self._clip.x2,
                'clip_y2': self._clip.y2,
            }
            param_dict.update(clip_dict)

        if url and param_dict:
            # パラメータがあればURLに付加
            url += f'?{urlencode(param_dict)}'
        return url

    def show_window(self):
        """ 画像のウィンドウ表示（開発用）
        """
        img = self.get_image()
        cv2.imshow(str(self._path), img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def release_buffer(self):
        if self._src_view:
            # ビューデータを削除
            self._src_view.release()
            self._data.pop(self._org_fmt)
        if self._src_buffer:
            # バッファをクローズ
            self._src_buffer.close(release=True)
            self._src_buffer = None

    # 読み取り専用のパラメータアクセス定義
    @property
    def format(self) -> int:
        return self._org_fmt

    @property
    def data(self) -> int:
        return self._data

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> InspectImage:
        return self._parent

    @property
    def zoom(self) -> float:
        return self._zoom

    @property
    def order(self) -> ColorOrder:
        return self._order

    @property
    def width(self) -> int:
        """ 画像の幅のピクセル数
        """
        return self.get_image().shape[1]

    @property
    def height(self) -> int:
        """ 画像の幅のピクセル数
        """
        return self.get_image().shape[0]

    @property
    def buffer(self) -> BytesIO:
        return self._src_buffer

    @property
    def mmap_path(self) -> str:
        """ メモリマップドファイルへのパス名
        """
        return self._mmap_path

    @staticmethod
    def get_merged(images: Tuple[InspectImage]) -> InspectImage:
        """ 画像をカラー合成したイメージオブジェクトを返す
        Args:
            images:     グレースケール画像のリスト
        Return:
            合成画像
        """
        # 画像生成
        try:
            src_data = []
            for img in images:
                img_data = img.get_image()
                if img_data.dtype == np.uint16:
                    img_data = (img_data // 0x100).astype(np.uint8)
                src_data.append(img_data)
            buf = cv2.merge(src_data)
            new_name = '_'.join(img.name for img in images if img.name)
            img = InspectImage(ImageFormat.NDARRAY, buf, name=new_name)
        except Exception as e:
            imgs_str = ', '.join(str(img._name) for img in images)
            log.warning(f'Failed to merge images ({imgs_str})\n{e}')
            img = None
        return img

    @staticmethod
    def check_data(data) -> ImageFormat:
        """ バッファのデータサイズをチェック
        Args:
            data:       チェックするバイナリ
        Returns:
            ImageFormat.XXXXX:      全データ取得済みの画像フォーマット
            ImageFormat.None:       画像データ取得未完了
        Note:
            バッファ操作でメモリ確保を行わない
        """
        size = len(data)
        format = ImageFormat.check_header(data)
        length = 0

        # PNGフォーマット確認
        if (
            format == ImageFormat.PNG
            and (size >= 24)
            and (data[12:16] == b'IHDR')
        ):
            # PNGファイルサイズの推測（データの存在する範囲で計算）
            length = 8 + 25     # Signature + IHDR
            while length + 8 <= size:
                # 読み出すチャンクがまだ存在するならば
                l, = struct.unpack('> L', data[length:length + 4])
                ctype = data[length + 4:length + 8]
                length += int(l) + 12       # Lenght + ChunkType + CRC (12bytes)

                # 解析用のログ出力を行う場合(デバグ用コード)
                # from logging import DEBUG
                # if log.root.level <= DEBUG:
                #     # デバグ出力有りの場合
                #     if type(ctype) is memoryview:
                #         bdata = ctype.tobytes()
                #     else:
                #         bdata = ctype
                #     log.debug(f'    PNG chunk {bdata.decode()} [{length:,} bytes]')

                if ctype == b'IEND':
                    # 終端なので解析終了
                    break
            if ctype != b'IEND':
                # 終端チャンク未到達ならば足し合わせる
                length += 12

        # BMPフォーマット確認
        elif (
            format == ImageFormat.BMP
            and (size >= 6)
        ):
            # PNGファイルのデータ読み取り
            format = ImageFormat.BMP
            l, = struct.unpack('< L', data[2:6])
            length = int(l)

        # JPEGフォーマット確認(TBD)
        elif format == ImageFormat.JPEG:
            # 暫定でJPEGは常に読み取り完了済みとする
            length = size

        # RAWフォーマット確認
        elif format == ImageFormat.RAW:
            # RAWフォーマット判定時はデータサイズ完了を保証
            length = size

        # 受信サイズの方が大きい場合は読込完了とする
        return format

    def __str__(self):
        if self._name:
            text = f'"{self._name}"'
        else:
            text = 'Image'
        text += f'({self.width}, {self.height}): '
        cached = [
            f'{ImageFormat(fmt).name} '
            f'{len(self._data.get(fmt)):,d} bytes'
            for fmt in IMG_FORMAT_SUF
            if type(self._data.get(fmt)) is bytes
        ]
        if self._order:
            # 基準データ(ndarray)作成済み
            raw = self._data.get(ImageFormat.NDARRAY)
            cached.append(
                f'{ImageFormat.NDARRAY.name}-'
                f'{self._order.name} '
                f'{raw.size:,d} bytes'
            )
        text += ', '.join(cached)
        if self._path:
            try:
                path = Path(self._path).resolve().absolute().as_posix()
            except Exception:
                path = str(self._path)
            # ファイルに紐づいている場合
            text += f', path: {path}'
        return text
