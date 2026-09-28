# Golden Ledger Specification

基線日期：2026-09-10  
事實來源：Golden Version `ledger.js`、當前local-first runtime storage與可選D1 adapter。

## 0. Contract Boundary

- **[FROZEN BEHAVIOR]**：成熟 Ledger使用者行為。
- **[FROZEN ALGORITHM]**：相同有效輸入必須產生完全相同的 cents結果、成員初字和 settlement結果。
- **[CURRENT IMPLEMENTATION]**：當前儲存/檔案組織或容錯路徑，允許未來經批准替換，但必須做迴歸。
- **[CONFIRMED ISSUE] / [POTENTIAL BUG] / [UNVERIFIED]**：不凍結為正確產品規則，詳見 `known-issues.md`。

重構不得以浮點金額重新實現 cents演算法，也不得用普通 greedy settlement替代當前最少轉賬搜尋。

## 1. Data Model

### 1.1 Snapshot

**[CURRENT IMPLEMENTATION]** normalized snapshot：

```text
version: 1
settings:
  baseCurrency: currency code
  commonCurrencies: currency code[]
  lastCurrency: currency code
travelers: Traveler[]
bills: Bill[]
updatedAt: ISO timestamp
```

Travel Todo/Ticket雖與同一 API snapshot並存，但不進入 Ledger `normalizeData()` 結果。

### 1.2 Traveler

```text
id: string
name: trimmed string, max 30 characters on create/edit/load
initial: derived display character
color: #RRGGBB uppercase
```

### 1.3 Bill

```text
id: string
originalAmountCents: positive safe integer
baseAmountCents: positive safe integer
currency: supported uppercase currency code
category: 餐飲 | 交通 | 住宿 | 門票 | 購物 | 其他
note: trimmed string, max 160 characters
orderedAt: datetime-local string or empty string
payerId: existing Traveler ID
participantIds: unique existing Traveler ID[], at least one
createdAt: ISO timestamp
updatedAt: ISO timestamp
```

`originalAmountCents` 表達 bill currency金額；`baseAmountCents` 是統計與結算所用金額。二者均為整數 cents。

## 2. Traveler

### 2.1 Create

**[FROZEN BEHAVIOR]**

- 姓名先 trim；空姓名不建立、focus姓名欄位、顯示 notice。
- 與現有 active traveler重複則不建立。
- name儲存最多前30個字元；initial由儲存前輸入按規則計算。
- color為合法六位hex時轉 uppercase儲存，否則使用 `nextAvatarColor()`。
- 新 ID透過 `makeId("person")` 產生。
- 新成員加入時先捕獲未提交 bill draft，並把新ID加入 draft participants。
- 儲存成功後 dialog保持 members open並顯示成功 notice；儲存失敗不提交本地 traveler。

### 2.2 Rename / Color Edit

**[FROZEN BEHAVIOR]**

- Members dialog的“編輯”切換為內聯 edit form並focus姓名。
- 空姓名拒絕；重複姓名拒絕。
- 成功時 name截到30字元、重新計算initial；合法color才覆蓋原color。
- Traveler ID保持不變，因此現有 bill引用繼續有效。
- 儲存成功後結束 edit state；失敗保留上一個已儲存狀態。

### 2.3 Duplicate Name

**[FROZEN ALGORITHM]**

```text
candidate = trim(name).toLocaleLowerCase()
duplicate = any traveler other than ignoredId
            whose trim(traveler.name).toLocaleLowerCase() === candidate
```

- 比較忽略首尾空白和大小寫。
- 不做 Unicode normalization、內部空白摺疊或同音/別名判斷。
- Create notice與Rename notice文案不同，但均阻止 mutation。
- Load normalization不會主動合併歷史同名 traveler；重複檢查只發生在 create/edit操作。

### 2.4 Delete

**[FROZEN BEHAVIOR]**

- 若 traveler是任一 bill的 payer或出現在participantIds中，立即阻止刪除、顯示 notice；不會顯示 confirm、不會傳送 mutation。
- 未被引用時呼叫瀏覽器 `confirm("刪除同行人…？")`；取消則無變化。
- 確認後從未提交 bill draft的participants移除該ID；若其為draft payer則清空payer。
- 儲存成功後從 travelers移除；members dialog保持開啟。

### 2.5 ID Generation

**[CURRENT IMPLEMENTATION]**，唯一性語義為 **[FROZEN BEHAVIOR]**。

