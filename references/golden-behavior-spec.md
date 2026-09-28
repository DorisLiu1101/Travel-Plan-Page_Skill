# Golden Behavior Specification

基線日期：2026-09-10  
事實來源：Golden Version 的 `app.js`、`site-navigation.js`，以及此前已完成的 Map shell 瀏覽器/程式碼審計。Ledger 細節見 `golden-ledger-spec.md`。

## 0. 分類

- **[FROZEN BEHAVIOR]**：成熟產品互動。架構重構必須保持使用者可觀察結果。
- **[CURRENT IMPLEMENTATION]**：當前程式碼路徑，可能在後續架構中被配置化或替換；不自動成為產品規則。
- **[POTENTIAL BUG]**：程式碼已顯示風險或不一致，但影響尚未完成真實邊界驗證。
- **[UNVERIFIED]**：缺少足夠的真實瀏覽器、失敗注入或多裝置驗證；不得猜測。

“凍結”指相同有效輸入與狀態下的行為結果一致，不要求函式名、檔案位置或內部模組邊界不變。

## A. Travel Navigation

### A00 Config-driven modules

**[FROZEN BEHAVIOR]**

- Given `trip-data.json > config.modules`中某模組為`false`  
  Then該section、導航入口與相關初始化均不出現，不留下空白，也不發起該模組的runtime/API請求。
- Given前置模組關閉  
  Then頁面與導航從第一個啟用模組開始；不得依賴手工刪除HTML或JavaScript。
- Given Config缺失或非法  
  Then顯示明確配置錯誤；不得自行猜測使用者模組選擇。

### A01 Travel / Ledger 頁面切換

**[FROZEN BEHAVIOR]**

- Given 當前位於 Travel view  
  When 點選頂部“記賬”  
  Then 阻止預設錨點跳轉，關閉 Travel 下拉選單，地址變為 `#ledger`，Travel `hidden + inert`，Ledger 取消 `hidden/inert`，body 標記 active view，Ledger Entry tab 啟用。

- Given 當前位於 Ledger view  
  When 點選 Travel 選單中的 section link 或 wordmark  
  Then 關閉選單、顯示 Travel、隱藏並 inert Ledger；section link滾動到目標 section，wordmark滾動到 `#top`。

- Given 頁面由 `#ledger-stats` 開啟  
  When 初始 route 執行  
  Then Ledger view顯示且 Stats tab啟用；`#ledger` 啟用 Entry tab。

### A02 頂部導航和當前狀態

**[FROZEN BEHAVIOR]**

- Given Travel view active  
  When 導航狀態同步  
  Then Travel summary具有 `aria-current="page"`，Ledger link移除該屬性，skip link指向 `#main`。

- Given Ledger view active  
  When 導航狀態同步  
  Then Ledger link具有 `aria-current="page"`，Travel summary移除該屬性，skip link指向 `#ledger-root`。

### A03 Travel 下拉選單

**[FROZEN BEHAVIOR]**

- Given Travel details menu開啟  
  When 點選選單外部  
  Then 移除 `open`。

- Given Travel details menu開啟  
  When 點選任一 Travel link或 Ledger link  
  Then 選單先關閉，再執行導航。

- **[CURRENT IMPLEMENTATION]** 選單為原生 `<details>/<summary>`；除瀏覽器原生行為外，沒有單獨實現 Escape、方向鍵或 menu roving focus。
- **[UNVERIFIED]** 不同瀏覽器對原生 details 的 Escape 行為和 `role=menu/menuitem` 鍵盤體驗尚未逐項驗證。

### A04 Scroll、歷史和返回

**[FROZEN BEHAVIOR]**

- Given Travel 與 Ledger 已分別滾動  
  When 在兩個 view 之間切換  
  Then 離開 view 時把 `window.scrollY` 儲存到記憶體中的對應 slot。

- Given 點選 Travel section link  
  When Travel view顯示  
  Then 使用目標元素 `scrollIntoView({block:"start"})`；CSS smooth scroll/reduced-motion結果由 Frozen UI 控制。

- Given 切換到一個沒有 section target 的新 view  
  When 不是 browser restore  
  Then 滾動到 top `0`。

