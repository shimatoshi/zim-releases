# zim-releases

zimmaker が生成した ZIM アーカイブ置き場。Kiwix Android/Desktop で閲覧可能。

## カタログ

| tag | 公開日 | URL |
|---|---|---|
| `www-ha-shotoku-ac-jp-20260416` | 2026-04-15 | [release](https://github.com/shimatoshi/zim-releases/releases/tag/www-ha-shotoku-ac-jp-20260416) |
| `tansuigyo-net-20260416` | 2026-04-15 | [release](https://github.com/shimatoshi/zim-releases/releases/tag/tansuigyo-net-20260416) |
| `zakonomizube-web-fc2-com-20260416` | 2026-04-15 | [release](https://github.com/shimatoshi/zim-releases/releases/tag/zakonomizube-web-fc2-com-20260416) |
| `info-cern-ch-20260415` | 2026-04-15 | [release](https://github.com/shimatoshi/zim-releases/releases/tag/info-cern-ch-20260415) |

## 取得方法

```bash
# 単一ファイル
gh release download <tag> --repo shimatoshi/zim-releases
# 分割ファイルの自動結合（zimmaker同梱）
python release.py fetch <tag> --outdir .
```
