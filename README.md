# Jiffy75 LP 縦置きスタンド "Silver Spine"

![hero](images/hero.png)

JezailFunder **Jiffy75**（左右分割・ロープロファイル 75%）の左右ハーフを、
**短辺（127.7 mm側）を下にして背中合わせ**に立てて収納するスタンドです。
ケース裏面どうしの間に薄い「背骨（スパイン）」を1枚通し、キー面は外側を向きます。
寸法はすべて **白銀比（1 : √2）** の数列から決め、Apple製品のような削り出しの塊感を狙いました。

| キーボードを入れた状態 | 正面（背中合わせ） |
|---|---|
| ![](images/with_keyboard.png) | ![](images/front.png) |

| 上面 | スペースグレイ（色違いの例） |
|---|---|
| ![](images/top.png) | ![](images/space_gray.png) |

## STL

- [`stl/jiffy75_stand.stl`](stl/jiffy75_stand.stl): 70.7 × 141.4 × 70.7 mm（スパイン頂部まで）、約120 cm³、watertight確認済み

## 対象キーボードの寸法（調査値）

| 項目 | 値 |
|---|---|
| 左ハーフ | 156.4 × 127.7 mm |
| 右ハーフ | 176.1 × 127.7 mm |
| ケース厚 | 約 11 mm |
| キートップまでの高さ | 約 20〜23 mm |
| 重量 | 約 0.87 kg（左右合計） |

公式の厚み値は見つからなかったため、片側の溝幅は余裕を持たせて **25 mm** にしました。

## 白銀比によるデザイン

すべての主要寸法は `S(k) = 200 / √2^k` の数列から取っています。

| k | 1 | 2 | 3 | 6 | 7 | 8 | 10 | 11 | 13 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|
| mm | **141.4** | **100** | **70.7** | **25** | **17.7** | **12.5** | **6.25** | **4.42** | **2.21** | **1.56** |
| 用途 | 全長 | スパイン長 | 全幅・スパイン高 | 溝幅 | 台座高 | 溝深さ・角R・脚径 | スパイン厚 | 上面エッジR | 底面の影ライン | 溝入口の面取り |

- 全長 : 全幅 = 2 : 1 = (√2)²
- スパイン長 : 全長 = 1 : √2
- スパイン高 = 全幅 = 70.7 mm（正面から見ると台座とスパインが正方形に収まる）
- 全幅 : 台座高 = 4 : 1 = (√2)⁴

## Appleらしさのための工夫

- **一枚の薄いブレード**: 厚さ 6.25 mm、上端と両端は半円で丸めた背骨が、2枚のケースを分ける
- **スクワークル（超楕円）コーナー**: 平面の角を曲率が連続する iPhone / Mac 風の角に
- **上面の丸いリム（R4.42）**: トレイ全体が一つの塊から削り出したように見える
- **底面の45°面取り（2.21 mm）**: 机との間に細い影が落ち、浮いて見える。サポート不要
- **溝入口の面取り**で差し込みがなめらか
- 底面に Ø12.5 × 深さ1 mm の凹み4か所: ゴム足やフェルトを貼る位置

## 印刷のおすすめ

- 向き: 底面をベッドに置く（そのままの向き）。**サポート不要**
- サイズ: 70.7 × 141.4 mm（ほぼすべての3Dプリンターで印刷可能）
- 素材: シルバー系のシルクPLA、または マットPLA（ホワイト / スペースグレイ）
- 設定例: 0.2 mm レイヤー、壁 3〜4周、インフィル 20〜30%（ジャイロイド）。スパインは壁だけでほぼ埋まるので十分な強度になります
- 台座が軽いので、底にゴム足を貼るのがおすすめです
- 仕上げ: 上面をサンディング → サーフェサー → シルバー塗装にすると、アルマイト調に近づきます

## カスタマイズ

`src/stand.py` の先頭にある定数を変えて再生成できます。

```bash
pip install trimesh manifold3d scipy numpy
python3 src/stand.py
```

キートップが高くて入らない場合は `CH_W` を大きく、ぐらつく場合は `FIN_TOP` を `S(2)=100` に、`CH_DEPTH` を `S(7)=17.7`・`H` を `S(6)=25` にしてください（どれも白銀比の数列内の値です）。

プレビュー画像の作り方は `preview/`（three.js + Playwright）を参照してください。

## 参考にした寸法情報

- [OZO Keyboards – Jiffy75 Wireless Split Low-Profile](https://www.ozokeyboards.com/products/jiffy75-wireless-split-low-profile-mechanical-keyboard)
- [KeyLab DB – Low-Profile Split Keyboards Compared](https://www.keylabdb.com/en/blog/low-profile-split-keyboards-compared)
- [green-keys – Jiffy75 (SP75) Advance Review](https://green-keys.info/en/jezailfunder-jiffy75-sp75-advance-review%EF%BD%9Ceasy-to-use-left-right-split-75-keyboard-with-low-switching-costs/)
- [Keyboard Builders' Digest – Jiffy75 review](https://kbd.news/Jiffy75-review-2818.html)
