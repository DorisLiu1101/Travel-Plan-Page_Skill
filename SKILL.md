---
name: generate-lightweight-travel-page
description: Assemble a Golden-style travel page from user materials with two short confirmations. Use ten fixed map templates, automatic deterministic template selection, one editable trip-data.json input, and lightweight validation.
---

# AI-Friendly Lightweight Travel Template

普通生成中，Agent 是模板裝配員。第一版優先速度、穩定性和複用，不重新設計頁面、地圖或記賬功能。

## 首次生成優先順序

首次生成的目標是儘快交付一個可用、好看的網頁底板，不是完成正式上線級驗收。

已有模板和規則明確時，直接按本 Skill 生成，不重新審計框架或重複分析專案結構。使用者資料能夠從文字中明確提取時直接使用；只有內容無法識別、排版異常或存在明顯歧義時，才做進一步的頁面級視覺檢查。

首次生成只做必要校驗：資料可讀取、頁面正常載入、已開啟模組正常顯示、地圖正常生成、無明顯執行錯誤。完整的桌面/手機互動測試、逐項事實複核和邊界場景檢查不是預設步驟，需要時再執行。

`trip-data.json` 預設是不含任何示例旅行事實的空白底板，所有旅行陣列為空，六個模組關閉。新旅行直接根據使用者資料一次性寫入，不查詢、不識別、也不合並舊 Demo 資料。

## 普通生成只讀範圍

開始時只讀：

- 使用者上傳的旅行資料；
- `trip-data.json`。

不要掃描整個 Repo，不要重新分析 Golden UI、記賬、Runtime 或架構。只有使用者明確要求修改某個模組，或輕量校驗指出對應問題時，才定向讀取相關 reference。

## 固定許可權邊界

普通生成只允許修改：

- `trip-data.json`；
- 本次旅行明確授權的 trip-specific assets。

`trip-data.json > routeMap` 和 `metadata.assets.routeMaps` 是構建派生欄位，只由 `scripts/build-map.mjs` 寫入；Agent 不手寫這兩處。

普通生成禁止修改：

- `index.html`、`styles.css`、`ledger.css`；
- `app.js`、`overview-map.js`、`route-ui.js`、`site-navigation.js`；
- `ledger.js`、記賬金額/分賬/結算演算法；
- Golden Map Style、路線顏色、雙 stroke、圓點、字型、圖例和核心互動；
- Schema、Migration、Normalizer、Runtime、D1 或其他 Framework 級實現。

使用者生成第一版後明確提出 DIY 請求，才進入自由修改模式；仍需保護使用者未授權的資料和檔案。

## 標準生成流程

### STEP 1：讀取旅行資料

一次性讀取使用者提供的文件、文字或公開資料。不得把私人原始檔案當作公共示例或可複用模板資源；但使用者提供並要求用於本次本地頁面的門票 PDF，按下文門票規則複製完整副本到本次旅行 asset，不因其中包含票號或二維碼而追加隱私確認。測試和公共資源必須使用完全虛構或明確允許公開的資料。

### STEP 2：提取實際內容

提取：

- 日期與基本旅行資訊；
- 國內/國外屬性；國內行程在使用者資料中明確表達的主要目的地名稱；國外行程的目的地國家組合；
- 航班與住宿；
- 每日行程與地點順序；
- 門票；
- 租車；
- 準備事項；
- 真正存在的缺口或衝突。

不要建立 `source-facts.json`，不要記錄逐條 provenance、頁碼或 confidence，不要建立 canonical 中間層，也不要強制補齊所有 Entity 或 Stable ID 類別。

本地個人版以完整保留使用者資料為預設。票號、二維碼、Booking PIN、私人電話、完整預訂號以及門票 PDF 中的其他內容都按使用者提供的原文提取和使用；除非使用者明確要求，否則不得在資料閱讀、內容總結、模組確認、缺口確認或首次生成過程中主動建議隱藏、脫敏、刪除、裁切或打碼。它們不是“缺失材料”或需要額外確認的隱私問題。

### STEP 3：第一次確認（模組）

一次性告訴使用者：

- 哪些資料已經存在；
- 建議開啟哪些模組；
- 哪些模組資料部分存在或暫未發現；

