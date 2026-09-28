# Target Travel Data Contract

狀態：Advanced/legacy canonical data contract；不屬於普通單檔案生成流程。  
用途：定義Trip Package中旅行事實的規範化邊界；單次生成只填寫資料，不修改Core來繞開合同。  
上位合同：`golden-contract.md`  
配套文件：`data-duplication-matrix.md`、`stable-id-proposal.md`、`data-migration-map.md`

## 1. Contract Principles

1. **One Fact, One Authoritative Source**：同一旅行事實只有一個可編輯來源；其他檢視從該來源派生。
2. **Identity is explicit**：實體與跨模組關係使用 stable ID，不使用陣列位置、顯示文字或 substring 推斷。
3. **Display text is presentation**：`title`、`text`、`note` 可以保留 Golden 文案，但不得承擔 identity。
4. **Trip facts are immutable input**：Todo、Ticket completion、Ledger 等使用者使用後狀態不寫回本合同。
5. **Normalized Core is destination-neutral**：Core不得識別具體國家、城市、Day編號或地點名；目的地差異透過canonical data和generated assets表達。
6. **Golden fixture remains lossless**：遷移當前資料時，所有現有可見內容、順序、地圖 geometry 和互動入口均須可表達。
7. **Public structure, private values**：欄位結構可以開源；真實旅行內容預設是私人值，不得因結構公開而釋出。

## 2. Notation

- `[PUBLIC-SAFE STRUCTURE]`：欄位名、型別、列舉和關係規則可進入公開 Core、Schema 與文件。
- `[PRIVATE VALUE]`：當前真實行程中的值預設留在 Private Trip Package；包括日期、路線、地址、訂單、金額和私人 query。
- `[REQUIRED]`：規範化 Trip Package 必須提供。
- `[OPTIONAL]`：僅在事實存在或模組需要時提供。
- `[DERIVED]`：由 validator/build step 計算，禁止作為第二個可編輯事實源。
- `[REFERENCE]`：值必須解析到指定 stable ID class。
- `[FIXTURE PRESENTATION]`：為保持當前 Golden 文案而允許保留；只用於顯示，不參與關聯。

本文以 TypeScript-like notation 表達邏輯模型。物件索引鍵就是 canonical ID；物件值中不再重複 `id`。

## 3. Top-level Shape

```ts
type TravelData = {
  schemaVersion: string;
  trip: Trip;
  entities: {
    places: Record<PlaceId, Place>;
    stays: Record<StayId, Stay>;
    flights: Record<FlightId, Flight>;
    flightGroups: Record<FlightGroupId, FlightGroup>;
    carriers: Record<CarrierId, Carrier>;
    tickets: Record<TicketId, Ticket>;
    transport: Record<TransportId, Transport>;
    rentals: Record<RentalId, Rental>;
    restaurants: Record<RestaurantId, Restaurant>;
  };
  days: Day[];
  map?: TripMap;
  preTrip?: { items: Record<PreTripItemId, PreTripItem> };
  issues?: Record<IssueId, TripIssue>;
};
```

`entities` 中的九類一級旅行實體是本輪的目標集合。空類別使用空 object；不得為渲染方便複製同一實體。

## 4. Common Scalar Types

```ts
type StableId = string;          // lowercase ASCII kebab-case, prefix required
type LocalDate = string;         // YYYY-MM-DD
type LocalTime = string;         // HH:mm or HH:mm:ss
type IanaTimeZone = string;      // e.g. Europe/Paris; validator checks IANA name
type CurrencyCode = string;      // ISO 4217 uppercase code
type MinorAmount = number;       // positive safe integer in currency minor units
type CountryCode = string;       // ISO 3166-1 alpha-2 uppercase code
type LocaleTag = string;         // BCP 47
type GeoPoint = { lat: number; lng: number };
```

共同約束：

- 日期與時間不得僅用 locale-dependent display string 表達。
- 航班起降、住宿入住/退房、租車取還車各自擁有發生地 `timeZone`。
- 金額的權威值使用整數 minor units；顯示字串與貨幣符號由 Core 派生。
- 能從實體計算的 duration、route text、night count 與 day count 不重複儲存。