- Given 瀏覽器 Back/Forward 造成 view改變  
  When `popstate` 在 animation frame 中處理  
  Then 嘗試恢復該 view 的記憶體 scroll position；`history.scrollRestoration` 為 `manual`。

- **[CURRENT IMPLEMENTATION]** Scroll positions只存於當前頁面記憶體，不跨 reload/tab持久。
- **[UNVERIFIED]** 同一 view 內 `#ledger ↔ #ledger-stats` 的 Back/Forward 與連續 `popstate/hashchange` 組合下，scroll精確恢復結果尚未做瀏覽器矩陣驗證。

### A05 外部連結

**[FROZEN BEHAVIOR]**

- Given 使用者點選 Place overlay footer 的 Google Maps link或 driving reference link  
  When 瀏覽器允許開啟外部頁面  
  Then 以新 browsing context 開啟，使用 `target="_blank"` 和 `rel="noopener noreferrer"`。

- Given 使用者點選 timeline 的地點地圖按鈕  
  When overlay開啟  
  Then 先在站內 iframe展示 Google Maps，並提供外部開啟入口；不會直接離開當前行程頁。

- **[UNVERIFIED]** 各瀏覽器 popup policy、Google 網路不可達與 iframe CSP/地區限制下的最終外部開啟結果。

## B. Flight

### B01 Carousel、snap、centered card 和 active dot

**[FROZEN BEHAVIOR]**

- Given 多個 journey card已渲染  
  When 使用者水平滾動 carousel  
  Then CSS執行 mandatory x snap；scroll handler在下一 animation frame計算 viewport center與每張 card center的絕對距離，距離最小的 card成為 active。

- Given active card改變  
  When center計算完成  
  Then 只有對應 dot獲得 `is-active`，section index顯示一基序號 `activeIndex + 1 / journeyCount`。

- Given 初次渲染  
  When 尚未滾動  
  Then 第一顆 dot active，index為 `1 / count`。

- **[CURRENT IMPLEMENTATION]** 兩張 card center等距時，因只接受嚴格更小距離，陣列中較早的 card勝出。

### B02 Journey status

**[FROZEN BEHAVIOR]**（狀態階段），**[CURRENT IMPLEMENTATION]**（時間解析來源）

- Given 當前時間早於某段 departure  
  When 按航段順序掃描  
  Then 第一段顯示“距離起飛還剩”，後續段顯示“距離下一程起飛還剩”，target為該 departure。

- Given departure已過且 arrival未到  
  When 狀態計算  
  Then 顯示“飛行中 · 距抵達”，target為 arrival。

- Given 所有 arrival均已過  
  When 狀態計算  
  Then label為“已抵達”，card value為“已完成”。

- **[CURRENT IMPLEMENTATION]** departure/arrival分別由該端點的本地日期、時間和 `utcOffset` 解析；不再使用機場程式碼或固定 offset 表。非 placeholder 航段的 offset 由輕量 validator 按 `±HH:MM` 檢查。

### B03 Countdown 與每秒重新整理

**[FROZEN BEHAVIOR]**

- Given target在未來  
  When precise countdown渲染  
  Then 使用 floor後的總秒數；有天數顯示 `N天 HH:MM:SS`，不足一天顯示 `HH:MM:SS`，時分秒補零。

- Given target已到或已過  
  When countdown渲染  
  Then 使用呼叫方 completion text；flight card最終顯示“已完成”或過渡呼叫中的“即將出發”。

- Given Travel初始化完成  
  When countdown timer啟動  
  Then 立即更新一次 flight/rental，再以 `1000ms` interval更新。

### B04 跨日期

**[FROZEN BEHAVIOR]**

- Given stop日期與 journey起始日期相同  
  When 日期標籤渲染  
  Then 顯示緊湊月日。

- Given stop日期比 journey起始日期晚一天  
  When 日期標籤渲染  
  Then 顯示“次日”。

- Given日期差不是0或1  
  Then 顯示該日期的緊湊月日。

### B05 Today / future / past

- **[FROZEN BEHAVIOR]** Flight的 future/in-flight/past階段切換及文字語義凍結。
- **[CURRENT IMPLEMENTATION]** Flight本身不使用 Today label；Daily Today優先使用可選的 `metadata.timeZone` IANA 時區覆蓋值，缺失或無效時回退當前瀏覽器時區。
- **[UNVERIFIED]** target精確等於當前毫秒、瀏覽器休眠喚醒、後臺tab interval節流後的邊界顯示。

