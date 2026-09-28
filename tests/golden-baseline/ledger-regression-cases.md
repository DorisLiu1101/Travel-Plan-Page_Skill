# Golden Ledger Regression Cases

版本：Phase 0 / Round 2  
金額單位：除顯示值外，所有 Expected均為integer cents。  
預設Traveler ID順序：`A < B < C < D < E`；participantIds按題目書寫順序。

## Test Harness Rules

- 測試必須比較完整 `{paidCents, owedCents, netCents}` 和有序 transfers，而非只比較總額。
- 不得用浮點金額構造內部expected。
- 每個case至少執行兩層：純Ledger/fake repository，以及當前D1 adapter integration。Settings case必須明確區分兩層。
- `[CODE-CONFIRMED]` 表示結果可從當前函式精確推出；`[UNVERIFIED-INTEGRATION]` 表示仍需真實瀏覽器/D1測試。
- 對相同金額的排序依賴Traveler ID `localeCompare`；測試ID不可隨機，否則tie-break不可復現。

## CASE 01 — A支付100.00，ABCD參與

**Status:** `[CODE-CONFIRMED]`

**Given**

- Travelers：A、B、C、D。
- Bill：payer A，`baseAmountCents=10000`，participants `[A,B,C,D]`。

**When** 計算split、members和settlement。

**Expected**

| Member | Paid | Owed | Net |
|---|---:|---:|---:|
| A | 10000 | 2500 | +7500 |
| B | 0 | 2500 | -2500 |
| C | 0 | 2500 | -2500 |
| D | 0 | 2500 | -2500 |

有序 transfers：`B→A 2500`、`C→A 2500`、`D→A 2500`。

## CASE 02 — B支付100.00，BCD參與，驗證餘數

**Status:** `[CODE-CONFIRMED]`

**Given** Bill payer B，`10000` cents，participants `[B,C,D]`。

**When** equal split。

**Expected**

- `floor(10000/3)=3333`，remainder `1`。
- participantIds首位B承擔 `3334`；C與D各 `3333`。

| Member | Paid | Owed | Net |
|---|---:|---:|---:|
| A | 0 | 0 | 0 |
| B | 10000 | 3334 | +6666 |
| C | 0 | 3333 | -3333 |
| D | 0 | 3333 | -3333 |

Transfers：`C→B 3333`、`D→B 3333`。

## CASE 03 — 100.01，ABC參與，驗證cents remainder

**Status:** `[CODE-CONFIRMED]`

**Given** Bill payer A，`10001` cents，participants `[A,B,C]`。

**When** equal split。

**Expected**

- Base share `3333`，remainder `2`。
- A=`3334`，B=`3334`，C=`3333`。
- Net：A `+6667`，B `-3334`，C `-3333`。
- Transfers：`B→A 3334`、`C→A 3333`。

## CASE 04 — A/B多筆付款

**Status:** `[CODE-CONFIRMED]`

**Given**

- Bill 1：A支付 `12000`，participants `[A,B,C,D]`。
- Bill 2：B支付 `9000`，participants `[B,C,D]`。

**When** 計算累計balance。

**Expected**

| Member | Paid | Owed | Net |
|---|---:|---:|---:|
| A | 12000 | 3000 | +9000 |
| B | 9000 | 6000 | +3000 |
| C | 0 | 6000 | -6000 |
| D | 0 | 6000 | -6000 |

有序 transfers：`C→A 6000`、`D→A 3000`、`D→B 3000`。

## CASE 05 — 複雜debt，驗證minimum transfer而非greedy

**Status:** `[CODE-CONFIRMED]`

**Given**

- Bill 1：B支付 `4000`，participant `[C]`。
- Bill 2：A支付 `3000`，participant `[D]`。
- Bill 3：A支付 `3000`，participant `[E]`。

形成：A `+6000`、B `+4000`、C `-4000`、D `-3000`、E `-3000`。

**When** settlement遞迴搜尋。

**Expected**

