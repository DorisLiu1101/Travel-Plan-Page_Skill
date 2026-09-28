# Standard Generation Workflow

狀態：保留的 advanced/canonical 流程；普通單檔案生成以根目錄 `SKILL.md` 為準。  
範圍：從使用者材料到本地標準預覽；不包含個性化改版、公開部署或雲資料庫配置。

## 1. Outcome

一次生成必須產出可在本地開啟的標準旅行網頁，同時滿足：

- 使用者只需要做兩輪集中確認；
- 單次旅行只替換配置、事實資料和該旅行資產；
- 頁面結構、視覺、互動和 Ledger 演算法來自凍結 Core；
- 缺失材料不會阻斷預覽，也不會被猜測；
- 原始材料和提取中間結果不會進入釋出目錄；
- 無網路、無 Cloudflare、無 D1 時，啟用的本地功能仍可使用；
- 生成耗時可以按階段解釋和復現。

## 2. Directory and privacy boundary

### Private work directory

放在釋出倉庫之外，由當前使用者單獨控制：

```text
<private-work-dir>/
├── source-files/          原始 PDF、圖片、票據、訂單等
├── source-facts.json      一次提取後的結構化事實與來源
├── canonical-travel-data.json  確認後的規範化構建輸入
└── working-notes/         可選的臨時 OCR、消歧和檢查記錄
```

這些檔案不得複製到模板、公開倉庫、Demo、Skill、references、測試 fixture 或共享快取。絕對路徑也不得寫入釋出資料。

### Publishable trip directory

單次生成只允許改變以下類別：

```text
trip-config.json           模組與持久化模式
travel-data.json           編譯後的Renderer資料
assets/...                 本次旅行獲授權使用的資產
reports/...                不含原始材料或秘密的生成/校驗報告
```

其餘檔案視為 Core 或框架工具。生成前後由 `schemas/core-integrity.json` 和 validator 比對。發生不一致時停止並報告；不得執行 `freeze` 將意外改動登記為正常。

## 3. Stage A — extract facts once

優先讀取 PDF 的文字層；只有無文字、表格錯位、影象承載關鍵資訊或低置信度頁面才做視覺/OCR檢查。不要反覆從頭閱讀同一份材料。

將結果寫入倉庫外的`source-facts.json`，其結構由`schemas/source-facts.schema.json`定義。至少保留：

- `sourceDocuments`及文件ID、media type、頁數；
- 每條事實的`sourceRefs`，指向文件頁碼或使用者確認；
- `issues`中的`missing-material / contradiction / uncertain / privacy-review`型別；
- issue的`open / resolved / accepted-for-preview`狀態；
- `confirmations.moduleSelection`與`confirmations.missingMaterials`兩輪結果。

若提取置信度不足，將其登記為`uncertain` issue，而不是增加Schema之外的自由欄位。

提取階段不生成 HTML，不畫地圖，不連線資料庫，也不改模板。

## 4. Round 1 — module confirmation

事實提取完成後，一次性向使用者展示七個模組。可以標註“材料中已檢測到 / 未檢測到”，但最終開關由使用者決定。

| Config key | 使用者看到的模組 | 關閉後的行為 |
|---|---|---|
| `flights` | 航班 | 不渲染、不導航、不初始化倒計時 |
| `overview` | 旅行總覽與路線地圖 | 不渲染國家總覽或路線地圖 |
| `itinerary` | 逐日行程 | 不渲染 Timeline 或每日入口 |
| `tickets` | 門票 | 不渲染票據狀態或開啟入口 |
| `todo` | Todo | 不渲染或初始化 Todo |
| `driving` | 自駕 | 不渲染租車、還車倒計時或駕駛提醒 |
| `ledger` | 記賬 | 不渲染或初始化 Ledger |

把確認值寫入 `trip-config.json > modules`。配置結構由 `schemas/trip-config.schema.json` 驗證。

Ticket卡片嵌在逐日行程中，因此`tickets=true`要求`itinerary=true`。在Round 1清楚說明這個依賴，並在進入Round 2之前解決衝突；不要等生成失敗後再追加一輪提問。

關閉模組只能透過 Config 生效。禁止為某個使用者刪除 section、導航、事件處理器或初始化程式碼。第一個可見 section 和導航順序由 Core 根據已啟用模組自動決定。

## 5. Round 2 — missing-material decision

只檢查已啟用模組。把所有缺失、矛盾或歧義合併成一次清單，每項說明：

- 缺什麼；
- 影響哪個模組或哪條事實；
- 是否阻止可靠顯示；
- 繼續預覽時會怎樣表示。

然後只讓使用者決定：

