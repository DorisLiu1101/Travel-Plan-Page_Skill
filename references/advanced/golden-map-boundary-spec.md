# Golden Map Specification — Public Template Edition

狀態：Standard Generator Map Guardrail  
範圍：凍結地圖視覺語言、Renderer層次和互動；不公開私人Golden目的地的路線、日期、座標、query或assets。

## 1. Product Direction

地圖採用 **deterministic two-mode generation**。Builder 自動選擇 `country-golden` 或 `generic-diagram`，使用者與 Agent 均不得手動設計第三種模式。國家模式從獲授權的真實國家 Boundary 與地點座標生成；通用模式複用唯一凍結示意底圖並按確定性佈局分散地點。兩種模式均由同一 Renderer 以 Golden Map Style 呈現。

當前標準能力必須提供：

- GeoJSON country-boundary輸入與source/license記錄；
- lat/lng projection；
- 按canonical Place/Transport/Day引用生成route；
- 確定性的預設label layout；完整collision solver仍是獨立框架增強；
- Overview 與 Daily 共用完整地圖視口；
- 相同輸入產生可復現Map Package。

單次Trip生成不得修改`overview-map.js`、`route-ui.js`、HTML或CSS，也不得手畫國家輪廓、route path或pin座標。Renderer/Core能力不足時應停止並報告為獨立框架問題。

## 2. Layer Model

| Layer | Responsibility | Current public source |
|---|---|---|
| MAP SHELL | section、tabs、viewport、utility、fullscreen dialog | `index.html`, `styles.css` |
| MAP RENDERER | SVG layer composition、route、point、label、legend | `overview-map.js` |
| MAP STYLE | stroke、marker、type、surface、popover | JS SVG attributes + `styles.css` |
| MAP SOURCE DATA | country codes、canonical Places、Days、Transport order | private canonical input; compiled view in `travel-data.json` |
| MAP GENERATOR | auto mode、projection/schematic layout、base SVG、routes、labels、daily layouts | `scripts/build-map.mjs` |
| GENERATED MAP DATA | country packages、paths、projected places、daily layouts | generated region JSON + assets |
| MAP INTERACTION | Day切換、place/transport popup、Google Maps、fullscreen | `route-ui.js` |
| GENERATED TRIP ASSET | authorized region artwork與derived geometry | `assets/` + generated Map Data |

Source Data與Generated Trip Asset可以按旅行更換；Map Style、generator contract和可觀察互動未經批准不得改變。

## 3. Canvas and Surface

### `[FROZEN MAP STYLE]`

- SVG：`display:block; width:100%; height:auto`，保持viewBox比例縮放。
- viewport：`border-radius:12px`、`1px solid var(--line)`、background `#f6f6f1`。
- Overview 與 Daily 保持完全相同的 canvas、viewBox、scale、extent 與 region 位置。
- map utility使用muted `12px`文字、兩端對齊和無重灌飾button。
- fullscreen沿用原dialog shell；Overview與Daily保持各自尺寸規則。

### `[GENERATOR CONTRACT]`

- 每個標準Map Package使用`1448×1086`、`4:3` canvas。
- projection、point、label、route 和 pin 使用同一 canvas 座標系；Overview 與 Daily 固定共用該 canvas 的完整 bounds。

## 4. Region Artwork

### `[FROZEN MAP STYLE]`

- 淺奶油紙面；
- 低飽和灰綠region輪廓；
- 淡藍水體與剋制地理文字；
- 極淡等高線/地形線；
- 少量山脈、樹木或目的地相關插畫；
- 不讓底圖搶過route和label的資訊層級。

### `[GENERATED TRIP ASSET]`

region shape、海岸線、湖泊和全部地理位置來自獲授權的boundary/geodata，並由Core generator投影。山脈、樹木、紋理等裝飾層來自公共安全的Frozen style assets或確定性生成規則，不從私人地圖複製。

公開Demo的`assets/maps/aster-isles-base.png`與`assets/maps/mist-coast-base.png`是原創生成的虛構國家底圖。它們只作為fixture保留，不對應任何真實國家，也不能作為真實目的地的boundary來源。

## 5. Route

### `[FROZEN MAP STYLE]`