- 初始最大額配對 `C→A` 會需要4筆，因此演算法必須繼續搜尋。
- 最少結果為3筆，且按當前tie-break輸出：
  1. `C→B 4000`
  2. `D→A 3000`
  3. `E→A 3000`

## CASE 06 — 單人賬單

**Status:** `[CODE-CONFIRMED]`

**Given** A支付 `10000`，participants `[A]`。

**When** 計算。

**Expected** A paid=`10000`、owed=`10000`、net=`0`；total=`10000`；transfers為空。

## CASE 07 — 編輯bill amount

**Status:** `[CODE-CONFIRMED]`

**Given** 原bill：A支付 `9000`，participants `[A,B,C]`；ID=`bill-1`。

**When** amount編輯為 `12000` 並儲存。

**Expected**

- bill ID與createdAt不變；updatedAt改變。
- original/base amount均為 `12000`（base currency bill）。
- A paid=`12000`、owed=`4000`、net=`+8000`；B/C各owed=`4000`、net=`-4000`。
- Transfers：`B→A 4000`、`C→A 4000`。

## CASE 08 — 編輯payer

**Status:** `[CODE-CONFIRMED]`

**Given** `10000` cents，participants `[A,B]`，原payer A。

**When** payer改為B。

**Expected**

- 修改前：A `+5000`、B `-5000`。
- 修改後：A `-5000`、B `+5000`。
- 修改後transfer：`A→B 5000`。

## CASE 09 — 編輯participants

**Status:** `[CODE-CONFIRMED]`

**Given** A支付 `10000`；原participants `[A,B]`。

**When** participants改為 `[A,B,C]`。

**Expected**

- 修改前shares A/B=`5000/5000`。
- 修改後shares A/B/C=`3334/3333/3333`。
- 修改後net：A `+6666`、B `-3333`、C `-3333`。
- Transfers：`B→A 3333`、`C→A 3333`。

## CASE 10 — 刪除bill

**Status:** `[CODE-CONFIRMED]`

**Given** 只有CASE 01的一筆bill。

**When** 使用者確認刪除且save成功。

**Expected** bills為空；total=`0`；A/B/C/D paid/owed/net均為0；transfers為空；travelers保留。

**And** 使用者取消confirm時任何state、updatedAt、API均不變。

## CASE 11 — 刪除被引用traveler

**Status:** `[CODE-CONFIRMED]`

**Given** A是payer或participant，且至少一筆bill引用A。

**When** 點選刪除A。

**Expected**

- 不出現刪除confirm。
- 不呼叫adapter.save。
- A與bill保持不變。
- Live notice提示需先處理相關賬單。

## CASE 12 — Duplicate traveler name

**Status:** `[CODE-CONFIRMED]`

**Given** 已有 traveler name=`Alice`。

**When** 新增 ` alice ` 或把另一成員改名為 `ALICE`。

**Expected** trim + locale lowercase後相等，操作被拒絕、focus姓名、顯示duplicate notice、不呼叫save。

**And** `A lice`不因內部空格而判重；Unicode normalization不屬於當前duplicate演算法。

## CASE 13 — Foreign currency

**Status:** `[CODE-CONFIRMED]`

**Given** baseCurrency=`CNY`；建立EUR bill：original=`100.00`，手動converted base=`780.50`，payer A，participants `[A,B]`。

**When** 儲存和計算。

**Expected**

- `currency="EUR"`
- `originalAmountCents=10000`
- `baseAmountCents=78050`
- split基於base：A=`39025`、B=`39025`
- A paid=`78050`、owed=`39025`、net=`+39025`；B net=`-39025`
- 列表顯示原幣金額，並額外顯示摺合CNY；settlement使用CNY `39025`。
- 不進行自動匯率計算。

## CASE 14 — 修改baseCurrency：無bill / 已有bill

**Status:** `[CODE-CONFIRMED]`，含已知integration issue。

### 14A 無bill，settings-capable fake repository

**Given** defaults且bills為空。

**When** base選擇EUR。