- 首選 `${prefix}-${crypto.randomUUID()}`。
- 無 randomUUID時退回 `${prefix}-${Date.now()}-${8位base36隨機}`。
- normalize load時，空ID或重複ID會重新生成 `person-*`。

### 2.6 Avatar Initial

**[FROZEN ALGORITHM]**

1. `Array.from(trim(name))` 得到Unicode字元序列；空序列返回 `?`。
2. 查詢第一個 Unicode Han字元。
3. 若第一個Han為 `小`、`阿` 或 `老`，查詢其後的第一個Han；存在則返回該字元。
4. 否則返回第一個Han。
5. 若沒有Han，返回遇到的第一個 ASCII Latin `[A-Za-z]` 的uppercase。
6. 若沒有Han或Latin，返回第一個字元的uppercase結果。

示例：`小明 → 明`、`阿華 → 華`、`老張 → 張`、`王小明 → 王`、`alice → A`、`123b → B`。

### 2.7 Avatar Color

**[FROZEN ALGORITHM]** palette順序：

```text
#D96C42, #217D91, #5C8E62, #8B6AA8, #C58B32,
#4F72A2, #B85F76, #4E8F86, #9A6B4F, #68798E
```

`nextAvatarColor(travelers)`：

1. 把active travelers colors轉uppercase放入Set。
2. 返回palette中第一個尚未使用的顏色。
3. 若全部已用，返回 `palette[travelers.length % 10]`。

Load normalization對合法hex uppercase；缺失/非法時按 traveler index迴圈 palette。顏色避免重複只適用於新增建議色，不會改寫使用者主動選出的重複顏色。

## 3. Bill

### 3.1 Create

**[FROZEN BEHAVIOR]**

- 沒有 travelers時不渲染 bill form，只顯示 onboarding。
- 新 bill預設：currency=`lastCurrency`；category=`餐飲`；participants=所有當前 travelers；payer為空。
- 表單必須透過 currency、original amount、foreign base amount、category、payer、至少一位participant校驗。
- participantIds去重並過濾不存在的 traveler。
- 成功建立 `bill-*` ID、createdAt/updatedAt為同一當前ISO時間；append到bills。
- 新建bill時把 `settings.lastCurrency`設為本次currency。
- 儲存成功後清除bill draft和edit state；失敗不提交 ledgerData。

### 3.2 Edit

**[FROZEN BEHAVIOR]**

- 點選編輯時捕獲當前new-bill draft，切換Entry tab、重渲染為edit form，平滑滾動到entry card並focus amount。
- edit form以原 bill currency、amounts、category、note、orderedAt、payer、participants初始化。
- 儲存時保留 ID與createdAt，只覆蓋欄位與updatedAt。
- Edit不會更新 `lastCurrency`。
- 若另一bill已在完整編輯，拒絕切換並提示先儲存或取消。
- 取消編輯只清除editingBillId並重渲染；不儲存修改。

### 3.3 Delete

**[FROZEN BEHAVIOR]**

- 刪除前呼叫 `window.confirm("刪除這筆賬單？")`。
- 取消無變化。
- 確認並儲存成功後移除該ID，重新計算list/stats/settlement。
- 若該bill的inline note editor開啟，先清除note edit state。

### 3.4 Date / Ordering

**[FROZEN BEHAVIOR]**

- `orderedAt`可空，來自 `datetime-local`，當前不附加獨立timezone。
- Bill list排序key=`orderedAt || createdAt`，按字串 descending。
- 顯示時有效日期用 `Intl.DateTimeFormat("zh-CN", month/day/hour/minute, 24h)`；無法解析則把 `T` 替換為空格。
- Stats計算遍歷 `ledgerData.bills` 當前陣列順序，但加法結果與順序無關；related bill展示沿billIds收集順序。

### 3.5 Category

**[FROZEN BEHAVIOR]**

- 有效值固定為：餐飲、交通、住宿、門票、購物、其他。
- Form必須選中有效分類；load時非法/未知分類歸為“其他”。

### 3.6 Note 與 Inline Note Edit

**[FROZEN BEHAVIOR]**

- Full form note可空、trim、最多160字元。
- Inline editor開啟時focus並select；相同bill已完整編輯則轉到full note欄位。
- 點選其他區域/action時先flush；切換到另一note前先儲存當前note。
- note未變化時直接關閉editor，不傳送mutation。
- 儲存期間form標記saving且controls disabled。
- 成功後同步full form note（若存在）、恢復trigger並顯示“已更新/已清空”。
- 失敗後editor保持、controls重新啟用、顯示錯誤notice；後續依賴action被阻止。
- Escape或取消按鈕放棄未儲存值。