1. **現在補充材料**：等待使用者一次性補充，再合併進同一份 `source-facts.json`；
2. **繼續生成預覽**：把問題記錄為 accepted/open，並用“待補充 / 待確認”狀態完成頁面。

選擇預覽後，禁止：

- 用常識、搜尋結果或相似訂單補寫未知事實；
- 把多個候選地點壓成一個泛化城市點；
- 因一個交通班次未知而刪除已知起點、終點或途經點；
- 為了讓校驗透過而刪除使用者已確認的資訊；
- 在生成過程中拆成第三、第四輪零散確認。

只有當缺失項會導致安全風險、無法確定同名地點國家/城市，或無法生成任何有效結果時，才再次阻塞並說明原因。

## 6. Stage B — canonical trip data

根據兩輪確認生成：

```json
{
  "$schema": "./schemas/trip-config.schema.json",
  "schemaVersion": "1.0.0",
  "modules": {
    "flights": true,
    "overview": true,
    "itinerary": true,
    "tickets": true,
    "todo": true,
    "driving": true,
    "ledger": true
  },
  "persistence": {
    "mode": "local"
  }
}
```

上例只說明欄位結構；每個模組的布林值必須來自 Round 1，不能把示例值當作使用者選擇。

先在倉庫外生成`<private-work-dir>/canonical-travel-data.json`。它應遵守`references/travel-data-contract.md`和`schemas/travel-data.schema.json`支援的canonical形狀：

- 一個事實只有一個權威來源；
- Place、Day、Day Item、Ticket、Transport 等使用穩定 ID；
- 日程透過 ID 引用地點、票務和交通，不用顯示文字或陣列位置充當關係；
- 文字只是展示內容；
- Todo、Ticket 勾選狀態和 Ledger 賬目不進入靜態旅行事實；
- 未確認欄位保留明確狀態，不偽造成已確認值。

已保留但材料不全的航班必須寫成 `status="missing"` 的 typed placeholder，包含 `title + missingFields + issueIds`，不填寫猜測的起降資訊。已保留但沒有票據檔案的 Ticket 保留為 `materialStatus="missing"`。這兩種狀態都是第二輪“繼續預覽”的標準輸出，不是校驗逃生口。

## 7. Stage C — standardized maps

### Required inputs

每個保留的目的地國家需要：

- 使用者有權使用的國家邊界 GeoJSON，並記錄來源與許可；
- `trip.primaryDestinationCountries[]` 中的 ISO 3166-1 alpha-2 code；
- canonical Places 中的 `countryCode` 與 `geo.lat/lng`；
- Days 和 Day Items 對 Place/Transport 的明確引用；
- 已確認的訪問順序。

不要從顯示文案猜國家或地點，不要從私人 Golden 地圖反推 geometry，也不要用手寫貝塞爾曲線替代真實國家輪廓。

### Generation

```bash
node scripts/generate-map-package.mjs \
  --boundary /absolute/path/to/authorized-country-boundary.geojson \
  --data /absolute/path/to/private/canonical-travel-data.json \
  --country <ISO2> \
  --out assets/maps/<country>-region.json \
  --source <BOUNDARY_SOURCE_OR_URL> \
  --license <BOUNDARY_LICENSE>
```

生成器負責：

- 把準確國家邊界投影到固定 `1448×1086` 畫布；
- 輸出 Golden 風格底圖 SVG，而不是臨時卡通輪廓；
- 從 canonical geo Places 投影地點；
- 按引用順序生成 Overview route；
- 按 Day 生成 `dailyLayouts`、路線和 transport pins；
- 為每日地點計算帶padding的viewport，使城市內行程使用城市尺度，而不是整國尺度；
- 輸出確定性的預設標籤資訊；當前不承諾完整的自動collision求解；
- 記錄邊界來源、許可和生成引數，便於安全複用與復現。

自動路線表達的是地點之間的行程關係，不等同實時公交、步行或駕車導航。具體線路未確認時可以標記為待確認，但已知地點仍須顯示。需要真實路網時，應作為使用者明確要求的後續增強，不阻塞首版預覽。

相同國家的純邊界/風格底圖可快取，但快取不得包含任何使用者路線、日期、地點、地址或 query。僅在 source、license、projection、canvas 和 style fingerprint 一致時複用。

### Compile to renderer data

Map generator輸出 region package 後，使用固定 compiler 生成頁面實際讀取的 `travel-data.json`。`overview=true`時，每個目的地國家重複一次 `--region`；`overview=false`時省略 `--region`：

```bash
node scripts/compile-travel-data.mjs \
  --input /absolute/path/to/private/canonical-travel-data.json \
  --config trip-config.json \
  --region assets/maps/<country>-region.json \
  --out travel-data.json
```

