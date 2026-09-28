# Golden Contract

狀態：Public Template Guardrail  
原則：**Reuse, not recreate.**

本檔案是未來Agent修改模板前必須先讀取的合同。Golden Version原始碼是視覺、行為與演算法的事實來源；公開倉庫不包含其私人Trip Data和Custom Map Fixture。

## Current Product Direction

當前目標是 **data-driven Standard Travel Generator**。每份使用者材料都經過相同的兩輪確認與構建流程，先交付本地標準預覽；個性化改版、線上部署和雲端共享分別屬於後續任務。

- 普通單次旅行生成只允許更改 `trip-data.json`和該 Trip 獲授權的 assets；歷史 canonical 流程僅作 advanced 相容保留。
- HTML、CSS、JavaScript、Schema、validator、Function、migration、Skill和references均為Core；單次生成不得修改。
- `source-facts.json`與原始PDF/圖片/訂單必須位於釋出倉庫之外。
- 六個使用者模組由 `trip-data.json > config.modules` 控制，不透過刪除section、導航或初始化程式碼實現。
- 地圖從十張固定模板中自動選擇；地點投影、路線、Daily layout 和 pins 由 Builder 從 `trip-data.json > map` 確定性派生，不由 Agent 逐點手畫。
- 本地瀏覽器儲存是預設執行方式；D1只在使用者明確要求多人/多裝置共享時啟用，並且必須屬於該使用者。
- 隱私安全、Golden UI、成熟互動與Ledger演算法仍是強制邊界。

普通單檔案生成的權威順序與輸出邊界見根目錄 `SKILL.md`。

## Contract Authority

視覺事實來源依次是：Golden production code、實際DOM/computed style/rendering、`golden-ui-spec.md`。截圖只用於迴歸，不能用來重新估算CSS。

行為與演算法分別由`golden-behavior-spec.md`和`golden-ledger-spec.md`展開。發現文件與程式碼衝突時應定向驗證並記錄，不得自行選擇“更漂亮”或“更通用”的結果。

## [FROZEN UI]

未經使用者明確批准，不得改變：

### Design Tokens

- paper、surface、ink、muted、line、lake、lake-soft、forest、terracotta、warning及元件級輔助色；
- Apple/PingFang/Hiragino/Microsoft YaHei系統字型棧和現有monospace棧；
- 字號、字重、line-height、letter-spacing；
- `720px`主content width；
- `24px/16px`主圓角層級及元件既有圓角；
- 主陰影、Ledger surface/dialog/card陰影；
- 頁面紋理、surface和border視覺。

### Layout and Responsive

- Topbar高度、sticky、safe-area、對齊和backdrop blur；
- Hero移動/桌面高度、padding和type scale；
- 主內容列、route寬版佈局、mobile gutter；
- section rhythm、heading/footer spacing；
- 當前breakpoints、carousel、map scroll和overflow邊界；
- `390×844`、`430×932`、`1440×900` baseline下的結構與響應結果。

### Components

- Flight carousel/card、airport flow、status、countdown和dots；
- Trip Overview、route tabs、map shell、utility和caption；
- Daily timeline、accordion、schedule、map button、Ticket、note和cost tag；
- Rental deadline/countdown/details和三個notes tabs；
- Todo form/list/check/delete/empty；
- Footer、Travel/Ledger navigation、active/dropdown states；
- place map overlay、map fullscreen、loading/error states；
- Ledger header、tabs、traveler avatar、bill form/list、stats、settlement、dialogs、buttons、inputs與empty states。

完整數值見`golden-ui-spec.md`。公開Demo內容造成的頁面絕對x/y不是通用硬編碼規則。

## [FROZEN BEHAVIOR]

### Navigation

- Travel與Ledger互斥顯示，hash/active/hidden/inert/skip-link同步。
- view切換儲存各自記憶體scroll position；section link滾動到目標。
- Travel menu外部點選關閉；Google Maps和reference links安全地在新context開啟。

### Flight

- carousel橫向snap，active card由中心距離判斷。
- Journey由ordered flights組成；future departure、in-flight arrival、completed狀態語義保持。
- precise countdown每秒重新整理，跨日顯示規則保持。