**Expected** base=`EUR`；EUR從common移除；last=`EUR`；顯示成功notice。

### 14B 已有bill

**Given** 至少一筆bill。

**When** 嘗試修改base。

**Expected** settings button disabled；即使直接觸發action也拒絕、提示已有賬單，settings不變、無save。

### 14C 當前D1 adapter

**Given** 無bill且使用Golden D1 adapter。

**When** base選擇EUR。

**Expected current issue** POST不含settings change；server返回`settings:null`；normalize後回到defaults。此結果用於記錄當前bug，不得作為未來正確產品預期。

## CASE 15 — commonCurrencies / lastCurrency

**Status:** `[CODE-CONFIRMED]`，含已知integration issue。

**Given** settings-capable fake repository，base CNY、common `[EUR,CHF,HKD]`、last CNY。

**When / Expected**

- 新增USD → common append USD，順序 `[EUR,CHF,HKD,USD]`。
- 再選USD → remove USD。
- 建立EUR bill → last=`EUR`。
- 移除當前last EUR → common不含EUR、last回退CNY。
- Edit一個CHF bill → last不改變。
- Base currency不能加入common。

**Current D1 integration Expected issue** 每次settings-only mutation響應`settings:null`並歸一化defaults；new bill雖設定last，server響應後last也回退default。

## CASE 16 — 重新整理頁面與持久化

**Status:** `[CODE-CONFIRMED]` for code path；真實部署仍需integration run。

**Given** 成功儲存travelers、bills，並嘗試修改base/common/last。

**When** reload並從當前D1 adapter載入。

**Expected**

| Field | 當前Golden持久化 |
|---|---|
| travelers | 是，逐record D1 |
| bills | 是，逐record D1 |
| baseCurrency | 否，回到default/normalization結果 |
| commonCurrencies | 否，回到defaults |
| lastCurrency | 否，回到base/default |

Todo/Ticket由同一API的其他collection持久，但不屬於Ledger snapshot normalization。

## CASE 17 — 同一瀏覽器快速連續mutation

**Status:** `[CODE-CONFIRMED]`

**Given** 連續觸發M1、M2、M3，adapter使用可控deferred promises。

**When** 三個mutation快速入隊。

**Expected**

- save呼叫嚴格按M1→M2→M3，不併行。
- M2在M1成功後clone包含M1的最新ledgerData。
- 若M1失敗，M2仍會執行，基於M1之前最後成功state。
- 每次成功各發一次changed event；失敗不發且顯示notice。

## CASE 18 — 兩裝置修改不同bill

**Status:** `[UNVERIFIED-INTEGRATION]`

**Given** Device 1與Device 2載入同一snapshot；D1新增/修改不同bill ID。

**When** 兩端先後POST。

**Expected from current code** 每個client diff只包含自己變更的record；server record-level upsert合併不同ID，後響應snapshot應包含兩端records。

**Verify** 網路順序、D1 batch結果、兩端本地snapshot是否只有發起mutation的一端立即看到合併結果；另一端需下一次save/reload才更新。

## CASE 19 — 兩裝置修改同一bill

**Status:** `[UNVERIFIED-INTEGRATION]`

**Given** 兩裝置載入同一 `bill-1`，分別改不同欄位或金額。

**When** 兩個完整payload先後upsert同一 `(trip_id,id)`。

**Expected from current code** 後到達寫入覆蓋先到達payload；無revision、ETag、field merge、衝突提示或自動重試。舊裝置之後再次儲存同record可再次覆蓋新值。

此“last write wins”是當前實現記錄，不是Frozen正確行為。

## Acceptance Summary

- Cases 01–13、17的演算法/互動結果必須在重構前後完全一致。
- Cases 14–16需同時保留“產品邏輯合同”和“當前D1 settings bug”兩層expected；修復bug前Golden integration應匹配當前記錄，修復必須另獲批准並更新baseline。
- Cases 18–19在真實D1驗證前保持 `[UNVERIFIED-INTEGRATION]`，不得宣稱已透過。