- SVG path `fill:none`。
- `stroke-linecap:round`、`stroke-linejoin:round`。
- 無arrow，無dash。
- 每條geometry繪製兩層：主色`stroke-width:7`；上層白色`stroke-width:2`、`stroke-opacity:.22`。
- 預設六色palette：`#397dc1`、`#e77e22`、`#618344`、`#209aaa`、`#8865a5`、`#df6185`。
- Overview顯示全部route；Daily只保留selected route，不使用inactive opacity。

### `[TRIP MAP DATA]`

- day與color assignment；
- 每日一條或多條SVG path；
- route是否往返、分支或中斷；
- geometry與地點的地理關係。

Route path由generator根據有序的canonical Place/Transport引用生成。Agent不得直接編輯path，也不得透過截圖估算或複製另一位使用者的custom map。

## 6. Place Point

### `[FROZEN MAP STYLE]`

- Overview marker：`r=10.5`、per-place fill、`#fafaf4` stroke、`stroke-width=2.5`。
- Daily可互動點疊加透明hit target與route-color visual point。
- visible point有白邊；hover/focus/expanded呈現同心ring反饋。
- hit target必須保持適合觸控，不得縮小到可見圓點大小。

### `[TRIP MAP DATA]`

- place ID、geo和顏色語義；
- Day layout中顯示哪些places；
- 起點、終點、途經點、換乘點等role；
- popup query和可選地點。

## 7. Labels and Heading

### `[FROZEN MAP STYLE]`

- family：`'Times New Roman', 'Kaiti SC', STKaiti, KaiTi, 'Songti SC', serif`。
- weight：`700`。
- fill/stroke：`#092653`。
- stroke width：`0.4`，paint order為stroke再fill。
- 多行label預設line rhythm：`31` canvas units。
- 支援per-label font size、x/y和`start | middle | end` anchor。
- Heading預設`40/700`，使用相同mixed serif/Kaiti語言。
- geographic annotation使用低飽和藍色italic serif，可有多行。

### `[TRIP MAP DATA]`

地點文字、語言、字號例外、heading copy和annotation內容由該Trip提供；x/y、anchor與預設字號由projection/renderer的確定性預設佈局派生。當前不承諾完整collision solver。必要的明確layout override仍屬於Trip Data，但只能在獨立地圖精修任務中批准，不能在標準首版中臨時手調。

## 8. Legend

### `[FROZEN MAP STYLE]`

- transparent，無獨立卡片背景；
- serif `23/700`、深藍文字；
- route-color round swatch，長度`28` canvas units、width`5`；
- default row step `43` canvas units；
- 日期由route對應Day讀取，使用簡潔month/day顯示。

legend位置由generator按canvas與內容數量確定；明確override屬於Generated Trip Layout。

## 9. Overview and Daily Composition

多國旅行首先顯示由`routeMap.regions[]`生成的國家標籤。切換國家必須同時切換base artwork、routes、places、annotations、legend和dailyLayouts；Core不得包含國家名稱特判。

Overview layer order：

1. region artwork；
2. all route paths；
3. markers；
4. place labels；
5. geographic annotations；
6. heading；
7. date legend。

Daily composition：

1. 複用同一region artwork；
2. 只保留selected route；
3. 移除Overview markers、geographic annotations和legend；
4. 只保留dailyLayout指定labels並應用其x/y/anchor；
5. 在SVG上疊加HTML place buttons和transport pins。

Daily 不得按當天地點重新計算 bounds，不得 zoom-to-route、fitBounds、裁切或改變 transform；只切換當天路線、必要地點、交通 pins 與相關標籤的可見性。

## 10. Transport Icon

### `[FROZEN MAP STYLE]`

- white/route-color rounded square；
- desktop約`28px`，窄屏約`24px`；
- subtle shadow、thin line icon；
- expanded：route-color background + white icon；
- 與route關聯但不嵌入SVG path。

當前icon registry支援drive、train/rail、cable-car、hike/walk、boat/ferry、rental-car。未支援的真實交通型別使用已有安全fallback並記錄框架缺口；增加Core圖示必須作為獨立框架維護任務並保持視覺語法。