Compiler負責把canonical entities/typed references與generated Map Packages轉換為現有Renderer需要的只讀shape。禁止手工複製欄位、改Renderer適配本次Trip，或把private source provenance帶入輸出。

## 8. Stage D — tickets and runtime modules

- Ticket 有本地 PDF/圖片且允許進入輸出資產時，使用站內預覽入口；不要把站內開啟偽裝成外部連結。
- 官方購買頁屬於外部連結，必須明確標識並安全地新開頁面。
- 缺少票據檔案時顯示待補充，不生成無效 URL。
- Todo 只裝載使用者確認的初始準備事項；執行時新增、完成和刪除屬於本地狀態。
- Driving 和 Ledger 只讀取 Config；無資料或關閉時不修改 Core。
- Ledger 的 cents、平分餘數、paid/owed/net 和最少轉賬演算法不得因旅行生成而改變。

## 9. Stage E — validation and preview

執行：

```bash
node scripts/validate-generation.mjs check \
  --source /absolute/path/to/private/source-facts.json \
  --profile preview
```

`check` 是預設命令；需要機器可讀結果時追加 `--json`。校驗至少覆蓋：

- Config/Data/Source Facts schema；
- 模組開關與資料、導航、初始化的一致性；
- stable ID 和 typed reference 完整性；
- 地圖國家、地點、路線、Daily bounds 與許可記錄；
- Core 檔案未改變；
- 釋出目錄沒有原始材料、秘密、Cloudflare identity 或私人工作路徑；
- accepted uncertainties 有對應頁面狀態。

然後執行：

```bash
node local-preview-server.mjs
```

`local-preview-server.mjs`是純靜態 GET/HEAD 伺服器，不提供 `/api/trip`，不寫本地資料檔案，也不連線 D1。可選 shared mode 的聯調必須在使用者明確選擇 D1 後使用 Cloudflare 開發環境，不得把普通本地預覽伺服器當作 D1 adapter。

開啟伺服器輸出的 `127.0.0.1` URL，驗證：

- 第一個啟用模組直接出現，無空 section；
- 所有啟用模組可用，關閉模組沒有 DOM 可見入口或後臺請求；
- Overview 與每個 Day 的地點、順序、範圍正確；
- Ticket 站內入口、Todo 和 Ledger 本地儲存可用；
- 移動端和桌面端無明顯溢位或互動失效。

釋出前另執行 `--profile publish`。它是釋出準備檢查，不代表已經部署。

## 10. Persistence boundary

預設：

```json
{
  "persistence": {
    "mode": "local"
  }
}
```

本地模式不訪問 `/api/trip`，不要求 Cloudflare，且不能顯示“未繫結 D1”錯誤。Todo、Ticket 狀態、Ledger 同行人、賬單和設定按 Trip ID 儲存在當前瀏覽器；瀏覽器儲存不可用時可退回本標籤頁記憶體。

D1 只用於使用者明確選擇的多人員、多裝置共享。啟用方式、限制與許可權邊界見 `deployment-guide.md`。靜態頁面存在 Ledger 並不意味著需要資料庫。

## 11. Performance budget

不計算等待使用者回覆的時間：

| Stage | Target |
|---|---:|
| PDF 文字提取與結構化 | 1–2 分鐘 |
| 兩輪結果合併與 canonical data | 約 1 分鐘 |
| 已準備/可複用國家邊界地圖 | 1 分鐘內 |
| 新國家邊界、投影和地圖包 | 2–4 分鐘 |
| 校驗與本地瀏覽器檢查 | 1–2 分鐘 |

常見任務目標 3–6 分鐘；首次新國家目標 5–10 分鐘。如果超過 10 分鐘，必須報告當前 stage、耗時、阻塞輸入和下一步，不得靜默重新設計頁面或反覆手工調整地圖。

## 12. Handoff contract

交付首版預覽時，最終訊息必須明確：

1. 已啟用/關閉模組和仍待補充內容；
2. 本地預覽地址與校驗結果；
3. “該地址只在本機預覽服務執行時可訪問，目前沒有公開部署”；
4. 釋出需要另走 GitHub + Cloudflare Pages 流程；
5. 普通本地使用和靜態釋出不需要資料庫；
6. 多人、多裝置共享 Ledger/Todo/Ticket 時，使用者需明確啟用並繫結自己的 Cloudflare D1；
7. 未經這次單獨授權，沒有執行 Git push、Cloudflare 部署、D1 建立、migration 或 binding。

首版交付後，使用者可以另開個性化最佳化階段。該階段的設計改動不得回寫公共 Skill、Demo 或其他使用者的模板。
