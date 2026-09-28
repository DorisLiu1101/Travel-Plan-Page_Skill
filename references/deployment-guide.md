# Deployment and Optional Shared State

狀態：使用者完成本地預覽後的可選操作。  
原則：生成、公開部署、雲端共享是三次獨立決定；前一步不自動授權後一步。

## 1. Local preview is the default result

在模板目錄執行：

```bash
node local-preview-server.mjs
```

開啟終端實際輸出的 `http://127.0.0.1:.../` 地址；預設埠被佔用時，以伺服器輸出的後續埠為準。

這是本機預覽地址：

- 只有本地伺服器執行時可訪問；
- 預設不會被網際網路訪問；
- 不是 GitHub 或 Cloudflare 的線上部署；
- `trip-data.json > config.persistence.mode = "local"` 時，Todo、Ticket 狀態與 Ledger 資料只儲存在當前瀏覽器。

生成完成後，Agent 必須先交付這個結果，並明確詢問/等待使用者是否另行釋出。不得把“生成網頁”理解成已授權 Git push 或 Cloudflare 操作。

## 2. Before any deployment

執行釋出檢查：

```bash
npm run build:map
npm run validate
```

對於使用者自己的旅行內容，公開部署前只提醒一次“獲得連結的人可能檢視頁面內容”，並由使用者明確決定原樣釋出、處理選定內容或增加訪問保護。不得因為發現以下內容就自動刪除、隱藏、打碼或拒絕本地生成：

- 原始 PDF、票據、訂單截圖、護照或私人工作記錄；
- 二維碼、PNR、訂單號、聯絡人、未批准公開的地址或金額；

無論使用者如何選擇旅行內容，以下開發憑據都不得進入靜態頁面或公開倉庫：

- `.env`、`.dev.vars`、token、secret、private key；
- Cloudflare account ID、D1 database ID、binding ID、資料庫匯出；
- 瀏覽器匯出的runtime state或任何本地除錯資料；
- 未獲授權的地圖、圖片、字型或其他素材。

如果私人檔案曾提交到 Git 歷史，僅刪除工作區檔案不夠；應建立一個新的乾淨倉庫。

## 3. Publish with GitHub + Cloudflare Pages

靜態釋出不需要 D1。保持：

```json
{
  "persistence": {
    "mode": "local"
  }
}
```

步驟：

1. 在 GitHub 建立一個新的倉庫；公開或私人倉庫都可以連線 Cloudflare Pages。只提交透過 publish profile 的檔案。
2. 將本模板目錄作為站點根目錄推送到該倉庫。
3. 在 Cloudflare Dashboard 進入 **Workers & Pages → Create application → Pages → Connect to Git**。
4. 授權 Cloudflare 訪問這一個 GitHub 倉庫，選擇生產分支。
5. 這是無編譯的靜態站點：不要新增應用構建命令；把包含 `index.html` 的模板目錄設為輸出目錄。若倉庫根就是模板目錄，輸出目錄使用根目錄。
6. 完成首次部署，開啟 Cloudflare 提供的 `*.pages.dev` 地址，重新檢查模組、地圖和本地瀏覽器持久化。

Git 整合後，每次推送到生產分支都會觸發部署；其他分支可以產生獨立 Preview URL。以 Cloudflare 當前官方說明為準：

