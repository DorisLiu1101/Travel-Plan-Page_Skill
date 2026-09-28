# Golden Viewport & Scenario Manifest

版本：Phase 0 / Round 1  
基線來源：Golden Version 線上正式版與 `golden-ui-spec.md`  
狀態：定義未來截圖入口；本輪不生成或提交截圖檔案。

## 1. 使用邊界

- 本 manifest 只定義 Golden screenshot regression 的 viewport、狀態、裁切目標和斷言入口。
- Golden fixture 含私人旅行內容與 Ledger runtime data。未來截圖及 trace 必須標記為 **INTERNAL / DO NOT PUBLISH**，不得直接進入公開倉庫或公開構建產物。
- 地圖視覺細節由`golden-map-spec.md`補充；公開Demo額外驗證每個目的地國家都擁有獨立總覽和日期路線。
- 所有截圖必須使用同一瀏覽器主版本、device scale factor `1`、同一字型環境、隱藏捲軸，並等待頁面資料與共享狀態穩定。
- 截圖前不得修改 Golden 資料來“適配” viewport；資料變化應產生新的 fixture version。

## 2. Viewport Matrix

| Viewport ID | CSS viewport | DPR | 用途 |
|---|---:|---:|---|
| `mobile-390` | `390 × 844` | `1` | 主要窄屏 Golden baseline |
| `mobile-430` | `430 × 932` | `1` | 較寬手機、`>420px` Ledger 分支 |
| `desktop-1440` | `1440 × 900` | `1` | 720px content 與 1100px route layout |

## 3. 通用捕獲前置條件

每次捕獲必須：

1. 從正式入口重新載入，清除當前頁臨時互動狀態，但不得清除 Golden D1 資料。
2. 等待 Hero、flight cards、route explorer、timeline、rental、todo 和 Ledger 初始化完成；loading error 必須隱藏。
3. 凍結當前時間或記錄 capture timestamp。涉及 flight/rental countdown 的截圖需使用約定 clock fixture，否則只斷言佈局，不斷言數字文字。
4. 將水平 carousel/map scroll 置於場景指定位置。
5. 將頁面 scroll 精確定位到目標容器；區域性截圖優先使用元件 bounding box，頁面截圖用於 section rhythm。
6. 同時儲存：PNG、DOM selector contract、關鍵 computed styles、關鍵 bounds JSON。PNG 不是唯一判定依據。

## 4. 場景定義

以下每個場景都必須分別在 `mobile-390`、`mobile-430`、`desktop-1440` 捕獲，共 27 個基本組合。

| Scenario ID | 頁面狀態 | 目標區域 | 必須可見 | 主要非畫素斷言 |
|---|---|---|---|---|
| `travel-top` | Travel 預設，scroll top 0 | Topbar + Hero + section transition | wordmark、Travel/Ledger nav、eyebrow、title、date | topbar sticky 48px；Hero mobile 188px / desktop 260px；content width |
| `flight` | Travel 預設，carousel 第 1 卡居中 | Flight heading、首卡、dots | flight meta、airport flow、time/status/countdown | card basis、330/350px min-height、14px gap、active dot |
| `trip-overview-country-1` | Route第一個國家，Overview active | Route heading、國家/日期tabs、map container、utility、caption | 第一國asset、全部本國routes/points/legend | mobile content width；desktop route 1100px；map overflow mode |
| `trip-overview-country-2` | Route第二個國家，Overview active | 國家/日期tabs、第二國map container | 第二國asset、全部本國routes/points/legend | 與第一國不串用asset/routes；切換後回到Overview |
| `daily-itinerary` | Golden Day 3 展開，其餘關閉 | Day 3 toggle、daily map入口、schedule、ticket/map button | timeline line/points、time、text、tag/button/ticket | day card 48px left rail；item 82px left padding；expanded detail |
| `rental` | Travel rental 預設 | Heading、deadline、countdown、details、drive tabs | status/deadline/timer、car/stops/price | 24px panel radius；deadline/countdown/details stacking；desktop stops兩列 |
| `todo` | Todo 預設穩定狀態 | Heading、progress、form、list或empty | input、add、existing items/empty | 48px controls、13px radius、54px item、complete/delete states |
| `ledger-home` | `#ledger`，Entry tab active，無 dialog | Header、tabs、members、bill form、bill list | amount/currency/category/date/participants/buttons | 720px app、entry padding breakpoint、6-column participant grid |
| `ledger-stats` | `#ledger-stats`，member cards維持 Golden 預設 open 狀態 | Stats summary、settlement、member cards | transfer rows、metrics、net balances | 17px cards、84px transfer、78px summary、3-column metrics |
| `ledger-dialog` | Ledger Settings dialog open | backdrop + complete dialog | header/close、base currency、common chips、add currency | dialog width/max-height/radius/shadow；390實測352px寬 |