### B06 缺失航班材料時繼續預覽

**[FROZEN BEHAVIOR]**

- Given 使用者在 Round 1 保留航班模組，但已確認材料缺失，並在 Round 2 選擇繼續預覽  
  Then 渲染標準的“資料待補充”航班卡，明確列出缺失類別。
- Placeholder 不包含猜測的航空公司、航班號、機場、起降時間或時區，也不執行倒計時。
- Given 使用者在 Round 1 關閉航班模組  
  Then 整個航班 section、導航和倒計時初始化均不出現，不生成 placeholder。

## C. Daily Itinerary

### C01 初始展開邏輯和 Today

**[FROZEN BEHAVIOR]**

- Given trip days中存在日期等於“當前旅行日”的 day  
  When timeline首次渲染  
  Then 該 day為唯一展開項，card有 Today狀態及“今天”文字。

- Given不存在匹配 day  
  When timeline首次渲染  
  Then `expandedDay=null`，所有 day detail關閉。

- **[CURRENT IMPLEMENTATION]** “當前旅行日”優先由可選的 `metadata.timeZone` IANA 時區覆蓋值決定；缺失或無效時使用當前瀏覽器時區。

### C02 Accordion 單開、展開和收起

**[FROZEN BEHAVIOR]**

- Given任意 day toggle被點選  
  When該 day原本關閉  
  Then 先把所有 toggles設為 collapsed、隱藏所有 details，再僅展開所點 day並更新 `expandedDay`。

- Given所點 day原本展開  
  When再次點選  
  Then 所有 days關閉，`expandedDay=null`。

- Given展開或收起  
  Then 不自動把 day滾動到視口，也不重建 timeline DOM。

### C03 Schedule content、地圖按鈕、note/cost/tag

**[FROZEN BEHAVIOR]**

- Given day包含 schedule items  
  When渲染  
  Then 保持資料順序，並顯示 time、escaped text、關聯 ticket、地點按鈕。

- Given day包含 notes或 source date conflict  
  When渲染  
  Then 普通 notes在前，source conflict附加在後，逐條顯示。

- Given day包含 cost references  
  When渲染  
  Then 按 amount、standard、discounted、amountOptions的現有優先順序生成 tag文字。

- Given schedule item按 navigation policy被認定無需導航  
  Then 不顯示地點按鈕。

- **[LEGACY COMPATIBILITY]** 舊Demo可能仍由schedule文字、match terms、名稱、priority與字串最後出現位置推斷地點；新canonical Trip必須使用typed Place references，validator不得允許顯示文案控制新資料關聯。

## D. Ticket

### D01 Ticket 與 schedule 的當前關聯

**[CURRENT IMPLEMENTATION]**

- Given ticket的 `day` 等於當前 day  
  And schedule item text轉為 locale lowercase  
  When 任一 `scheduleMatchTerms` 小寫後是該文字的 substring  
  Then ticket渲染到該 schedule item。

- Given同一 ticket命中同一天多個 item  
  Then 當前實現可能在多個位置渲染同一 ticket；所有例項透過 ticket ID同步視覺狀態。

- 該字串關聯不是 **[FROZEN BEHAVIOR]**，只允許作為舊fixture相容。新canonical Trip必須由Day Item `ticketIds[]`關聯；同一Golden fixture的可見結果仍須保持。

### D02 Pending / Purchased

**[FROZEN BEHAVIOR]**

- Given ticket data `purchaseStatus="purchased"` 或 runtime completion set包含 ticket ID  
  Then ticket為 purchased。

- Given ticket未 purchased  
  Then 根據 requirement顯示“需提前購票 / 建議預約 / 購票方式待確認 / 門票資訊”。

- Given day有 tickets  
  Then day summary顯示 pending數量；全部 purchased時顯示“門票已準備”。

### D03 完成、取消和 Runtime sync

**[FROZEN BEHAVIOR]**（使用者意圖），**[CURRENT IMPLEMENTATION]**（儲存時序）

- Given使用者勾選 ticket  
  When change觸發  
  Then立即把ID加入runtime Set、更新所有相同ticket例項及day summary，並交給當前persistence adapter儲存。

