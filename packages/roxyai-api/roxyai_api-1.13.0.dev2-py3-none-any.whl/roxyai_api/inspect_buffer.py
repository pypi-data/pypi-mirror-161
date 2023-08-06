# (c) Roxy Corp. 2020-
# Roxy AI Coordinator
from __future__ import annotations
from typing import Union
from pathlib import Path
from logging import getLogger
from os import environ, getpid
from mmap import mmap, ACCESS_READ, ACCESS_WRITE
from shutil import rmtree


log = getLogger(__name__)


class _RingBufferSet():
    def __init__(self):
        """ リング式バッファセット
        """
        self.list: list[InspectBuffer] = []
        self.index: int = 0

    def get_next(self) -> InspectBuffer:
        """ 次のバッファを取得
        """
        self.index = (self.index + 1) % len(self.list)
        return self.list[self.index]

    @property
    def buffer(self) -> InspectBuffer:
        """ 現在のバッファを取得
        """
        return self.list[self.index]


class InspectBuffer():
    _root_path = Path(environ.get('TEMP')) / 'roxyai_api_buffer' / str(getpid())

    # バッファ名に対応するリングバッファ辞書
    _name_dict: dict[str, _RingBufferSet] = {}

    @classmethod
    def clean(cls):
        """ Roxy AI のメモリマップドファイルを全て削除する
        Note:
            ロックされているファイルは無視
            起動時に1度だけ実行する想定
        """
        if cls._root_path.parent.exists():
            for path in cls._root_path.parent.iterdir():
                try:
                    if path.is_dir():
                        rmtree(str(path))
                    else:
                        path.unlink()
                except Exception as e:
                    log.info(
                        f'{cls.__name__}: failed to clear {path}: {e}'
                    )

    @classmethod
    def release_all(cls):
        """ 管理しているバッファを全て開放する
        """
        for name, lst in cls._name_dict.items():
            for i, buf in enumerate(lst.list):
                try:
                    buf._release()
                except Exception as e:
                    log.warning(
                        f'{cls.__name__}: failed to release buffer '
                        f'"{name}:{i}"\n{e}'
                    )
        cls._name_dict.clear()

    @classmethod
    def alloc_set(cls, set_name: str, set_size: int, buffer_size: int) -> InspectBuffer:
        """ バッファセットをメモリマップ上に取得する
        Args:
            set_name:       バッファセット名
            set_size:       セットで作成するバッファ数
            buffer_size:    バッファサイズ[bytes]
        Returns:
            InspectBuffer:   作成した先頭のバッファインスタンス
            None:            バッファの作成失敗
        """
        buf = None
        if set_size < 1:
            ValueError(f'{cls.__name__}: number must be greater than 0')

        buf_set = cls._name_dict.get(set_name)
        if buf_set:
            # 既に同名のバッファセットを生成済み
            if (buf_set.buffer.size != buffer_size):
                log.warning(
                    f'{cls.__name__}: {set_name}:{buf.id} size is different from {buffer_size}'
                )
            buf = buf_set.get_next()
        else:
            try:
                buf_set = _RingBufferSet()
                for index in range(set_size):
                    # バッファの確保
                    file_name = f'{set_name}_{index:03d}'
                    path = cls._create_temp_file(file_name, buffer_size)
                    # 書き込み可能でバッファを取得
                    buff = cls(path, read_only=False)
                    buf_set.list.append(buff)
                # バッファセットを登録
                cls._name_dict[set_name] = buf_set
                buf = buf_set.buffer
            except Exception as e:
                log.warning(
                    f'{cls.__name__}: falied to allocate buffer, '
                    f'name: "{set_name}", nubmer: {set_size}, '
                    f'size: {buffer_size:,d}\n{e}'
                )
        return buf

    @classmethod
    def get_next_buffer(cls, set_name) -> mmap:
        """ 次のバッファを取得する
        Args:
            set_name: バッファ名
        Returns:
            InspectBuffer: 次のバッファインスタンス
            None:          バッファがない
        """
        ret = None
        if cls._name_dict.get(set_name):
            lst = cls._name_dict[set_name]
            cls._name_index[set_name] = 0
            if len(lst) > 0:
                ret = lst.pop(0)
        return ret

    @classmethod
    def _create_temp_file(cls, name: str, size: int) -> Path:
        """ メモリマップドファイル用のファイルを生成する
        Args:
            name:   ファイル名
            size:   ファイルサイズ[bytes]
        Returns:
            Path:   ファイルパス
        """
        try:
            # 格納ディレクトリ作成
            cls._root_path.mkdir(parents=True, exist_ok=True)
            path = cls._root_path / name
            if path.exists():
                log.warning(f'{cls.__name__}: file already exists: {path}')
            # Windowsは空のファイルを利用できないので適当なファイルを作成
            with open(path, 'wb') as fd:
                fd.write(b'\0' * size)
                fd.flush()
        except Exception as e:
            log.warning(
                f'{cls.__name__}: failed to allocate buffer, '
                f'name: "{name}", size: {size:,d}\n{e}'
            )
            raise
        return path

    def __init__(self, path: Union[str, Path], read_only: bool = True):
        """ 検査用のバッファ管理
        Args:
            path:       メモリマップドファイルパス
            read_only:  読み取り専用か
        Notes:
            メモリマップドファイル上にバッファを確保する
        """
        self._path = Path(path).resolve()

        self._name = self._path.name[:-4]
        self._id = int(self._path.name[-3])

        self._fd = None
        self._mm = None
        self._size = None
        self._read_only = read_only

        # インスタンス生成時にバッファ獲得
        self._mmap()

    def _mmap(self) -> bool:
        """ バッファをメモリマップ上に取得する
        Returns:
            True:  獲得成功
            False: 獲得失敗
        """
        try:
            # ファイルオープン
            self._fd = open(self._path, 'r+b')
            if self._read_only:
                access = ACCESS_READ
            else:
                access = ACCESS_WRITE
            # メモリマップ割り当て(確保メモリサイズはファイルサイズ)
            self._mm = mmap(self._fd.fileno(), 0, access=access)
            self._size = self._mm.size()
        except Exception:
            log.warning(f'{self}: failed to allocate buffer')
            raise
        log.debug(f'{self}: allocated buffer')

    def _release(self):
        """ バッファを開放する
        """
        # メモリマップ開放
        try:
            if self._mm.closed:
                self._mm.close()
        except Exception as e:
            log.warning(f'{self}: failed to close mmap: {e}')
        self._mm = None
        # ファイルクローズ
        try:
            if self._fd and (not self._fd.closed):
                self._fd.close()
        except Exception as e:
            log.warning(f'{self}: failed to close mmap: {e}')
        self._fd = None

    def get_next(self) -> InspectBuffer:
        """ 次のバッファを取得する
        Returns:
            InspectBuffer: 次のバッファインスタンス
            None:          次のバッファがない
        Note:
            リングバッファのセットで確保した場合のみ利用可能
        """
        buf = None
        buf_set = self._name_dict.get(self._name)
        if buf_set:
            buf = buf_set.get_next()
        else:
            log.warning(f'{self}: not found buffer set {self._name}')
        return buf

    @property
    def closed(self) -> bool:
        """ メモリマップドファイル開放済みか
        """
        return (not self._mm)

    @property
    def mmap(self) -> mmap:
        """ メモリマップドファイル
        """
        return self._mm

    @property
    def size(self) -> int:
        """ バッファサイズ
        """
        return self._size

    @property
    def path(self) -> Path:
        """ メモリマップのファイルパス
        """
        return self._path

    def __str__(self) -> str:
        text = f'<{self.__class__.__name__} '
        text += f'{self._name}:{self._id} '
        text += 'RO> ' if self._read_only else 'RW> '
        text += f'({self._size:,d} bytes)'
        return text