## 5. Trip

| Field | Type | Rule | Ownership / visibility |
|---|---|---|---|
| `id` | `TripId` | `[REQUIRED]` canonical trip identity；Todo、Ticket與Ledger namespace從此派生，顯式shared mode才用於API/D1分割槽 | 結構公開；當前值 `[PRIVATE VALUE]` |
| `title` | `string` | `[REQUIRED]` 頁面主標題 | 當前值 `[PRIVATE VALUE]` |
| `language` | `LocaleTag` | `[REQUIRED]` 內容主語言；執行方式仍由 Config 決定 | 通常可公開，當前值仍屬 Trip Package |
| `startDate` | `LocalDate` | `[DERIVED]` 取最早 day/date 或顯式 event date | `[PRIVATE VALUE]` |
| `endDate` | `LocalDate` | `[DERIVED]` 取最晚 day/date 或顯式 event date | `[PRIVATE VALUE]` |
| `dayCount` | `number` | `[DERIVED]` 從 `days` 計算 | `[PRIVATE VALUE]` |
| `countries` | `CountryCode[]` | `[DERIVED]` 從 referenced places 計算，順序由首次行程出現確定 | `[PRIVATE VALUE]` |
| `primaryDestinationCountries` | `CountryCode[]` | `[OPTIONAL]` 產品語義，不總能從地點推斷 | `[PRIVATE VALUE]` |
| `groupSize` | `number` | `[OPTIONAL]` 行程規劃人數，不等同 Ledger travelers | `[PRIVATE VALUE]` |
| `status` | enum | `[OPTIONAL]` `draft | confirmed | completed | cancelled` | `[PRIVATE VALUE]` |
| `subtitle` | `string` | `[OPTIONAL]` `[FIXTURE PRESENTATION]` | `[PRIVATE VALUE]` |

下列現有欄位不再作為可編輯權威欄位：`nightCountAway`、`citiesAndAreas`、`routeSummary`。需要時由 Core/validator 生成 display view。

## 6. Entities

### 6.1 Place

`entities.places: Record<PlaceId, Place>` 是所有真實物理地點和導航目標的權威目錄。

| Field | Type | Rule |
|---|---|---|
| `name` | `string` | `[REQUIRED]` 預設顯示名稱 |
| `localizedNames` | `Record<LocaleTag, string>` | `[OPTIONAL]` 翻譯名稱，不是別名關聯表 |
| `category` | enum/string | `[REQUIRED]` 如 `country-region | city | airport | station | stay-premise | attraction | restaurant | rental-office | parking | other` |
| `countryCode` | `CountryCode` | `[OPTIONAL]` region 級抽象點可以省略 |
| `geo` | `GeoPoint` | `[OPTIONAL]` schematic map 或 provider link 需要時提供 |
| `address` | `string` | `[OPTIONAL]` `[PRIVATE VALUE]`；只在 Place 儲存一次 |
| `codes` | object | `[OPTIONAL]` 如 airport IATA/ICAO、station/provider code |
| `navigation` | provider map | `[OPTIONAL]` provider-specific query/place ID/URL；當前真實 query `[PRIVATE VALUE]` |
| `description` | `string` | `[OPTIONAL]` 顯示資訊，不用於關聯 |
| `privacy` | enum | `[OPTIONAL]` `public | private | sensitive`；預設按 `private` 處理真實 Trip Package |

約束：

- 機場、車站、酒店實際地點、餐廳、景點、租車門店和停車點均是 Place。
- Stay、Restaurant、Rental 不重複儲存其地址或導航 query。
- 一個概念地圖點需要開啟多個真實地點時，Map Feature 使用 `placeId + interactionPlaceIds[]`；不得把多個地點壓成一個混合 Place。

### 6.2 Stay