航班的 departure 與 arrival 分別使用各自端點資料中的 `utcOffset` 解析，不從機場程式碼推導。新 Trip 必須為兩個端點提供合法 offset；欄位缺失時當前相容回退為 `+00:00`，不得把該回退當作已確認的旅行事實。

### Daily Itinerary

- 初始只展開匹配當前旅行日的Day；無匹配則全部關閉。
- Accordion單開，點選已展開項可全部關閉。
- Schedule保持資料順序，顯示time/text/ticket/map links/note/cost。
- 地點overlay支援body lock、close/backdrop/Escape、focus return和主要control Tab迴圈。

### Ticket and Todo

- Ticket pending/purchased、requirement、day summary和同ID例項同步保持。
- Todo trim空值不新增；新增、完成、取消、刪除、progress與empty state保持。
- 預設在當前瀏覽器本地儲存，不請求共享API。
- 使用者明確啟用D1並列入`sharedCollections`時才共享；儲存失敗的當前限制見Known Issues，不把bug凍結為理想規則。

### Rental and Map

- Rental pickup前、使用中和return後的三階段倒計時語義保持。
- deadline、urgent state、每秒更新和三個notes tabs保持。
- Map國家切換、Overview/Day、place/transport popover、Google Maps和fullscreen入口保持。
- `routeMap.regions[]`中的每個目的地國家擁有獨立總覽、底圖和本國日期路線；Core只渲染明確資料，不從display text猜測國家。

### Ledger

- Traveler CRUD、重複姓名檢查、referenced-delete限制保持。
- Bill create/edit/delete、inline note、payer/participants、currency/base amount互動保持。
- Entry/Stats tabs、keyboard、draft、empty states和notice語義保持。
- 普通CRUD在save成功後提交本地Ledger state；mutation在單瀏覽器內序列。

## [FROZEN ALGORITHM]

未經使用者明確批准，Ledger不得重寫或改變：

- 金額輸入只接受正數與最多兩位小數；
- 所有金額、split、balance和settlement使用integer cents；
- foreign bill保留original與manual converted base amount；
- equal split使用`floor(total/participantCount)`；
- remainder按`participantIds`順序逐人分配，每人最多多1 cent；
- paid、owed、net balance定義；
- minimum-transfer settlement的debtor/creditor確定性順序；
- Avatar initial/color與Traveler identity規則。

迴歸輸入與精確預期見`golden-ledger-spec.md`及`tests/golden-baseline/ledger-regression-cases.md`。

## [FROZEN MAP STYLE]

所有標準生成地圖應繼承：

- 由 manifest 登記的十張固定 WebP 底圖及其安全區域；
- paper/terrain/water的低飽和region artwork語言；
- responsive SVG和當前map viewport surface；
- route雙stroke：主色`7`、白色高光`2/.22`、round cap/join；
- Golden六色route palette；
- Overview marker `r=10.5`、淺色2.5描邊；
- mixed serif/Kaiti place label、`700`、深藍、0.4描邊及generated anchor/size；
- heading和transparent date legend視覺；
- white/route-color rounded transport pins與line icons；
- current route tabs、utility、popover、fullscreen和responsive behavior；
- Overview全route、Daily僅selected route的composition。

詳見公開安全版`golden-map-spec.md`。目的地geometry與文字可變，視覺語法不隨意改變。

## [GENERATED TRIP ASSET]

下列內容屬於每個使用者自己的Trip構建結果，而不是公共模板常量：

- 由指標候選池與旅行簽名穩定雜湊選出的 template ID 與 base image 引用；
- 從 map Place、route 與 Day 引用生成的 route SVG paths；
- 投影后的place位置與自動label layout；
- daily layouts和transport positions；
- geographic annotations、heading、legend placement；
- destination queries、私人地址、地圖option和特殊影象。

這些值由標準map generator生成並驗證，Agent不得在單次旅行任務中手工修改座標、SVG path或Renderer。

私人Golden Map Package的實際assets、routes、dates、coordinates、queries和place list已從Public Template移除。不得嘗試從歷史文件、截圖或私人目錄重新複製。