if __name__ == '__main__':
    import numpy as np
    from timeit import timeit
    from shutil import copyfileobj
    InspectBuffer.clean()
    mm = InspectBuffer.alloc_set('test', 2, 512 * 1024)
    print(mm)
    dt = np.dtype('uint8')
    dt = dt.newbyteorder('<')
    dst_np = np.frombuffer(mm.mmap, dtype=dt, offset=0)
    src_np = dst_np.copy()
    m2 = mm.get_next()

    # コピースピードの確認
    def test_func1():
        # データサイズが小さい時（～500KBくらい）には最速
        dummy_np = dst_np.copy()

    def test_func2():
        # test_func3より若干遅い
        mm.mmap[:] = dst_np.data[:]

    def test_func3():
        # データサイズが大きい時（1MB～）には最速
        copyfileobj(mm.mmap, m2.mmap)

    def test_func4():
        m2.mmap[:] = mm.mmap[:]

    result1 = timeit(test_func1, number=10)
    print(f'np.copy(): {result1}')
    result2 = timeit(test_func2, number=10)
    print(f'np.copy(): {result2}')
    result3 = timeit(test_func3, number=10)
    print(f'np.copy(): {result3}')
    result4 = timeit(test_func4, number=10)
    print(f'np.copy(): {result4}')
    pass