| Field | Type | Rule |
|---|---|---|
| `name` | `string` | `[REQUIRED]` 住宿訂單顯示名稱 |
| `placeId` | `PlaceId` | `[REQUIRED][REFERENCE]` 住宿實際地點 |
| `checkIn` | `LocalEvent` | `[REQUIRED]` date/time/timeZone；未知具體時間可使用 precision |
| `checkOut` | `LocalEvent` | `[REQUIRED]` 同上 |
| `provider` | `string` | `[OPTIONAL]` 預訂平臺/酒店渠道 |
| `bookingStatus` | enum/string | `[OPTIONAL]` |
| `guestCount` | `number` | `[OPTIONAL]` |
| `room` | object | `[OPTIONAL]` 房型、早餐、設施等事實 |
| `price` | `Money` | `[OPTIONAL][PRIVATE VALUE]` |
| `confirmation` | object | `[OPTIONAL][PRIVATE VALUE]` 訂單號、聯絡人、訪問說明 |
| `notes` | `string[]` | `[OPTIONAL][PRIVATE VALUE]` |

`nightCount` 為 `[DERIVED]`；address 與 navigation 從 `placeId` 獲取。

### 6.3 Carrier

| Field | Type | Rule |
|---|---|---|
| `name` | `string` | `[REQUIRED]` |
| `localizedNames` | map | `[OPTIONAL]` |
| `codes` | object | `[OPTIONAL]` IATA/ICAO/rail operator code |

Carrier 目錄消除每段航班內重複的 airline object。品牌 logo 若存在屬於 asset/config boundary，不嵌入身份欄位。

### 6.4 Flight

```ts
type FlightEndpoint = {
  placeId: PlaceId;
  localDate: LocalDate;
  localTime: LocalTime;
  timeZone: IanaTimeZone;
  terminal?: string;
};
```

| Field | Type | Rule |
|---|---|---|
| `carrierId` | `CarrierId` | `[REQUIRED][REFERENCE]` |
| `flightNumber` | `string` | `[REQUIRED]` |
| `departure` | `FlightEndpoint` | `[REQUIRED]` endpoint Place 應為 airport |
| `arrival` | `FlightEndpoint` | `[REQUIRED]` endpoint Place 應為 airport |
| `status` | enum/string | `[OPTIONAL]` booking/operational planning status |
| `cabin` | `string` | `[OPTIONAL]` |
| `booking` | object | `[OPTIONAL][PRIVATE VALUE]` PNR、ticket number 等 |
| `price` | `Money` | `[OPTIONAL][PRIVATE VALUE]` leg-level price only |
| `notes` | `string[]` | `[OPTIONAL]` |
| `issueIds` | `IssueId[]` | `[OPTIONAL][REFERENCE]` |

route、duration、跨日標記、airport name/city/country 均 `[DERIVED]`。Flight 不再儲存 `journeyId` 或 `sequence`；分組順序由 Flight Group 的 `flightIds[]` 表達。

若使用者保留航班模組，但關鍵航班材料缺失，並在第二輪選擇繼續預覽，該實體改用明確的 missing union：

```ts
type MissingFlight = {
  status: "missing";
  title: string;
  missingFields: string[];
  issueIds: IssueId[];
};
```

Missing Flight 不得同時填入猜測的 `carrierId`、`flightNumber`、`departure` 或 `arrival`。Compiler 只會生成不帶倒計時的待補充卡；`issueIds` 必須指向已被第二輪接受繼續預覽的 Issue。

### 6.5 Flight Group

當前資料存在 group-only booking facts，因此保留輕量 `flightGroups`，而不是把所有 group 都當作純派生檢視。

| Field | Type | Rule |
|---|---|---|
| `flightIds` | `FlightId[]` | `[REQUIRED][REFERENCE]` 有意義的有序陣列；每個 ID 只出現一次 |
| `title` | `string` | `[OPTIONAL][FIXTURE PRESENTATION]` |
| `bookingStatus` | enum/string | `[OPTIONAL]` |
| `travelerCount` | `number` | `[OPTIONAL]` |
| `fare` | `Money` | `[OPTIONAL][PRIVATE VALUE]` group-level fare only |
| `notes` | `string[]` | `[OPTIONAL]` group-level facts only |

route、stops、departure、arrival、total duration 與 leg count 均 `[DERIVED]`，不得與 Flight 再維護一份。

### 6.6 Ticket