Pin位置由generator根據route/nearby points派生；彈層內容透過Transport或Day Item stable IDs關聯，不得使用schedule array index。插入/重排顯示專案不能靜默改變pin identity。

## 11. Place and Transport Popovers

### `[FROZEN MAP STYLE]`

- fixed positioning並限制在viewport邊緣`8px`以內；
- white surface、現有border/radius/shadow；
- place popup包含role、title、optional choices、iframe、external link和network note；
- transport popup按配置順序列出time/type/text；
- active pin使用expanded視覺。

### `[FROZEN BEHAVIOR]`

- 點選同一pin可關閉；
-點選其他pin替換當前popover；
- close、Escape、outside click/focus可以關閉；
- 需要時恢復opener focus；
- external link使用新視窗及`noopener noreferrer`；
- fullscreen克隆當前map visual state。

## 12. Responsive Rules

- route section在寬屏使用最多約`1100px`的視覺範圍；
- 當前CSS `>=1000px`取消map canvas最小寬度；
- Overview 與 Daily 在 mobile 均保持同一整圖範圍，並避免頁面整體橫向溢位；
- popover每次開啟、resize或scroll後重新定位；
- map dialog中canvas保持足夠寬度檢視細節。

任何selector重新命名必須保持這些computed results，不得藉機重做佈局。

## 13. Standard Map Workflow

1. 從完整資料中確認`trip.primaryDestinationCountries`；出發地或純轉機國家預設排除。
2. 在canonical Place目錄中保留每個已知地點的country code與經緯度；歧義地點進入第二輪確認，不降級成泛化城市點。
3. 為每個目的地國家取得可授權使用的準確GeoJSON boundary，並記錄source/license；不要抓取或複製來源不明的地圖。
4. 確保Day Item、Transport與Place使用stable IDs表達訪問順序與關係。
5. 執行：

   ```bash
   node scripts/generate-map-package.mjs \
     --boundary /absolute/path/to/authorized-country-boundary.geojson \
     --data /absolute/path/to/private/canonical-travel-data.json \
     --country <ISO2> \
     --out assets/maps/<country>-region.json \
     --source <BOUNDARY_SOURCE_OR_URL> \
     --license <BOUNDARY_LICENSE>
   ```

6. Generator輸出固定`1448×1086`底圖、投影地點、雙stroke routes、labels、Overview與Daily layouts及pins；所有日期共用完整地圖 bounds。
7. 用 `scripts/compile-travel-data.mjs` 合併 private canonical input、`trip-config.json` 和每個 generated region package，輸出 Renderer 實際讀取的 `travel-data.json`；不手工拼接欄位。
8. 私人地址/query只進入該使用者的Trip輸出；公共cache只允許儲存不含Trip地點與路線的country base。
9. 使用輕量 validator 檢查 Boundary、place/day/reference 完整性與核心檔案。
10. 檢查國家標籤數量、每個國家Overview、每個Day、popover、fullscreen和三個baseline viewports。

若標準生成器不能表達某個目的地，記錄框架缺口並停止；不要在該使用者的生成任務中區域性改Renderer。

## 14. Privacy Contract

- 私人Golden目的地的實際route、dates、place list、coordinates、queries和assets不屬於Public Template。
- 本公開spec只保留視覺引數和Renderer規則。
- 使用者新地圖預設也是private Trip Asset；只有獲得明確授權後才可釋出為Demo。
- 不得根據公開spec嘗試還原被移除的私人Golden map。

## 15. Acceptance

新地圖可以有不同region與內容，但必須驗證：

- route double stroke、palette、round caps/joins；
- marker、label、heading、legend層級；
- Overview/Daily顯示規則；
- place與transport互動；
- responsive map shell與fullscreen；
- 每個目的地國家都有且只有一個對應Map Package，國家標籤切換不會串用其他國家的asset或route；
- boundary來源/許可已記錄且國家輪廓不是手畫近似；
- canonical geo Places投影在正確國家/區域，已知地點沒有被泛化城市點吞併；
- Overview 路線順序與行程一致，Daily 只切換路線與相關地點，不改變整圖視口；
- Day/Place/Transport使用stable ID引用，沒有schedule index或display-text identity；
- 無私人Golden asset/query/date/route殘留。