### 3.7 Payer / Participants

**[FROZEN BEHAVIOR]**

- Payer為單選且必須引用active traveler；payer不必屬於participants。
- Participants為多選、去重、至少一人；賬單允許單人參與。
- “全選”按鈕：若存在任何未選成員則全選；若全部已選則全不選。
- Split summary：無人時提示至少一人；金額無效時僅提示人數/平分；有效時顯示 `floor(baseAmountCents / participantCount)` 的“每人約”金額，不展示remainder差異。

## 4. Amount Storage and Validation

### 4.1 Input Grammar

**[FROZEN ALGORITHM]** `toCents(value)`：

1. 轉字串、trim、刪除所有逗號。
2. 必須匹配 `^(?:\d+|\d*\.\d{1,2})$`。
3. 整數部分乘100；小數右補零至2位後相加。
4. 結果必須是 JavaScript safe integer，否則返回invalid。

由此：

- `100`、`100.0`、`100.00`、`.5`、`1,000.25`有效。
- 空、單獨`.`、負數、正號、科學記數、三個以上小數、非數字無效。
- Form另要求 cents `> 0`；`0`、`0.00`拒絕。

### 4.2 Integer Cents Invariant

**[FROZEN ALGORITHM]**

- `originalAmountCents` 與 `baseAmountCents`均為正safe integer。
- Equal split、paid、owed、net、total、settlement全程使用integer cents。
- 僅顯示/輸入邊界使用除100與兩位小數格式化。
- 未來實現不得在演算法中儲存或累加浮點金額。

### 4.3 Base / Foreign Amount

**[FROZEN ALGORITHM]**

- Bill currency等於baseCurrency：`baseAmountCents = originalAmountCents`，converted field隱藏並清空。
- Bill currency不同：必須手動輸入正的converted base amount；Core不計算匯率。
- `originalAmountCents/currency`保留原幣事實；stats/settlement只使用`baseAmountCents`。

## 5. Equal Split

**[FROZEN ALGORITHM]** 精確定義：

```text
validParticipantIds = bill.participantIds 中仍存在的 traveler，保持陣列順序
n = validParticipantIds.length
baseShare = floor(baseAmountCents / n)
remainder = baseAmountCents - baseShare * n

依次遍歷 validParticipantIds：
  amount = baseShare + (remainder > 0 ? 1 : 0)
  若分配了1 cent，remainder -= 1
```

- 餘數按 `participantIds` 陣列順序從前到後分配，每人最多多1 cent。
- Map插入順序保持participants順序。
- 無有效participants返回空Map；正常form不允許建立該狀態，但load normalization可能過濾非法記錄。

例：`10000 / [B,C,D]` → `B=3334, C=3333, D=3333`。  
例：`10001 / [A,B,C]` → `A=3334, B=3334, C=3333`。

## 6. Paid / Owed / Net Balance

**[FROZEN ALGORITHM]** 對每個 traveler：

```text
paidCents = Σ bill.baseAmountCents where bill.payerId == traveler.id
owedCents = Σ billShares(bill)[traveler.id]
netCents  = paidCents - owedCents
```

- `netCents > 0`：creditor，UI“應收”。
- `netCents < 0`：debtor，UI“應付”。
- `netCents = 0`：neutral，UI“已結清”。
- `totalCents = Σ all bill.baseAmountCents`。
- `billIds`包含該成員付款或參與分攤的bill，每個ID最多一次。

## 7. Settlement / Minimum Transfer

### 7.1 Input Sets and Sorting

**[FROZEN ALGORITHM]**

- Debtor：`netCents < 0`，amount=`-netCents`。
- Creditor：`netCents > 0`，amount=`netCents`。
- Debtors先按amount descending，再按traveler ID `localeCompare` ascending。
- Creditors使用相同排序。
- Neutral不進入搜尋。

### 7.2 Recursive Search

**[FROZEN ALGORITHM]**

1. 在debtAmounts中找第一個 `>0` 的 debtor；不存在則返回空transfer list。
2. Memo key為 `debtAmounts.join(",") + "|" + creditAmounts.join(",")`。
3. Lower bound為當前正debt數量與正credit數量的較大值。
4. 按creditor陣列順序嘗試；跳過 `<=0`。
5. 在同一遞迴層，餘額相同的creditor amount只嘗試第一個（`triedCreditAmounts`剪枝）。
6. 本次transfer=`min(firstDebtorDebt, selectedCredit)`；分別扣減後遞迴。
7. Candidate為當前transfer加遞迴結果。
8. 僅當candidate transfer數量嚴格更少時替換best；相同長度保留先遇到的candidate。
9. 若best長度達到lower bound，立即停止該層後續creditor嘗試。
10. Memoize best或空陣列。