- Given使用者取消勾選  
  Then立即移除ID並更新UI，並交給當前persistence adapter刪除。

- Given預設local mode  
  Then從當前瀏覽器按Trip ID讀取/儲存Ticket狀態，不訪問`/api/trip`。

- Given使用者明確啟用D1且`tickets`在`sharedCollections`  
  Then從共享快照讀取truthy completion，並透過同源API同步變更。

- **[CONFIRMED ISSUE]** 可選D1模式下POST失敗仍可能只`console.error`，不回滾Set/UI、不顯示使用者錯誤；重新整理後的結果可能與剛才UI不同。此失敗行為不凍結為正確產品行為。

### D04 Ticket document and purchase link

**[FROZEN BEHAVIOR]**

- Given Ticket有獲准進入Trip assets的PDF或圖片  
  When使用者點選票據入口  
  Then先在站內dialog/overlay預覽，不直接離開旅行頁；close、backdrop、Escape和focus return遵守現有overlay規則。
- Given Ticket只有官方購買URL  
  Then入口明確標識為外部購買頁，並使用`target="_blank"`與`rel="noopener noreferrer"`。
- Given票據材料缺失且使用者選擇繼續預覽  
  Then顯示“待補充”，不生成無效或猜測URL。

## E. Todo

### E01 新增和空輸入

**[FROZEN BEHAVIOR]**

- Given輸入 trim後為空  
  When提交  
  Then 不新增、不儲存，保留頁面狀態。

- Given輸入非空  
  When提交  
  Then生成穩定唯一runtime ID，追加`{text,completed:false}`，清空input，交給當前persistence adapter儲存並立即重繪。

- ID生成格式屬於 **[CURRENT IMPLEMENTATION]**；唯一、穩定的 runtime ID語義屬於 Frozen behavior。

### E02 完成、取消和刪除

**[FROZEN BEHAVIOR]**

- Given使用者切換checkbox  
  When change觸發  
  Then立即更新對應todo.completed、交給當前persistence adapter儲存、重繪progress/list。

- Given使用者點選刪除  
  Then立即從陣列移除、交給當前persistence adapter刪除、重繪；當前沒有confirm dialog。

- Given list為空  
  Then 顯示“還沒有準備事項，新增第一項吧。”，progress為 `0 / 0`。

- Given預設local mode  
  Then從當前瀏覽器按Trip ID讀取/儲存Todos，不訪問`/api/trip`。

- Given使用者明確啟用D1且`todos`在`sharedCollections`  
  Then使用共享snapshot `todos`；非陣列退回空陣列。

- **[CONFIRMED ISSUE]** 可選D1模式的upsert/delete失敗仍可能只寫console；沒有rollback、retry UI或使用者可見notice，不凍結為正確行為。

### E03 Optional shared load failure

- **[CURRENT IMPLEMENTATION]** 僅D1 shared mode會訪問Shared API；load失敗時仍繼續渲染Travel並保留可操作狀態。
- **[POTENTIAL BUG]** D1錯誤提示/重試與本地已存在狀態的合併仍需失敗注入驗證；不得把讀取失敗靜默解釋為遠端真實空狀態。

## F. Rental

### F01 Pickup / Return status

**[FROZEN BEHAVIOR]**（階段語義）

- Given now早於 pickup  
  Then label為“距取車”，target為 pickup。

- Given now介於 pickup和dropoff  
  Then label為“距還車”，target為 dropoff。

- Given now達到或超過dropoff  
  Then label為“已超過預約還車時間”，主文案提示立即聯絡 rental company。

- **[CURRENT IMPLEMENTATION]** `rentalStatus()` 分別使用 pickup/dropoff 自己的 `utcOffset`，deadline timer 使用同一個 dropoff offset。已開啟租車模組時，兩個 offset 均由輕量 validator 按 `±HH:MM` 檢查。

### F02 Countdown、deadline 和 urgent

**[FROZEN BEHAVIOR]**

- Given deadline未來  
  Then deadline顯示“距還車截止 {precise countdown}”。

- Given deadline已過  
  Then顯示預約時間已過的聯絡提示。

- Given remaining `<= 86,400,000ms`，包括已過期  
  Then deadline增加 urgent視覺狀態。

