# **<font color="#0068B7">Roxy AI</font>** API

**<font color="#0068B7">Roxy AI</font>** の検査サーバを利用する Python 用の API です。


テストサンプルを実行するには以下の準備が必要となります。

1. Python仮想環境の構築
1. 検査サーバの起動
1. テストの実行

動作確認テストの方法には以下の二つの方法を用意しています。

- pytest によるモジュール単体テスト実行
- サンプルアプリによる検査実行

また Visual Studio Code の開発環境を用意しています。

- _Visual Studio Code_ 環境の整備

---
---

## Python仮想環境の構築と有効化

初回の仮想環境の構築には仮想環境構築スクリプト `install_win.bat` を実行します。

一度仮想環境が構築されると、Visual Studio Code (VSC) のワークスペースは自動で仮想環境を設定します。
VSC以外で仮想環境を有効にするには `env/Script/activate` を実行します。

>  ※ Python 仮想環境の詳細は Python の[公式マニュアル](https://docs.python.org/ja/3.7/library/venv.html) を参照ください。


## 検査サーバの起動

[Inspection-Server マニュアル](https://roxy-ai-support.atlassian.net/wiki/spaces/RAD/pages/155517128) を参照ください。

## テストの実行

### 単体テスト pytest のコマンドライン実行

コマンドライン上で仮想環境を有効にした状態で `pytest` を実行します。

実行例

```Shell
(env) c:\XXXXX\roxy-ai-dev\python\roxyai-api>pytest
===================================================== test session starts =====================================================
platform win32 -- Python 3.7.7, pytest-5.4.3, py-1.9.0, pluggy-0.13.1 -- c:\RoxyAI\roxy-ai-dev\python\roxyai-api\env\scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\RoxyAI\roxy-ai-dev\python\roxyai-api, inifile: pytest.ini, testpaths: tests
collected 34 items
(中略)
PASSED2020-07-02 17:08:37,240 INFO <2820> [connection]
---- close connection: 127.0.0.1:53739 -> 127.0.0.1:6945
2020-07-02 17:08:37,240 DEBUG <2820> [connection] release lock 1652236766600


================================================ 34 passed in 77.59s (0:01:17) ================================================ 
```

### サンプルアプリの実行

サンプルの検査実行スクリプト `sample/inspect_sample.py` を実行します。

```shell
(env) C:\XXXXX\roxy-ai-dev\python\roxyai-api>python sample\inspect_sample.py

Roxy AI の検査を実行します。
  モデルパス： C:/XXXXX/roxy-ai-dev/python/roxyai-api/sample/product/Product1/fixed_model
  画像パス： C:/XXXXX/roxy-ai-dev/python/roxyai-api/sample/product/Checker
  画像枚数： 5枚
  繰り返し： 1回
ERR: Denied open additional product (0x13)

===== 検査開始 =====
2021-03-03 17:15:29.287783 [NOK]: org_image[JPEG], cached JPEG: 4,108 bytes
  NOK (  64,    0)-( 192,  128) 0.949533, label=1
  NOK (   0,   64)-( 128,  192) 0.938207, label=1
  NOK (   0,    0)-( 128,  128) 0.772167, label=1
  NOK (  64,   64)-( 192,  192) 0.934744, label=1
（中略）
  NOK ( 320,    0)-( 448,  128) 1.000000, label=1
  NOK ( 384,  256)-( 512,  384) 1.000000, label=1
  NOK ( 320,  256)-( 448,  384) 1.000000, label=1
2021-03-03 17:15:29.519165 [OK]: org_image[JPEG], cached JPEG: 95,249 bytes

===== 検査終了 =====
 検査枚数： 5 枚
 検査時間： 55.45 ms／枚
```

検査サンプルの実行時に検査対象のモデルや、検査画像のフォルダ指定も可能です。

- モデルは `-m` の後ろに「完成モデル」のフォルダパスとして指定します
- 検査画像はコマンドの最後にのフォルダまたは画像のパスを指定します

```shell
# 基本の使用方法
inspect_sample.py -m {モデルフォルダ} {イメージフォルダ}

# 実際の使用例
inspect_sample.py -m C:\RoxyAI\roxy-ai-release\product\テスト\テスト\model\fixed C:\RoxyAI\roxy-ai-release\product\テスト\テスト\img\test
```

詳細な使い方はコマンドヘルプを参照してください。

```shell
inspect_sample.py -h
```


## Visual Studio Code 環境の整備

_Visual Studio Code (VSC)_ をインストールして、拡張機能 `Python` を有効にします。

[ファイル]-[ワークスペースを開く] で `.vscode\roxyai-api.code-workspace` を開きます。


### 単体テストの実行

[F1] で Discover Tests を選択すると単体テストアイコン（フラスコ）が左端のバーに追加されます。

アイコンをクリックすると Test Exploler が開き、各単体テストを自由に実行できるようになります。

単体テストスクリプトにエラーがあるとテストが表示されなくなります。
その場合には、下部の[出力]タブで [Python Test Log] を開き、エラーの内容を確認して修正します。

### サンプルプログラムの実行

サンプルプログラムのコード（ `sample\inspect_sample.py` など）を開いた状態で、デバグ実行の対象として `Python: Current File (roxyai-api)` を選択し、[F5] キーなどでデバグ実行することでサンプルを実行できます。

---
---

## ライセンス

本プロジェクト（**<font color="#0068B7">Roxy AI</font>** API） は _[APACHE LICENSE 2.0](http://www.apache.org/licenses/)_ に基づいて公開しています。（参考：[APL2.0日本語訳](https://ja.osdn.net/projects/opensource/wiki/licenses/Apache_License_2.0)）