第一次確認只允許展示以下六個使用者模組，並且必須按此順序、使用中文名稱編號：

1. 航班
2. 地圖
3. 每日行程
4. 租車
5. To Do
6. 記賬

內部配置對映固定為：航班=`modules.flights`、地圖=`modules.overview`、每日行程=`modules.itinerary`、租車=`modules.driving`、To Do=`modules.todo`、記賬=`modules.ledger`。不得向使用者展示內部英文鍵，不得把記賬寫成 `Ledger`，也不得出現第七個模組。

門票不是獨立模組：不編號、不單獨確認、不寫入 `config.modules`。門票資料是“每日行程”中的內容，有資料時顯示在對應行程裡；資料不足時，只在第二次確認中作為內容缺口說明；顯示與隱藏始終跟隨“每日行程”。

第一次確認輸出後立即停止並等待使用者回覆。未收到明確回覆前，不得進入第二次確認、寫入旅行資料、構建地圖或啟動頁面。沒有資料不代表自動關閉，使用者仍可保留模組並顯示“待補充”。

地圖只使用 `assets/maps/templates/manifest.json` 中登記的十張固定底圖。普通生成不得臨時繪製、生成或增加新模板；只有模板庫維護任務才允許更新該目錄與 manifest。

Agent 只確認模組；`scripts/build-map.mjs` 先根據地點經緯度、路線跨度、方向、密度和連通關係形成候選模板池，再根據由區域、地點與路線組成的旅行簽名做穩定雜湊，從候選池中確定性選擇一張。不得要求使用者選擇地圖風格。`trip-data.json > map.mapMode` 固定寫為 `template-auto`，`map.templateId` 固定寫為 `auto`；Builder 生成的 `routeMap.regions[].mapMode` 為 `frozen-template`。

高密度點位由 Builder 在統一安全區域內確定性疏散。經緯度只負責相對東南西北和距離關係，不追求真實比例；同一輸入必須得到相同位置。

### STEP 4：第二次確認（真正的資料缺口）

只檢查使用者最終保留的模組，把所有缺失、衝突和歧義合併成一次確認。讓使用者選擇：

- 現在補充；或
- 先生成，缺失處顯示“待補充 / 待確認”。

不要重複詢問已經明確的資訊。少量缺失不得阻止生成；只標記缺失欄位，不覆蓋已經確認的事實。

收到使用者對第二次確認的明確回覆後，先向使用者傳送以下說明，再繼續 STEP 5。這只是進度提示，不構成第三次確認，也不需要等待使用者再次回覆：

> 首次生成需要 AI 閱讀並整理你的旅行資料，再套用模板生成頁面，因此會需要一定時間。簡單行程通常幾分鐘到十幾分鍾即可完成；如果行程天數較多、涉及多個城市/國家或資料比較複雜，生成時間可能更長

### STEP 5：只寫一份輸入

只寫入 `trip-data.json`：

- 從空白容器一次性寫入本次旅行的完整內容，把 `trip.status` 從 `uninitialized` 改為 `draft`，並替換 `metadata.tripId` 與標題；
- `config`：六個模組開關、語言和本地優先持久化；
- `map`：地點經緯度、區域歸屬、地點順序、總覽路線與每日路線。

使用者未提供的內容保持空陣列，或僅在已啟用模組中按現有規則標為“待補充 / 待確認”。不得把空白底板中的佔位狀態當成使用者事實。

不要手寫 `routeMap`、SVG path、地圖座標、路線顏色或標籤樣式。

### 首次寫入欄位速查

保留空白底板已有的容器鍵；模組關閉時保留空陣列或 `null`，不要刪除容器。首次生成至少遵守：

