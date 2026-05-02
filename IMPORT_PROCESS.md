# Excel Import Process - How Data is Imported

## Complete Import Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STEP 1: SELECT FILE                              │
├─────────────────────────────────────────────────────────────────────────┤
│  • User clicks "📥 Import Excel" button                                  │
│  • File browser opens → select Excel file                               │
│  • If multiple sheets: select which sheet to import                     │
│  • Identify header row (usually row 1-5)                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      STEP 2: COLUMN MAPPING                              │
├─────────────────────────────────────────────────────────────────────────┤
│  System auto-matches Excel columns to database fields:                   │
│                                                                          │
│  Excel Column          →    Database Field                               │
│  ─────────────────────────────────────────                               │
│  "Product Name"        →    name                                         │
│  "SKU"                 →    sku                                          │
│  "Category"            →    category                                     │
│  "Brand"               →    brand                                        │
│  "Stock" / "Qty"       →    stock                                        │
│  "Price" / "Cost"      →    cost_price / price_normal                    │
│                                                                          │
│  User can manually adjust mappings if needed                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 3: PREVIEW & ANALYSIS                            │
├─────────────────────────────────────────────────────────────────────────┤
│  System analyzes ALL data WITHOUT importing yet:                         │
│                                                                          │
│  📊 IMPORT SUMMARY:                                                      │
│     • Total products to import: 1,181                                    │
│     • New categories to create: 54                                       │
│     • New brands to create: 25                                           │
│     • Existing SKUs to update: 5                                         │
│                                                                          │
│  📦 SAMPLE PRODUCTS (First 10):                                          │
│     ┌─────────────────┬──────────┬───────┬───────┬──────────┐           │
│     │ Name            │ Category │ Brand │ Stock │ Price    │           │
│     ├─────────────────┼──────────┼───────┼───────┼──────────┤           │
│     │ Pulsar 220 Tyre │ Tyres    │ MRF   │ 8     │ ₹2,500   │           │
│     │ Brake Pad       │ Others   │ BAJAJ │ 12    │ ₹350     │           │
│     │ ...             │ ...      │ ...   │ ...   │ ...      │           │
│     └─────────────────┴──────────┴───────┴───────┴──────────┘           │
│                                                                          │
│  ⚠️  ERRORS (if any):                                                    │
│     • Row 15: Missing required field 'name'                              │
│     • Row 42: Invalid price format                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 4: USER CONFIRMATION                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│     [✓ Proceed with Import]        [✗ Cancel Import]                    │
│                                                                          │
│  • Click PROCEED → Data is saved to database                            │
│  • Click CANCEL → Nothing changes, dialog closes                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓ (if PROCEED)
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 5: ACTUAL IMPORT                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FOR EACH ROW in Excel:                                                  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ 1. GET OR CREATE CATEGORY                                       │     │
│  │    IF category "Air Filter" doesn't exist:                      │     │
│  │       → CREATE new category in database                         │     │
│  │    ELSE:                                                        │     │
│  │       → USE existing category ID                                │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                    ↓                                     │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ 2. GET OR CREATE BRAND                                          │     │
│  │    IF brand "BAJAJ" doesn't exist:                              │     │
│  │       → CREATE new brand in database                            │     │
│  │    ELSE:                                                        │     │
│  │       → USE existing brand ID                                   │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                    ↓                                     │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ 3. CHECK SKU                                                    │     │
│  │    IF SKU "AIR-BAJ-001" exists:                                 │     │
│  │       → UPDATE existing product                                 │     │
│  │    ELSE:                                                        │     │
│  │       → GENERATE new SKU (format: XXX-XXX-001)                  │     │
│  │       → CREATE new product                                      │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                    ↓                                     │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ 4. SAVE PRODUCT DATA                                            │     │
│  │    • name: "Pulsar 150 Air Filter"                              │     │
│  │    • sku: "AIR-BAJ-042"                                         │     │
│  │    • category_id: 6                                             │     │
│  │    • brand_id: 4                                                │     │
│  │    • stock: 15                                                  │     │
│  │    • cost_price: 180.00                                         │     │
│  │    • price_normal: 250.00                                       │     │
│  │    • price_workshop: 250.00                                     │     │
│  │    • reorder_level: 10                                          │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  REPEAT for all rows...                                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      STEP 6: RESULTS                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ✅ Successfully imported 1,181 products!                                │
│                                                                          │
│  Summary:                                                                │
│  • 1,181 products added/updated                                          │
│  • 54 new categories created                                             │
│  • 25 new brands created                                                 │
│  • 0 errors                                                              │
│                                                                          │
│  [OK]                                                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    STEP 7: REFRESH INVENTORY                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  • Inventory table automatically refreshes                              │
│  • New products appear in the list                                      │
│  • Filter dropdowns update with new categories/brands                   │
│  • Summary cards update (Total, Low Stock, etc.)                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Features

### ✅ Safe Import

- **Preview first**: See everything before any database changes
- **Cancel anytime**: Close dialog without importing
- **No duplicates**: Updates existing products by SKU instead of creating duplicates

### 🔄 Smart SKU Handling

```
If SKU provided in Excel:
    → Use that SKU
    → Update product if SKU exists

If SKU is empty:
    → Auto-generate: CAT-BRN-001
    → Example: AIR-BAJ-001, BRA-HON-042
```

### 📊 Data Mapping Examples

| Your Excel Data     | →   | Database Field | Example Value      |
| ------------------- | --- | -------------- | ------------------ |
| Bikes names / Items | →   | name           | "Pulsar 150 (ASK)" |
| Company             | →   | brand          | "BAJAJ"            |
| Sheet name          | →   | category       | "Air Filter"       |
| Wholesale Price     | →   | cost_price     | 180.00             |
| Retail Price        | →   | price_normal   | 250.00             |
| Qty in Hand         | →   | stock          | 15                 |

### ⚠️ Error Handling

- **Missing required fields**: Row skipped, error logged
- **Invalid numbers**: Default to 0, continue import
- **Empty rows**: Automatically skipped
- **Summary shown**: All errors displayed at end

## For Your "Diwan Autoparts backup.xlsx"

Your file has:

- **~60 sheets** (each becomes a category)
- **Columns**: Company, Bikes names, Wholesale Price, Retail Price, Qty in Hand
- **~1,180 products** total

The import will:

1. Create categories from sheet names ("Acc Cable", "Air Filter", "Brake Shoe", etc.)
2. Create brands from "Company" column ("BAJAJ", "HONDA", "YAMAHA", etc.)
3. Generate SKUs like `ACC-BAJ-001`, `AIR-HON-042`, etc.
4. Map wholesale → cost_price, retail → price_normal
