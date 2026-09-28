# Map Boundary Matrix — Public Template

狀態：Advanced/legacy Boundary 流程說明；不屬於普通單檔案生成流程。

| Source | Responsibility | Classification | Per-trip editable? | Main guardrail |
|---|---|---|---:|---|
| `index.html` | route section與dialog shell | FROZEN CORE | No | 透過Config隱藏，不刪除DOM |
| `styles.css` | viewport、響應式、route/point/label視覺 | FROZEN MAP STYLE | No | 保持Golden computed result |
| `overview-map.js` | SVG layer composition與package rendering | MAP RENDERER | No | 不含國家/城市特判 |
| `route-ui.js` | Overview/Day、popover、fullscreen互動 | MAP INTERACTION | No | 不從display text猜identity |
| `scripts/generate-map-package.mjs` | boundary投影、routes、labels、Daily bounds/layouts/pins | MAP GENERATOR | No | 相同輸入可復現；無手工geometry |
| `schemas/*.json` | Map source/output與reference約束 | CORE CONTRACT | No | 單次生成不能放寬Schema |
| authorized GeoJSON | 準確國家boundary及source/license | PRIVATE BUILD INPUT / LICENSED SOURCE | Input only | 不復制來源不明資料；不含Trip路線 |
| private canonical Places/Days/Transport | 地點經緯度與語義順序 | PRIVATE BUILD INPUT | Input only | stable ID、typed reference、one source |
| `travel-data.json` | compiler輸出的Renderer檢視 | GENERATED TRIP DATA | Generated only | 不人工拼接canonical與region shape |
| generated region JSON | routes、projected places、labels、daily layouts/bounds | GENERATED TRIP DATA | Generated only | 不由Agent手調 |
| generated `*-base.svg` | Golden風格國家底圖 | GENERATED TRIP ASSET | Generated only | 輪廓來自boundary；保留source/license metadata |
| navigation query / private address | 地點互動目標 | PRIVATE TRIP VALUE | Yes | 僅進入使用者Trip；釋出前審查 |
| pure country base cache | 無Trip內容的boundary/style輸出 | PUBLIC-SAFE CACHE | Reusable | 不得包含地點、路線、日期、地址或query |
| private Golden map package | 私人路線、座標、queries、assets | PRIVATE FIXTURE | No | 永不復制到Public Template |

## Reusable Core

- SVG layer renderer；
- Frozen route/point/label/legend visual grammar；
- Overview/Day切換；
- place/transport popover；
- fullscreen與responsive shell；
- deterministic projection、route、label和Daily bounds generation；
- icon registry和互動事件。

## Per-trip source and generated output

使用者或Agent只提供/確認：

- `trip.primaryDestinationCountries`；
- canonical Places的country code與geo；
- Day/Transport/Place訪問順序與stable references；
- 獲授權的boundary source；
- navigation query與特殊地點option。

Generator派生：

- country base SVG；
- projected x/y；
- route paths和顏色分配；
- label placement；
- Daily layouts、bounds和transport pins；
- Map Package metadata與source/license記錄。

單次生成不允許修改Core或手調這些派生geometry。若輸出不能滿足任務，先報告generator缺口，再在獨立框架維護任務中修改和迴歸。