| Field | Type | Rule |
|---|---|---|
| `name` | `string` | `[REQUIRED]` |
| `category` | enum/string | `[OPTIONAL]` attraction/transport/pass/reservation 等 |
| `requirement` | enum/string | `[OPTIONAL]` booking/entry requirement |
| `initialStatus` | enum | `[OPTIONAL]` `needed | planned | booked | not-needed`；不是使用者完成狀態 |
| `placeIds` | `PlaceId[]` | `[OPTIONAL][REFERENCE]` ticket 覆蓋的地點 |
| `transportIds` | `TransportId[]` | `[OPTIONAL][REFERENCE]` ticket 覆蓋的交通 leg |
| `validity` | object | `[OPTIONAL]` date/time/timeZone 或日期範圍 |
| `price` | `Money` | `[OPTIONAL][PRIVATE VALUE]` |
| `booking` | object | `[OPTIONAL][PRIVATE VALUE]` provider、confirmation、document asset ref |
| `guidance` | `string[]` | `[OPTIONAL]` |
| `issueIds` | `IssueId[]` | `[OPTIONAL][REFERENCE]` |

Ticket 不儲存 `day`、`scheduleMatchTerms` 或完成 boolean。出現在哪個 itinerary item 由 `item.ticketIds[]` 指定；使用者勾選結果屬於 Runtime State，以 `ticketId` 為 key。

### 6.7 Transport

| Field | Type | Rule |
|---|---|---|
| `mode` | enum/string | `[REQUIRED]` `drive | rail | metro | bus | boat | cable-car | walk | transfer | other` |
| `fromPlaceId` | `PlaceId` | `[OPTIONAL][REFERENCE]` |
| `toPlaceId` | `PlaceId` | `[OPTIONAL][REFERENCE]` |
| `viaPlaceIds` | `PlaceId[]` | `[OPTIONAL][REFERENCE]` travel order |
| `departure` | `LocalEvent` | `[OPTIONAL]` |
| `arrival` | `LocalEvent` | `[OPTIONAL]` |
| `durationMinutes` | `number` | `[OPTIONAL]` only when authored fact; otherwise `[DERIVED]` |
| `operatorId` | `CarrierId` | `[OPTIONAL][REFERENCE]` |
| `service` | object | `[OPTIONAL]` train number、route name、reservation rule |
| `rentalId` | `RentalId` | `[OPTIONAL][REFERENCE]` drive leg 使用的租車訂單 |
| `status` | enum/string | `[OPTIONAL]` planning status |
| `notes` | `string[]` | `[OPTIONAL]` |
| `issueIds` | `IssueId[]` | `[OPTIONAL][REFERENCE]` |

Road leg 與 public-transit row 統一為 Transport entity。Day item 引用它；schedule text、map pin 和 cost tag 不再各寫一份。

### 6.8 Rental

| Field | Type | Rule |
|---|---|---|
| `provider` | `string` | `[REQUIRED]` 當前品牌屬於 Trip Data，不屬於 Core |
| `pickup` | `RentalEvent` | `[REQUIRED]` `placeId + localDate + localTime + timeZone` |
| `dropoff` | `RentalEvent` | `[REQUIRED]` 同上 |
| `vehicle` | object | `[OPTIONAL]` class/model/transmission/fuel facts |
| `bookingStatus` | enum/string | `[OPTIONAL]` |
| `price` | `Money` | `[OPTIONAL][PRIVATE VALUE]` |
| `booking` | object | `[OPTIONAL][PRIVATE VALUE]` confirmation/contact |
| `requirements` | `string[]` | `[OPTIONAL]` |
| `notes` | `string[]` | `[OPTIONAL]` |
| `issueIds` | `IssueId[]` | `[OPTIONAL][REFERENCE]` |

Rental 的門店地址和 provider query 位於 referenced Place。倒計時直接使用 pickup/dropoff events，不讀取 HTML 文案或固定 UTC offset table。

### 6.9 Restaurant

Restaurant 保留為一級實體，因為餐廳可能同時參與日程、預訂準備和導航。