- Given rental階段未完成  
  Then status區使用較粗粒度 countdown：有天顯示天/小時，有小時顯示小時/分鐘，不足一小時至少顯示1分鐘。

### F03 Drive tabs

**[FROZEN BEHAVIOR]**

- Given首次渲染  
  Then “取還車檢查” active並顯示對應列表。

- Given點選非active tab  
  Then 關閉其他 tabs，僅所點 tab `aria-expanded=true`，panel替換為對應內容。

- Given點選當前 active tab  
  Then 當前 tab collapse，panel hidden；允許沒有任何 active內容。

- Driving reference links按外部連結規則開啟。

## G. Map Shell Interaction

本節只凍結 shell行為，不重複地圖視覺與資料審計。

### G00 Country switch

**[FROZEN BEHAVIOR]**

- Given Trip Data包含多個`routeMap.regions[]` Map Packages  
  When Route Explorer載入  
  Then按資料順序顯示相同數量的國家標籤，預設選擇`defaultRegionId`或第一個Package。

- Given使用者選擇另一個國家  
  When國家標籤切換  
  Then切換到該國自己的base artwork、總覽routes、places、annotations、legend和日期標籤，並回到該國總覽狀態；不得保留上一國家的Day選擇或地圖資料。

### G01 Overview / Day switch

**[FROZEN BEHAVIOR]**

- Given某一國家的Route Explorer已載入  
  When使用者選擇 Overview  
  Then顯示該國家的完整 artwork狀態並同步 pressed tab。

- Given使用者選擇某個 Day  
  Then僅顯示該 day的 daily map狀態、地點/交通互動入口並同步 pressed tab。

- **[CURRENT IMPLEMENTATION]** Day與內部 route/layout的具體選擇由當前 route module完成；目的地差異必須由 generated Map Package 表達，Core 不新增目的地特判。

### G02 Place popup 與 Google Maps

**[FROZEN BEHAVIOR]**

- Given使用者點選地圖 place dot  
  Then開啟 place popover，顯示地點標題、可用選項、嵌入地圖和 Google Maps外鏈。

- Given同一地點存在多個 place options  
  When切換 option  
  Then pressed狀態、iframe query和外鏈同步更新。

### G03 Transport popup

**[FROZEN BEHAVIOR]**

- Given使用者點選 transport pin  
  Then開啟固定定位 transport popover，展示關聯交通 leg；同一時刻不保留衝突 popup。

- Given popup已開  
  When點選關閉、外部或另一入口  
  Then關閉/替換 popup，並同步 `aria-expanded`。

### G04 Fullscreen、Escape、outside、focus 與 scroll

- **[FROZEN BEHAVIOR]** Fullscreen入口開啟 map dialog，關閉按鈕/原生 dialog關閉路徑應關閉；移動 overview map允許水平滾動，daily map shell不橫向滾動。
- **[FROZEN BEHAVIOR]** Place overlay開啟時鎖定 body overflow，focus移動到 close；Escape、backdrop點選或 close關閉，清空 iframe、恢復原 body overflow並把focus還給 opener；Tab在 close和external link之間迴圈。
- **[CURRENT IMPLEMENTATION]** Route popover/transport popover具有Escape、outside click/focusin關閉和focus恢復邏輯（據此前審計）。
- **[UNVERIFIED]** Fullscreen map dialog在所有瀏覽器中的初始focus、完整focus trap、Escape後的focus return與fallback-open路徑尚未逐項驗證。

## H. Dialog / Overlay

### H01 Open / Close / Cancel / Backdrop

**[FROZEN BEHAVIOR]**

- Given一個 Ledger dialog開啟  
  When請求開啟另一個 Ledger dialog  
  Then先關閉當前 dialog，再開啟目標 dialog；currency dialog可返回 settings。

- Given Ledger dialog open  
  When點選顯式 close、原生 Escape/cancel或dialog backdrop本身  
  Then dialog關閉並清理對應 open state；members dialog同時清除 member edit state。

- Given瀏覽器無 `showModal()`  
  Then使用 `open` attribute fallback。

### H02 Focus

