# Golden Map Specification: Fixed Template Edition

狀態：普通生成唯一地圖規範。

## 1. 核心目標

普通 Agent 不生成地圖背景，也不繪製國家、城市或行政區輪廓。所有旅行地圖由十張固定底圖之一與固定 SVG 疊加層組成。不同旅行只改變地點的相對位置、訪問順序、每日路線和文字內容。

地圖是模板化行程示意圖，不代表真實比例或精確地理邊界。

## 2. 凍結底圖

模板清單位於 `assets/maps/templates/manifest.json`。十張底圖統一使用 `1448 x 1086`、4:3 畫布，並固定紙張紋理、低飽和配色、地形、水體、山林、城市線稿、構圖留白及每張模板的路線安全區域。Manifest 的執行時路徑全部指向 WebP。底圖自身不得包含旅行標題、圖例、路線、節點或地點標籤。

普通生成不得修改、覆蓋或重新生成底圖。

## 3. 自動模板選擇

- 緊湊/高密度：跨度小於 45 km，或至少 6 個地點且平均最近距離小於 12 km，候選池為 `urban-radial` / `compact-basin` / `upland-basin`；
- 分離簇/長跳轉：路線連通分量多於 1，或最長路段超過 160 km 且它與路段中位數的比值大於 2.8，候選池為 `island-archipelago` / `river-highland` / `broad-riverland`；
- 南北向：南北跨度大於東西跨度的 1.1 倍，候選池為 `coastal-region` / `radial-watershed` / `compact-basin`；
- 東西向：東西跨度大於南北跨度的 1.3 倍，候選池為 `inland-alpine` / `wide-valley` / `broad-riverland`；
- 其餘均衡路線：候選池為 `inland-alpine` / `river-highland` / `upland-basin` / `compact-basin` / `broad-riverland`。

Builder 按上述順序確定候選池，再對區域、地點 ID 和路線順序組成的旅行簽名做穩定雜湊，從池內選出一張；同一輸入的結果始終相同。Manifest 的 `selectionRole` 是維護說明，不是 Builder 直接解析的規則。

`trip-data.json > map.mapMode` 在普通生成中固定為 `template-auto`，`map.templateId` 固定為 `auto`。Builder 生成的 `routeMap.regions[].mapMode` 為 `frozen-template`；這是派生輸出，不得寫回輸入的 `map.mapMode`。顯式模板 ID 只允許在使用者後續 DIY 時使用。

地圖按目的地分割槽，而不是按完整航班鏈路分割槽。出發國、返程終點國和純轉機國家不在 `trip.primaryDestinationCountries` 中時，其機場不進入地圖；目的地境內的抵達機場繼續作為路線起點。跨國航段永遠不繪製路線。

多國旅行必須生成多個 `routeMap.regions[]`。每個 Region 獨立選擇底圖、佈局地點和繪製境內路線，不得把兩個國家的地點合併到一張地圖。跨國移動當天由抵達目的地的 Region 承接 Daily Map。

## 4. 相對位置佈局

地點經緯度只用於確定相對方位和距離關係。Builder 使用統一比例將全部地點一次性對映到模板安全區域，再執行有限的確定性疏散。

- 北方保持在上方，東方保持在右側；
- 緊湊旅行允許整體放大；
- 節點使用固定最小間距並受安全區域限制；
- 疏散後向原始投影位置回拉，避免方向關係顛倒；
- 同一輸入始終得到相同座標；
- Overview 與所有 Daily 複用同一組最終座標。

缺少經緯度時使用確定性備用佈局，但 `validate-lite` 必須給出警告。

## 5. 凍結視覺

- 路線 `fill:none`，round linecap 與 linejoin；
- 主路線寬度 `7`，白色半透明內層寬度 `2`、透明度 `.22`；
- 固定六色：`#397dc1`、`#e77e22`、`#618344`、`#209aaa`、`#8865a5`、`#df6185`；
- 固定三次貝塞爾曲線規則，不使用隨機曲線；
- Overview 節點半徑 `10.5`，白色邊框 `2.5`；
- 字型為 Times serif 與中文楷體、宋體回退組合；
- 標籤使用深藍 `#092653`、字重 `700`、描邊 `0.4`；
- 標題固定左上角，預設 `40/700`；
- 圖例透明無卡片，固定色條、字號、間距和位置。

Agent 不得直接填寫 SVG path、節點座標或自由調整樣式。

## 6. Overview 與 Daily

Overview 最多顯示 10 個核心地點。超過時，Builder 根據起終點、跨日出現次數和路線中點選擇核心地點，並使用簡化路線減少擁擠。Daily 使用當天完整路線與地點。

Overview 與 Daily 必須保持相同底圖、canvas、viewBox、scale、地點座標和模板位置。Day 切換隻改變路線、當天地點、標籤和交通 pin 的可見性。禁止 fitBounds、zoom-to-route、crop-to-day 或任何 Daily 重投影。

## 7. 普通 Agent 邊界

普通 Agent 只寫 `trip-data.json > map` 中的地點、經緯度、順序、每日路線、名稱和 query。不得呼叫圖片模型、讀取 Boundary Library、下載地圖、設計背景、選擇配色或繞過 `build-map.mjs`。

Boundary Library 和舊國家輪廓生成實現只作為 `references/advanced/` 參考保留，不屬於普通生成鏈路。

## 8. 固定說明

Overview 地圖下方必須顯示：

“本圖為模板化行程示意圖，僅表達地點的相對方位與路線順序，不代表真實比例或精確地理邊界。如需使用真實國家或城市地圖，可在生成後自行調整。”

## 9. 驗收條件

- 十張底圖均可由 Builder 讀取；
- 模板選擇和地點佈局確定性；
- 地點方向關係基本正確，密集地點不會全部重疊；
- 路線、節點、字型、標題與圖例保持 Golden token；
- Overview 使用核心地點，Daily 使用當天詳細地點；
- Overview 與 Daily 的地圖範圍和地點座標完全一致；
- 普通生成不讀取 Boundary、不生成新底圖、不呼叫圖片模型。