| Field | Type | Rule |
|---|---|---|
| `placeId` | `PlaceId` | `[REQUIRED][REFERENCE]` name/address/navigation 由 Place 提供 |
| `status` | enum/string | `[OPTIONAL]` planned/reserved/walk-in/cancelled |
| `mealKinds` | `string[]` | `[OPTIONAL]` |
| `specialties` | `string[]` | `[OPTIONAL]` |
| `reservation` | object | `[OPTIONAL][PRIVATE VALUE]` date/time/provider/confirmation |
| `notes` | `string[]` | `[OPTIONAL]` |

## 7. Day and Daily Item

```ts
type Day = {
  id: DayId;
  sequence: number;
  date: LocalDate;
  title: string;
  subtitle?: string;
  stayId?: StayId;
  items: DayItem[];
  notes?: string[];
};
```

### 7.1 Day Rules

- `[REQUIRED]` `id`、`sequence`、`date`、`title`、`items`。
- `sequence` 只決定展示順序，不是 identity；不得由 `days[4]` 表示 Day 5。
- `stayId` 表示該日結束後的住宿。無住宿或跨夜交通時可以省略。
- `weekday`、`locations`、`costReferences`、ticket pending count 均 `[DERIVED]`。
- `items` 是有意義的有序陣列；每一項仍有獨立 `DayItemId`。

### 7.2 Day Item

```ts
type DayItem = {
  id: DayItemId;
  type: string;
  time: ItemTime;
  title: string;
  text?: string;
  note?: string;
  tag?: string;
  placeId?: PlaceId;
  placeIds?: PlaceId[];
  stayId?: StayId;
  flightId?: FlightId;
  ticketIds?: TicketId[];
  transportId?: TransportId;
  rentalId?: RentalId;
  restaurantId?: RestaurantId;
  issueIds?: IssueId[];
};
```

每個 normalized Day Item 還必須暴露有效 `date`。為保持 One Fact：

- serialized package 以 parent `Day.date` 為唯一權威日期；item 不重複寫相同日期；
- normalize step 將 `effectiveDate = day.date` materialize 給 Core；
- 只有真正跨日且 event entity 不能表達時，item 才允許 `dateOverride`，並必須透過 validator 說明原因；
- 因此 Core contract 中 item 有明確 date，但 raw JSON 不維護第二份相同事實。

`ItemTime` 支援三種表達：

```ts
type ItemTime =
  | { kind: "entity-event"; event: "departure" | "arrival" | "check-in" | "check-out" | "pickup" | "dropoff" }
  | { kind: "local"; localTime: LocalTime; timeZone?: IanaTimeZone; precision?: "exact" | "approximate" }
  | { kind: "label"; label: string };
```

- `entity-event` 必須能由同一 item 的 `flightId`、`stayId` 或 `rentalId` 唯一解析。
- `label` 只用於“上午/全天/抵達後”等非精確事實，不得偽裝成可計算時間。
- `title` 是 `[REQUIRED]` 結構化摘要。
- `text`、`note`、`tag` 可保留當前 Golden 文案，但均為 `[FIXTURE PRESENTATION]`；Renderer 不得從其中查詢實體。

### 7.3 Type-specific Reference Constraints

| Item type | Required semantic reference |
|---|---|
| flight departure/arrival | exactly one `flightId`; `time.kind=entity-event` preferred |
| stay check-in/check-out | exactly one `stayId`; related `placeId` derived from Stay |
| transport | exactly one `transportId` |
| rental pickup/dropoff | exactly one `rentalId`; event identifies pickup/dropoff |
| restaurant meal | exactly one `restaurantId`; `placeId` derived from Restaurant |
| attraction/activity | at least one `placeId` or `placeIds`; optional `ticketIds[]` |
| free note/rest | no entity ref required |

Typed references may coexist when semantically necessary，例如 transport item 同時關聯 `ticketIds[]`；不得為 renderer 便利建立反向重複關係。

## 8. Trip Map Contract

Map Data 引用相同 Place、Transport、Day IDs；不得建立第二套地點 identity。

```ts
type TripMap = {
  mode: "custom-artwork" | "schematic";
  regions: Record<MapRegionId, MapRegion>;
  routes: Record<MapRouteId, MapRoute>;
  segments: Record<MapSegmentId, MapSegment>;
  customLayout?: CustomMapLayout;
  schematicInput?: SchematicMapInput;
};
```