### 7.3 Determinism and Tie-breaking

**[FROZEN ALGORITHM]**

- 第一個未清debtor由已排序陣列決定。
- Credit嘗試順序由creditor排序決定。
- Equal outstanding amount在每層只嘗試第一個，因此ID升序決定代表者。
- Equal-length方案不會覆蓋先遇到方案。
- 最終輸出保持遞迴生成順序，不做二次排序。
- Transfer對映回 `{fromId,toId,amountCents}`。

### 7.4 Required Result

演算法目標是當前搜尋空間內的最少transfer數量，而非簡單最大額greedy。未來可以重構實現，但對同一規範化輸入，transfer數量、順序、from/to與amount cents必須完全一致。

### 7.5 Complexity

**[CURRENT IMPLEMENTATION]** 使用memoization和同額credit剪枝，但成員多時仍可能出現組合搜尋開銷。效能最佳化不得改變輸出tie-break。

## 8. Multi-Currency

### 8.1 Defaults and Available Currencies

**[CURRENT IMPLEMENTATION]** defaults：

```text
baseCurrency = CNY
commonCurrencies = [EUR, CHF, HKD]
lastCurrency = CNY
```

- Available bill currencies為base + common +當前extra bill currency的去重集合。
- Settings normalization只保留catalog已知code；common中移除base並去重。
- last必須屬於base/common，否則回退base。

### 8.2 Base Currency

**[FROZEN BEHAVIOR]**

- 無bill時允許選擇新base；選擇後從common移除該code並將last設為新base。
- 有至少一筆bill時settings按鈕disabled；action層也再次拒絕並提示。
- 鎖定意圖是避免歷史converted base cents失真。

### 8.3 Common Currencies

**[FROZEN BEHAVIOR]**

- Base不能作為common選擇。
- 搜尋支援code、中文名、英文名、symbol與aliases，normalize NFKD、小寫並刪除空白/點/下劃線/斜槓/連字元；最多展示24項。
- 選擇未加入code則append；選擇已加入code則remove。
- 從common移除當前last時，last回退base。

### 8.4 Last Currency

**[FROZEN BEHAVIOR]**

- 僅在建立新bill時設為本次currency。
- 新bill form優先使用draft currency，否則使用last。
- Edit bill不更新last。

### 8.5 Settings Persistence

- **[CURRENT IMPLEMENTATION]** 預設local mode按Trip ID在當前瀏覽器儲存settings、travelers與bills；重新整理同一瀏覽器後恢復。
- **[CONFIRMED ISSUE]** 顯式D1 mode仍不把settings同步到雲端；settings保持當前瀏覽器本地，不能承諾跨裝置一致。這不屬於`[FROZEN ALGORITHM]`。

## 9. Form Draft and UI State

**[FROZEN BEHAVIOR]**

- New-bill draft包含currency、兩個amount輸入、category、note、orderedAt、payerId、participantIds。
- 開啟dialog、切tab、進入member編輯等會capture draft；重新渲染後恢復。
- 新增成員成功時加入draft participants；刪除成員時從draft清除。
- 進入完整bill edit前儲存new-bill draft；取消/完成edit後可回到draft。
- Draft、editing IDs、open dialog、currency query、notice只存在記憶體，不跨reload。

## 10. Mutation Queue and Failure

### 10.1 Queue

**[FROZEN BEHAVIOR]**

```text
queued = previousQueue.then(operation, operation)
mutationQueue = queued.catch(() => {})
```

- 同一頁面內Ledger mutations按觸發順序序列。
- 前一mutation失敗不會永久阻斷後續mutation。
- 普通 `mutateData` 在輪到執行時clone最新一次成功的`ledgerData`。

### 10.2 Commit Semantics

**[FROZEN BEHAVIOR]**

- 普通Ledger CRUD/settings：clone → mutate next → adapter.save → success後normalize/replace state/render/event。
- Save失敗：記錄console，顯示“儲存失敗…”notice，保留上一次成功的ledgerData，不發changed event。
- 成功：發 bubbling `travel-ledger:changed`，包含tripId、reason與snapshot clone。
- Inline note使用同一queue但有專門saving/disabled/failure恢復邏輯。

## 11. Persistence Adapters

### 11.0 Selection contract