- [Cloudflare Pages Git integration](https://developers.cloudflare.com/pages/get-started/git-integration/)
- [Cloudflare Pages Git configuration](https://developers.cloudflare.com/pages/configuration/git-integration/)
- [GitHub: Creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)

### What local persistence means on a public site

網頁可以公開訪問，但每臺裝置、每個瀏覽器儲存的是自己的 Todo、Ticket 狀態和 Ledger 資料：

- 不同裝置不會自動同步；
- 清除該站點的瀏覽器資料會清除本機狀態；
- 不會因為部署到 Cloudflare Pages 就自動上傳到作者的資料庫；
- 頁面不應請求 `/api/trip`，也不應顯示“缺少 D1”錯誤。

如果這正是使用者想要的行為，到這裡已經完成，無需建立資料庫。

## 4. Opt in to user-owned Cloudflare D1

只有使用者明確提出“多人或多裝置共享 Todo、Ticket 或 Ledger”時，才進入本節。啟用 D1 前應再次說明：資料會寫入使用者自己的 Cloudflare 賬戶，且當前 API 的訪問控制限制見下文。

### 4.1 Configure the website

把 `trip-data.json > config.persistence` 改為以下結構，並只列出使用者明確要共享的 collection：

```json
{
  "persistence": {
    "mode": "d1",
    "apiBase": "/api/trip",
    "sharedCollections": ["todos", "tickets", "ledger"]
  }
}
```

配置必須符合 `schemas/trip-data.schema.json` 中的 `config` 定義。`apiBase` 通常保持同源 `/api/trip`；只有部署架構明確不同並經使用者確認時才改變。不要自行增加 database ID、account ID、token、binding ID 或 secret。

### 4.2 Create the user's database

使用者可以在自己的 Cloudflare Dashboard 建立一個全新的 D1 database。不要複用模板作者、Agent 或其他專案的資料庫。

D1模板位於`optional/cloudflare-d1/`，不會隨普通靜態站點自動啟用。使用者明確選擇shared mode後，先把`optional/cloudflare-d1/functions/`複製到部署根目錄的`functions/`，再由使用者在D1 Console執行`optional/cloudflare-d1/migrations/0001_shared_trip_data.sql`，或在使用者明確授權遠端變更後使用Wrangler：

```bash
npx wrangler d1 execute <USER_DATABASE_NAME> \
  --remote \
  --file=./optional/cloudflare-d1/migrations/0001_shared_trip_data.sql
```

`<USER_DATABASE_NAME>` 必須由使用者提供或從其賬戶中確認，不能猜測。`--remote` 會修改雲資料庫；Agent 不得因使用者只要求生成或部署靜態頁面而自動執行。

參考：

- [Cloudflare D1 getting started](https://developers.cloudflare.com/d1/get-started/)
- [Wrangler D1 commands](https://developers.cloudflare.com/d1/wrangler-commands/)
- [Cloudflare D1 migrations](https://developers.cloudflare.com/d1/reference/migrations/)

### 4.3 Bind D1 to the Pages project

在使用者自己的 Cloudflare Pages 專案中：

1. 開啟 **Settings → Bindings → Add → D1 database bindings**；
2. Variable name 填 `DB`；
3. 選擇使用者剛建立的 D1 database；
4. 儲存後重新部署，使 binding 生效。

倉庫不儲存這個 binding 指向的 database ID。生產環境和 Preview 環境的 binding 分開檢查。參考 [Cloudflare Pages bindings](https://developers.cloudflare.com/pages/functions/bindings/#d1-databases)。

`local-preview-server.mjs`是純靜態GET/HEAD伺服器，不提供`/api/trip`，也不會接觸D1。需要本地聯調shared mode時，必須在使用者已明確選擇D1後使用Cloudflare開發環境；例如在已複製`functions/`的部署根執行：

```bash
npx wrangler pages dev . --d1 DB=<USER_DATABASE_ID>
```

佔位ID必須來自使用者自己的Cloudflare資源，並且不能提交到倉庫。普通local mode不需要Wrangler。

### 4.4 Verify before sharing

確認部署根目錄已包含從可選模板複製出的`functions/api/trip/`，然後重新部署並檢查：

- `trip-data.json > config.persistence.mode` 明確為 `d1`，且 collection allowlist 正確；
- `/api/trip/<trip-id>` 返回預期 JSON，不洩露其他 Trip；
- 兩臺裝置對已啟用 collection 的新增、編輯和刪除能夠同步；
- 未加入共享 allowlist 的狀態仍只留在瀏覽器；
- 重新整理和網路失敗時頁面不會把讀取失敗誤報為空資料。

## 5. Security boundary

`metadata.tripId` 只是資料分割槽鍵，不是密碼。當前 Pages Function 沒有使用者登入、記錄級授權或衝突合併機制。若站點和 API 對公網開放，知道站點與 Trip ID 的訪問者理論上可能讀寫共享資料。

因此：

- 不要在 D1 存票據原件、二維碼、訂單號、護照或其他高敏感資料；
- 需要私密共享時，應在釋出前由使用者選擇 Cloudflare Access 或另行實現經過確認的認證；
- 同一記錄被多裝置同時修改時，可能發生後寫覆蓋；
- Ledger 的幣種設定當前仍可能保持瀏覽器本地，而不是跨裝置共享，具體以 `golden-ledger-spec.md` 為準。

認證、訪問策略或衝突控制都是單獨的產品/部署任務，不能因“啟用了 D1”而自動擴大授權範圍。

## 6. Required deployment handoff

如果只完成本地預覽，使用清晰措辭：

> 當前提供的是本地預覽地址，只在你的電腦上且預覽服務執行時可訪問，並未公開部署。若要釋出為網頁，請另行按 GitHub + Cloudflare Pages 流程操作。普通靜態釋出不需要資料庫；只有需要多人、多裝置共享記賬、Todo 或 Ticket 狀態時，才需要明確啟用並繫結你自己的 Cloudflare D1。

如果完成了公開部署，則另外報告：

- 線上 URL；
- GitHub repository 與 production branch；
- `persistence.mode`；
- 是否存在 D1 binding，以及它屬於哪個使用者專案（不得輸出秘密或完整 ID）；
- 已執行哪些 migration；
- API 是否有認證保護及已知風險。