### 8.1 Shared semantic layer

| Field | Type | Rule |
|---|---|---|
| `regions[*].title` | `string` | display only |
| `regions[*].countryCodes` | `CountryCode[]` | semantic region coverage |
| `routes[*].regionId` | `MapRegionId` | `[REFERENCE]` |
| `routes[*].dayId` | `DayId` | `[OPTIONAL][REFERENCE]` |
| `routes[*].segmentIds` | `MapSegmentId[]` | meaningful render order |
| `routes[*].colorKey` | `string` | Trip assignment to Frozen palette, not raw CSS override by default |
| `segments[*].fromPlaceId` | `PlaceId` | `[OPTIONAL][REFERENCE]` |
| `segments[*].toPlaceId` | `PlaceId` | `[OPTIONAL][REFERENCE]` |
| `segments[*].transportIds` | `TransportId[]` | `[OPTIONAL][REFERENCE]` |

### 8.2 `custom-artwork` （舊 Fixture / 單獨批准的精修模式）

該模式只用於無損保留已批准的舊 Golden fixture，或使用者在標準首版之後單獨批准的地圖精修。普通單次生成不能進入此模式手調座標。獲批的 Trip Map Package 可以提供：

- canvas width/height/viewBox；
- region artwork asset reference；
- route SVG paths；
- per-place x/y、label x/y、anchor、size、multiline；
- geographic annotations、heading、legend placement；
- daily layout keyed by `dayId`；
- place feature keyed by `MapFeatureId`，含 `placeId`、`role`、`interactionPlaceIds[]`；
- transport pin keyed by `MapFeatureId`，含 `transportIds[]` 和 manual x/y；
- `visibleRouteSegmentIds[]`，替代 SVG child position。

這些欄位屬於 `[CUSTOM TRIP ASSET]` 或 `[GOLDEN MAP FIXTURE]`。任一獲准保留的 Golden Map Package 輸入不變時，必須產生對應的 Golden result。

### 8.3 `schematic`

允許的 authored inputs：authorized region boundary asset/ref、`placeIds[]`、route/segment order 和 Place `geo`。`schematic` 不允許目的地特判。projection、normalization、route curve、確定性預設 label placement 與 Daily bounds 由當前 map generator 生成；首版不承諾完整 collision solver。Generated layout 可作為 build artifact 快取，但不能成為第二份手工旅行事實。

## 9. Pre-trip Items and Issues

### 9.1 Pre-trip Item

```ts
type PreTripItem = {
  type: "packing" | "reservation" | "document" | "reminder" | "other";
  title: string;
  note?: string;
  relatedRefs?: StableId[];
};
```

這是靜態規劃內容，不是使用者新增 Todo。Todo completion/add/delete 屬 Runtime State。現有 packing IDs 可遷移為 `PreTripItemId`；當前未被 UI 消費不等於可以靜默刪除。

### 9.2 Trip Issue

```ts
type TripIssue = {
  severity: "info" | "warning" | "error";
  status: "open" | "resolved" | "accepted-for-preview";
  title: string;
  detail?: string;
  relatedRefs: StableId[];
};
```

Issue 用 typed `relatedRefs` 指向事實源；不得在 `issuesAndUncertainties` 中複製完整航班、票務或租車事實。Issue 本身是 Trip authoring metadata，是否渲染由 Config/Core 能力決定。

## 10. Money and Private Booking Values

```ts
type Money = {
  currency: CurrencyCode;
  amountMinor: MinorAmount;
};
```

- 當前旅行的真實價格、PNR、confirmation、聯絡人、地址、私人文件路徑均 `[PRIVATE VALUE]`。
- Demo 可使用虛構值，但不得從真實 Trip Package 脫敏後猜測釋出。
- 公開 Schema 只描述型別與約束，不包含真實 examples。
- Ledger bills 不屬於 Travel Data，即使也使用 Money type。

## 11. Reference Integrity Contract

Build/validation 必須失敗的情況：