- **[FROZEN BEHAVIOR]** `persistence`缺失、非法或`mode="local"`時使用local adapter，不訪問`/api/trip`，不要求Cloudflare或D1。
- **[FROZEN BEHAVIOR]** localStorage按canonical Trip ID隔離；不可用時退回本標籤頁記憶體，Ledger仍可操作。
- **[FROZEN BEHAVIOR]** 只有`mode="d1"`且`ledger`列入`sharedCollections`時才啟用D1 adapter。
- D1必須由部署者在自己的Cloudflare賬戶中顯式建立/繫結；database/account/token/binding identity不得進入Trip Config或倉庫。

### 11.1 Optional D1 collections

**[CURRENT IMPLEMENTATION]**

- Ledger D1 adapter只同步`bills`、`travelers`；settings保留瀏覽器本地。
- 可選Cloudflare API還可存`todos`、`tickets`，但只有列入`sharedCollections`時才由Travel module同步。
- D1表主鍵均為 `(trip_id,id)`；bill另有 `(trip_id,created_at)` index。
- 沒有settings table、snapshot revision、mutation ID、user或conflict metadata。

### 11.2 Diff and Save Order

**[CURRENT IMPLEMENTATION]**

- Adapter持有上次server snapshot `previous`。
- 對bills/travelers分別構造before/after ID maps。
- before有、after無 → delete；after與before JSON不等 → upsert完整record。
- 單次POST傳送changes陣列；server使用D1 batch執行後返回完整snapshot。
- 遠端snapshot對`bills/travelers`是authoritative；runtime adapter在返回前合併當前瀏覽器的local settings，避免把D1的`settings:null`當成共享設定。

### 11.3 Normalize on Load

**[CURRENT IMPLEMENTATION]**

- 空/非object snapshot退回default。
- Traveler空name丟棄；空/重複ID重建；非法color按index palette。
- Bill original/base amount非正safe integer、currency未知、payer不存在或participants為空時整筆丟棄。
- Participant IDs去重並過濾不存在成員；category非法歸“其他”；note trim/160。
- 這些是當前防禦性容錯，不應代替未來schema validation。

### 11.4 D1 load failure

- **[FROZEN BEHAVIOR]** 顯式D1 load異常時顯示shared-state notice並保留安全的本地/預設normalized ledger，UI仍可操作；提示不得暗示使用者必須繫結模板作者的資料庫。
- **[POTENTIAL BUG]** 在尚未成功讀取遠端時繼續mutation的覆蓋/合併風險仍需失敗注入驗證。預設local mode不受此風險影響。

## 12. Concurrent Devices

### 12.1 Different Records

**[CURRENT IMPLEMENTATION]** 從程式碼推導：兩個已載入同一snapshot的裝置分別新增/修改不同bill ID時，各自diff只傳送所改ID；server record-level upsert後返回完整snapshot，因此通常合併兩條記錄。

### 12.2 Same Record

**[CURRENT IMPLEMENTATION]** 從程式碼推導：兩個裝置修改同一bill時，後到達的完整payload覆蓋先到達值；沒有revision/ETag/field merge/conflict提示。持有舊snapshot的裝置之後再次儲存該record，可能覆蓋對方修改。

- **[UNVERIFIED]** 以上兩種併發尚未在真實D1雙裝置環境執行；以 regression cases 18/19 作為驗證入口。
- 併發覆蓋行為不是 `[FROZEN BEHAVIOR]`，未來是否加入conflict control需使用者批准。

## 13. Dialog and Keyboard

**[FROZEN BEHAVIOR]**

- Members、Settings、Currency dialogs同時最多一個open。
- Open預設focus首個非color input/button；currency focus search。
- 點選dialog backdrop、close或native cancel關閉；currency close語義為返回Settings。
- Ledger tabs支援Left/Right切換並focus新tab。
- Inline note Escape取消。

**[CURRENT IMPLEMENTATION]** Ledger dialogs依賴native modal focus containment，無自定義trap或opener restore。

**[UNVERIFIED]** 關閉後的focus return、fallback `open`路徑和全瀏覽器keyboard行為。

## 14. Public API

**[CURRENT IMPLEMENTATION]** `window.TravelLedger`公開的Ledger入口仍包括：

- `init`
- `setActiveTab`
- `createLocalStorageAdapter`
- `createD1Adapter`（只供顯式D1 mode使用）
- `getPersistenceMode`
- `getSnapshot`（deep clone或null）

演算法函式當前未公開。未來建立演算法測試時可以抽出純函式或使用受控test harness，但抽取前後結果必須滿足本規範。