- `metadata` 寫 `tripId`、`title`；`trip` 寫 `status: "draft"`、起止日期、`dayCount`、國家和目的地區域。日期使用 `YYYY-MM-DD`。
- `days[]` 寫 `day`、`date`、`title`、`locations[]`、`schedule[]`；行程項寫 `id`、`time`、`type`、`text`，有對應資料時再加 `placeId` / `placeIds` / `ticketIds`。`dayCount` 必須等於 Day 數量。
- `accommodations[]` 可保留住宿記錄；當前頁面要顯示的入住、退房和住宿文字仍寫入對應的 `day.schedule[]`。
- 完整航班使用 `flightJourneys[]:{id}` 和 `flights[]:{id,journeyId,sequence,airline:{name或nameZh},flightNumber,departure:{airportCode,city,date,time,utcOffset},arrival:{同結構}}`。資料缺失時只寫帶 `placeholder:true`、`status:"pending"`、`missingFields[]` 的 Journey，不猜航班事實。
- `places[]` 寫唯一 `id` 和 `name` 或 `nameZh`；`ticketPlanning.items[]` 用唯一 `id`、`day` / `dayId`、名稱和 `requirement`，由行程項的 `ticketIds[]` 關聯。
- `preTrip.packingItems[]` 寫 `id`、`text`、`completed`；沒有使用者明確提供的 To Do 時保持空陣列。
- 開啟租車時，`rentalCar` 寫 `company`、`rentalPeriodDays`、`vehicle:{example,class}`、`unlimitedKilometers`、`price:{currency,payAtCounter}`、`insurance[]`、`pickup:{date,time,location,address,utcOffset}`、`dropoff:{date,time,timeZoneLabel,vehicleReturnPoint,deadlineWarning,recommendedArrivalTime,utcOffset}`；同時保留租車檢查、駕駛提醒和參考連結陣列。
- 地圖開啟時填寫 `region`、`places[]`、`routes[]`、`dailyRoutes[]`。地圖地點使用唯一 ID，優先提供經緯度；路線的 `day` 對應已有 Day，`placeIds` 至少兩個且必須存在。多目的地地點還需 `countryCode` 或 `mapRegionId`；Daily Map 需要交通圖示時，用 `scheduleItems` 按相鄰路線段關聯行程項 ID 或索引。
- 地圖關閉時三組地圖陣列可為空；地圖開啟時執行 Builder。Agent 不寫 `routeMap` 或 `metadata.assets.routeMaps`。

Hero 標題與地圖模式完全獨立。固定規則只有兩種：

- 國內旅行：`trip.primaryDestinationName` 保留使用者資料中的主要目的地表述，例如“內蒙古”“成都”“新疆”；Hero 不顯示“中國”；
- 國外旅行：Hero 根據 `primaryDestinationCountries` 顯示國家名；多國之間使用 ` × `。

優先從旅行計劃標題、路線主題或使用者原文提取 `primaryDestinationName`，不要機械取第一個城市，也不要根據地圖 Scope 改寫它。資料沒有明確目的地表述時，才回退到 `primaryDestinationCity` 或 `citiesAndAreas` 第一項。`trip.heroTitle` 僅作為使用者後續明確 DIY 時的直接展示覆蓋值。

### STEP 6：構建並輕量校驗

```bash
npm run build:map
npm run validate
```

`build-map` 必須是唯一地圖生成入口。它從 `trip-data.json > map` 讀取地圖輸入，並把 Renderer 直接讀取的 `routeMap` 寫回同一份 `trip-data.json`。

`validate-lite` 只檢查會導致頁面失敗或洩露的問題：JSON、基本行程、Day、模組資料或明確待補充、地圖地點/路線、模板清單與所引用底圖、明顯 Secret，以及核心執行檔案。

不要在普通生成中執行完整 Entity、18 類 Stable ID、provenance、migration、architecture 或 Framework Schema 校驗。

### STEP 7：啟動並快速檢查

```bash
npm run preview
```

從本次預覽程序輸出的 `Travel plan local preview:` 後取得實際 URL，用該地址確認 HTTP 200 或頁面正常載入，並在交付後保留此預覽程序執行。預設從 4173 埠開始；埠占用時伺服器會自動嘗試後續埠。連結必須來自本次成功執行的程序，不能預設埠、複用舊任務地址或僅憑啟動日誌判斷。內建瀏覽器已經開啟也不能替代最終交付連結。

只檢查資料可讀取、頁面能載入、已啟用模組可見、地圖已生成，且沒有明顯執行錯誤。只有內容無法識別、排版異常或存在明顯歧義時，才補充頁面級視覺檢查；完整桌面/手機互動、逐項事實和邊界場景驗收需要時再執行。完成後停止。

## 地圖硬邊界