## 5. 每個 Viewport 的必拍清單

### 5.1 `mobile-390` — 390 × 844

- `mobile-390__travel-top.png`
- `mobile-390__flight.png`
- `mobile-390__trip-overview.png`
- `mobile-390__daily-itinerary.png`
- `mobile-390__rental.png`
- `mobile-390__todo.png`
- `mobile-390__ledger-home.png`
- `mobile-390__ledger-stats.png`
- `mobile-390__ledger-dialog.png`

已取得、未來可用於 bounds JSON 的 **[GOLDEN FIXTURE MEASUREMENT]** 摘要：

- Topbar `390×48`；Hero `390×188`；H1 `x18 y132.547 w354 h45.859`。
- 首 flight card `x18 y331 w334 h330`。
- Overview map shell `x18 y944 w354 h266`。
- 首 day toggle `x66 w306 h78`。
- Rental panel `x18 w354 h759.023`。
- Todo form `x18 w354 h48`。
- Ledger entry card `x18 w354 h704.984`；amount controls `h44`；primary `w322 h48`。
- Settings dialog `x19 w352 h423.297`。

### 5.2 `mobile-430` — 430 × 932

- `mobile-430__travel-top.png`
- `mobile-430__flight.png`
- `mobile-430__trip-overview.png`
- `mobile-430__daily-itinerary.png`
- `mobile-430__rental.png`
- `mobile-430__todo.png`
- `mobile-430__ledger-home.png`
- `mobile-430__ledger-stats.png`
- `mobile-430__ledger-dialog.png`

已取得、未來可用於 bounds JSON 的 **[GOLDEN FIXTURE MEASUREMENT]** 摘要：

- Hero `430×188`；H1 computed font-size `51.6px`。
- 首 flight card寬 `374px`、高 `330px`。
- Daily map shell `x18 w394 h296`。
- Golden Day 3 card `x18 w394 h760.008`；detail `x66 w346 h650.117`。
- Schedule map button `h32`；ticket `h58`。
- Rental panel寬 `394px`、高約 `748.445px`。
- Todo form寬 `394px`。

### 5.3 `desktop-1440` — 1440 × 900

- `desktop-1440__travel-top.png`
- `desktop-1440__flight.png`
- `desktop-1440__trip-overview.png`
- `desktop-1440__daily-itinerary.png`
- `desktop-1440__rental.png`
- `desktop-1440__todo.png`
- `desktop-1440__ledger-home.png`
- `desktop-1440__ledger-stats.png`
- `desktop-1440__ledger-dialog.png`

已取得、未來可用於 bounds JSON 的 **[GOLDEN FIXTURE MEASUREMENT]** 摘要：

- Topbar水平 content padding `360px`；Hero `x360 w720 h260`。
- Hero H1 `w620 h62.719`、computed font-size `64px`。
- 首 flight card `w619.195 h350`。
- Route section `x170 w1100`；map shell `x170 w1100 h825.5`。
- Itinerary `x360 w720`；首 toggle `x408 w672 h78`。
- Rental panel `x360 w720 h660.578`。
- Todo form `x360 w720 h48`；Footer `x360 w720 h126`。

## 6. 可選補充場景（不屬於本輪最低完成條件）

後續視覺迴歸可增加：

- `flight-second-card`、`flight-last-card`
- `daily-itinerary-closed`
- `ticket-pending`、`ticket-complete`
- `todo-item-default`、`todo-item-complete`、`todo-empty`
- `ledger-currency-dialog-result`、`ledger-currency-dialog-empty`
- `ledger-members-dialog`
- `ledger-bill-edit`、`ledger-note-inline-edit`
- `loading-error`
- `place-map-sheet`
- `reduced-motion`

這些場景不得替代 27 個基本組合。

## 7. 迴歸判定

- **Computed style：嚴格**。font-size、weight、line-height、letter-spacing、padding、gap、border、radius、shadow、display、grid/flex、overflow、position 必須匹配規範；瀏覽器序列化等價值允許歸一化。
- **Bounds：嚴格但允許亞畫素容差**。整數佈局容差建議 `≤0.5px`，由字型 metrics 導致的文字 bounds 需單獨標註平臺基線。
- **Screenshot：感知差異輔助**。不得因字型抗鋸齒少量差異失敗，也不得用較寬畫素閾值掩蓋真實 padding/radius/layout 變化。
- **動態數字：結構嚴格、文字按 clock fixture**。未凍結時鐘時，對 countdown 只比較 font/layout，不比較數字內容。
- **內容高度：fixture-specific**。只對當前 Golden data version 的頁面總高度和內容驅動高度進行比較。