1. 任一 ID 不符合該 class 的 prefix/pattern。
2. 任一 object key 重複，或 ID 被修改後仍有舊引用。
3. `placeId`、`stayId`、`flightId`、`ticketIds`、`transportId`、`rentalId`、`restaurantId`、map/day refs 無法解析。
4. 同一實體被不允許地重複定義於兩類 entity map。
5. Flight endpoint 缺 date/time/timeZone 或引用非 airport-compatible Place。
6. Stay/Rental event 的 timeZone 缺失，且 normalize step 無合法來源。
7. Day `sequence` 重複、Day ID 重複、Item ID 在 trip 內重複。
8. `entity-event` 無法從 item 的 typed reference 唯一解析。
9. custom map 的 `visibleRouteSegmentIds`、place feature 或 transport pin 引用不存在。
10. Core-facing relation仍依賴 `matchTerms`、substring、schedule index、day array index、SVG child index 或 display name。

Warnings 而非 hard failure：可選 geo 缺失導致 schematic map 無法包含某地點；可選 provider query 缺失導致外部導航 unavailable。若配置啟用相關模組，則 warning 可提升為 error。

## 12. Derived Views

下列內容應由 normalize/build step 產生給 Renderer 的只讀 view，而不是回寫 Trip Package：

- Hero dates、day count、country/city summary、route summary；
- Flight Group route、stops、跨日標記、duration；
- Day weekday、location summary、cost tags；
- Ticket pending count 與 completed summary（結合 Runtime State）；
- Stay nights；
- Map overview/daily visibility；
- navigation actions；
- display currency/amount、localized dates/times。

Golden fixture 可以儲存 `text`/`title` overrides 以逐字保持頁面，但這些 overrides 不改變上述權威關係。

## 13. Public / Private Boundary

### `[PUBLIC-SAFE STRUCTURE]`

- 本文、當前JSON Schema、列舉、ID prefix、reference constraints；
- generic validator、normalizer、renderer；
- 完全虛構的 demo data 與授權公開 assets；
- schematic mode 的 generic inputs/output rules。

### `[PRIVATE VALUE]`

- 真實 `trip.id`、日期、人數、路線和 day schedule；
- 真實機場/住宿/餐廳/景點組合；
- 地址、navigation queries、訂單號、票據、價格、聯絡人；
- 任何私人 Golden Trip 的 custom artwork/coordinates/routes（按 Golden Contract 作為 private Trip asset 管理）；
- 任何由真實材料推導、足以還原私人旅行的 metadata。

Private values 必須從 public build allowlist 之外輸入；`.gitignore` 不是釋出邊界。

## 14. Remaining Product Decisions

這些決定不阻塞標準首版生成；需要擴充套件可見行為時另行確認：

1. **舊資料中只存在於規劃列表、未進入互動Ticket UI的記錄**：遷移時保留為Ticket entity，並只在有明確Day Item關係時掛`ticketIds`；本地票據與外部購買入口遵守Golden Behavior。
2. **Flight Group**：本合同建議保留輕量 authored group，因為當前有 group-only bookingStatus、fare 與 notes；若未來刪除，必須先決定這些事實的新權威歸屬。
3. **複合地圖點**：建議以一個概念anchor `placeId`配合`interactionPlaceIds[]`表達“城市錨點 + 酒店/車站/還車點”等複合目的地；每個點的primary interaction需在遷移fixture中逐一確認。
4. **未被當前 UI 消費的 preTrip packing 資料**：建議保留為可選靜態 Trip Data，不能在沒有產品決定時當作 dead data 刪除。

## 15. Current implementation boundary

- `schemas/travel-data.schema.json`定義當前可執行子集；本檔案可以描述比首版Renderer更完整的canonical方向，衝突時Schema優先。
- 單次Trip生成可以修改 `trip-config.json`、編譯後的 `travel-data.json`、該Trip獲授權的assets和reports，但不得修改Schema、normalizer、validator、renderer或map generator。
- Config負責module enablement；七個值來自第一輪確認。
- Runtime persistence與靜態Trip Data分離，預設local，D1為顯式opt-in。
- 任何資料架構工作不得改變Frozen UI、Behavior、Ledger Algorithm或Map Style。