Agent 只提供地點、經緯度、順序和每日路線。Builder 從十張固定底圖中自動選擇一張，併疊加固定路線、節點、標籤、標題和日期圖例。禁止呼叫圖片生成模型畫地圖，禁止自行設定顏色、字型、線寬、圓點、圖例、地形裝飾或交通圖示，禁止繞過 `scripts/build-map.mjs`。

地圖只收錄目的地內部行程。出發國、返程終點國和純轉機國家不屬於本次目的地時，其機場與跨國飛行路線不得寫入地圖；例如深圳飛往蘇黎世，只顯示蘇黎世及之後的瑞士境內路線。抵達機場位於目的地內部時必須保留，例如蘇黎世機場到瑞士其他地點。

多國旅行必須在 `trip-data.json > map.regions` 中按目的地拆分，每個地點提供 `countryCode` 或 `mapRegionId`。Builder 為每個目的地生成獨立 `routeMap.regions[]`，並刪除跨區域連線；瑞士地點只出現在瑞士地圖，羅馬或義大利地點只出現在對應地圖。不得把多個國家的全部地點壓進同一張模板圖。

Overview 最多顯示核心地點，Daily 顯示當天詳細地點；二者必須共用同一底圖、畫布、比例與地點座標。禁止 Day zoom、fitBounds、crop-to-day 或重新計算當天 extent。

普通旅行生成不得讀取 Boundary Library、研究地圖版權、下載輪廓或為某個國家另做新模板。舊 Boundary 和國家輪廓能力只作為 advanced/reference 保留。

## To Do 提取規則

To Do 只允許提取使用者資料中明確寫出的待辦、備忘、提醒、準備事項或尚未完成的動作。不得根據常識自行補充證件檢查、天氣、換匯、網路、保險、行李、地圖或其他建議。使用者沒有明確提供 To Do 時，`preTrip.packingItems` 寫為空陣列，保留輸入介面供使用者自行新增；這不屬於阻止生成的資料缺口。

## 門票 PDF

使用者提供門票 PDF 時，不修改源 PDF，只將獲准使用的完整副本放入本次旅行的 `assets/tickets/`，並在對應 `ticketPlanning.items[].document` 寫入相對 `url`、`type: application/pdf` 與使用者可見 `label`。不得為了“安全”主動遮擋、裁切、打碼或重新匯出 PDF；只有使用者明確要求時才處理其中內容。點選門票的“檢視”按鈕必須在現有門票 Dialog 內嵌 PDF，同時保留“在新視窗開啟 PDF”作為瀏覽器不支援內嵌時的回退。沒有 PDF 時繼續顯示現有文字說明，不偽造檔案。

## 記賬與 Runtime

記賬直接複用 Golden 實現。普通使用固定為 `config.persistence.mode = "local"`，不需要資料庫。只有使用者明確要求多人共享或多裝置同步時，才定向讀取 `optional/cloudflare-d1/` 並啟用使用者自己的 D1；不得提交資料庫 ID、Account ID、Token、Secret 或私人執行資料。

## 生成結束提示

完成本地檢查後，按以下格式向使用者交付並結束任務。把下面兩處 `ACTUAL_URL` 替換成本次驗證成功的完整本地 URL，絕不能原樣輸出佔位符；即使頁面已經在內建瀏覽器開啟，也不能省略可點選連結。公開訪問風險只在這個最終交付階段提醒一次，不得提前放入資料分析或兩輪確認。不要展開 GitHub、Cloudflare Pages 或 D1 教程，不要要求使用者選擇下一步，也不要暗示已經完成公網部署：

第一版旅行網頁已生成完成，目前是本地可執行版本。

網頁地址：[開啟旅行網頁](ACTUAL_URL)

本地地址：`ACTUAL_URL`

隱私提醒：當前是本地頁面。如果以後公開部署，頁面內容可能被任何人訪問；是否移除或隱藏敏感內容、增加訪問保護，由你自行決定。

後續如需上線或多人共享，可以繼續配置：

本地網頁 → GitHub（版本管理） → Cloudflare Pages（公網部署） → [可選] Cloudflare D1（多人共享資料）

D1 僅在需要多人 / 多裝置共享記賬、Todo、Ticket 等資料時使用。

後續具體配置可再自行與 AI 溝通。