- **[FROZEN BEHAVIOR]** Ledger dialog開啟後在下一 frame focus search input或第一個非color input/button；currency search選區位於當前query末尾。
- **[CURRENT IMPLEMENTATION]** Ledger dialog依賴原生 modal focus containment；沒有自定義 Tab trap，也沒有儲存 opener引用。
- **[UNVERIFIED]** Ledger dialog關閉後的focus return目標、fallback-open的focus containment和不同瀏覽器 cancel事件次序。

### H03 Inline note editor

**[FROZEN BEHAVIOR]**

- Given點選賬單備註  
  Then開啟單行 editor、focus並select現有值。

- Given點選 editor外部或執行其他 Ledger action  
  Then先嚐試儲存；儲存失敗阻止後續 action。

- Given按 Escape或點選取消  
  Then放棄未儲存內容並恢復只讀 trigger。

- Given同一 bill正在完整編輯  
  When點選其 inline note  
  Then滾動/focus完整 bill form的 note欄位，而非開啟第二個 editor。

## I. Initialization、Error、Responsive 與 Reduced Motion

### I01 Travel load

- **[FROZEN BEHAVIOR]** Config與travel-data載入成功後，只初始化已啟用模組；預設先讀取local runtime state。只有顯式D1 mode與allowlist才嘗試shared state。
- **[FROZEN BEHAVIOR]** travel-data讀取或主初始化失敗時顯示全域性 loading error。
- **[CURRENT IMPLEMENTATION]** 可選 D1 shared state 讀取失敗不觸發全域性 loading error；Travel 端當前會把 Todo/Ticket 暫時呈現為空，且只寫 console。這是 `known-issues.md#pb-04--d1-shared-state讀取失敗可能被呈現為空狀態` 記錄的可選 shared-mode 風險，不是應凍結的理想行為。

### I02 Ledger load/save

- **[FROZEN BEHAVIOR]** Ledger初始化時root標記`aria-busy=true`；當前adapter load完成後歸一化並渲染，再移除busy。
- **[FROZEN BEHAVIOR]** 預設local mode無需D1；localStorage不可用時退回本標籤頁記憶體並保持可操作。
- **[FROZEN BEHAVIOR]** 顯式D1 load/save失敗顯示live notice並保留安全的本地/上一次成功state，不把錯誤顯示成“必須繫結作者資料庫”。

### I03 Responsive / keyboard / reduced motion

- **[FROZEN BEHAVIOR]** 響應式改變佈局而不刪減功能；具體視覺見 Golden UI spec。
- **[FROZEN BEHAVIOR]** Ledger tabs支援 ArrowLeft/ArrowRight在兩個 tab間切換並把focus移到新 tab。
- **[FROZEN BEHAVIOR]** Reduced motion時關閉 Ledger view animation並極小化CSS transition/animation duration。

## J. Ledger Product Interaction Summary

以下屬於 **[FROZEN BEHAVIOR]**，精確資料與演算法見 `golden-ledger-spec.md`：

- Traveler新增、編輯姓名/顏色、刪除確認、重複姓名攔截、賬單引用刪除限制。
- Bill新增、編輯、刪除確認、inline note編輯、payer單選、participants多選與全選/全不選切換。
- Base/foreign amount雙欄位，category/date/note，表單錯誤定位與live notice。
- Entry/Stats tab切換、hash同步、統計卡預設展開、空狀態文案語義。
- 設定/成員/貨幣 dialogs與currency search。
- Ledger mutation在單瀏覽器內序列；成功後才替換 ledgerData並重繪，失敗保持舊state。

以下不凍結為正確行為：settings persistence缺失、API無衝突控制、失敗情況下的已知問題。

## K. Unverified Register

本輪仍為 **[UNVERIFIED]**：

1. Travel menu原生 details在各瀏覽器的Escape/鍵盤行為。
2. 同一 view內瀏覽器Back/Forward的精確scroll恢復。
3. countdown臨界毫秒、後臺tab節流和系統時間跳變。
4. Google iframe失敗、popup policy與外部瀏覽器開啟結果。
5. Fullscreen map dialog的完整focus return/trap/fallback路徑。
6. Ledger native/fallback dialog關閉後的focus return與Tab containment。
7. Cloudflare/D1真實失敗注入後的端到端notice、重試和最終一致性。
8. 兩裝置併發寫入不同/相同記錄的真實部署測試。