普通生成只使用 `assets/maps/templates/manifest.json` 登記的十張固定底圖；舊 Boundary、`country-golden` 與 `generic-diagram` 能力只作為 advanced/legacy 參考保留，不屬於普通生成鏈路。

## [TRIP CONFIG AND DATA]

`trip-data.json` 是普通生成中旅行內容、`config` 與 `map` 輸入的唯一權威來源；`routeMap` 由 Builder 寫回同一檔案。該檔案必須透過輕量 Schema 與 `validate-lite`。

- Config中的六個module值只來自第一輪確認；門票跟隨每日行程，不是第七個開關。
- Data只來自使用者材料、兩輪確認和可驗證的派生結果；普通生成不建立 source-facts 或 canonical 中間檔案。
- Place、Day Item、Ticket、Transport和Map使用stable ID與typed references，不依賴顯示文字、array index或substring建立身份。
- 旅行摘要、地圖佈局、pending count等可計算內容由build/renderer派生，不作為第二份人工事實源。
- 未確認事實用明確issue/status表達，不以虛構值補齊。
- Runtime Todo、Ticket completion和Ledger不寫回靜態Trip Data。

### Authoritative Rules

- `metadata.tripId`是頁面與runtime namespace的唯一Trip ID；HTML不得維護第二份。
- `trip.primaryDestinationCountries`是 Agent 確認後的目的地國家清單；`config.modules.overview=true`時，每個 code 必須有一個對應的 `routeMap.regions[]` Map Package。
- 出發地或純轉機國家預設不生成地圖；跨境日可以同時出現在兩個Map Package中，分別呈現當地段落。
- Rental provider從Data渲染，不在HTML寫真實品牌。
- Day Item、Ticket、Place、Transport與Map必須透過穩定ID引用；改變顯示文案不得改變關聯。
- Map Package只能由map generator從 `trip-data.json > map` 派生，不手寫 `routeMap`。
- 精確事件時間應帶當地日期、時間和offset/timezone資訊；不要假設所有地點同一時區。
- Todo、Ticket completion與Ledger是Runtime State，不寫入公開Demo事實。

普通單檔案資料邊界以 `schemas/trip-data.schema.json` 與 `validate-lite` 為準；`travel-data-contract.md` 僅作 advanced/canonical 相容參考。

## [STABLE REFERENCE]

- 已有ID不得因顯示名稱、語言、日期或排序改變而重新生成。
- 新ID必須清晰、唯一、穩定且不包含私人敏感資訊。
- 任何Core-facing關係不得使用substring、schedule/day陣列位置、display name或SVG child順序充當identity。
- validator必須拒絕懸空、錯誤型別或重複引用。

命名約定見`stable-id-proposal.md`。

## [RUNTIME STATE]

當前Runtime State包括：

- travelers與bills；
- Todo items；
- Ticket completion；
- 使用者修改後的Ledger settings。

預設由當前瀏覽器localStorage按Trip ID儲存；localStorage不可用時退回當前標籤頁記憶體。只有`persistence.mode="d1"`且collection列入allowlist時才訪問Pages Function/D1。D1不應儲存靜態Travel Data、私人PDF、票據原件或原始檔。

## [PRIVACY]

Public Template不得包含：

- 真實Trip Data或Trip ID；
- 酒店地址、完整私人路線、真實日期/金額/訂單；
- Ticket PDFs、訂單截圖、源文件或私人D1匯出；
- secrets、tokens、private keys或真實Cloudflare identity；
- 私人Golden地圖assets、geometry、coordinates或queries；
- 未獲授權的照片、地圖或字型。

Demo必須完全虛構或明確獲准公開。`.gitignore`不是歷史清理工具；如果私人檔案曾被commit，建立新的乾淨Public Repo。

## Change Control

只有獨立框架維護任務才可以改變Frozen設計或產品行為，並且必須：

1. 先說明擬改變的Frozen合同。
2. 將架構修改與視覺/行為修改分開。
3. 對相關viewport、interaction和Ledger cases迴歸。
4. 更新對應spec與baseline。
5. 無法確認時停止並記錄，不順手修復潛在bug。

單次生成的預設驗收目標始終是：**Immutable Core + Confirmed modules + Verified facts + Generated maps + Local-first preview + Private sources excluded.**
