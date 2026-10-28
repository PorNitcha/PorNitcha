TWIN_build - TWIN (Indonesia) customer profitability, 2 layers (TDC manufacturer + TWIN trading) + FX (Oct 2026)
Inputs (export first with openpyxl, copy the xlsx via PowerShell if Por has it open):
  tdc_twin_rows.csv     = TDC Profitability_Act ... _AddPPA.xlsx / data_Actual, rows where Customer name (Group) = PT THAI WAH INDONESIA
  twin_rawww_2024.csv   = TWIN customer breakdown.xlsx / sheet "TWIN RAWww" (2024-01..2025-08, qty in kg, has Currency+Country)
  twin_raw_2025on.csv   = TWIN customer breakdown.xlsx / sheet "TWIN Raw data" (2025-01.., qty in tons)
Run:  python build_model.py <dir>            -> model.json (FX base = 2024 avg; BOT24 dict = assumed USD/THB for 2024)
      python build_xlsx.py  <dir> <out.xlsx> -> workbook (README / Summary / By customer / By customer-product / Quarterly trend / TDC product rates / FX / Data)
Notes: TDC GP per customer is allocated by product x quarter (TDC sells to TWIN as one customer). Non-TDC products (native, sago, ...) show TWIN layer only.
  python keyfindings_patch.py <dir> <out.xlsx> -> adds 'Key findings' sheet (run last)
  python keyfindings_patch.py <dir> <out.xlsx> -> adds 'Key findings' sheet (run last)

OUTPUT LOCATION (Por, 26-Oct-2026): save every analysis file to
  C:\Users\NitchaSuwongtham\THAIWAH\Commercial Finance - General\2026\04_FC\09 9+3\TWIN\analysis\\
  (not the TWIN root folder, which holds the source files). A copy in lovely\ is fine for the file pane.

FORMULA VERSION (v5, 26-Oct-2026): python build_formula_xlsx.py <dir> <out.xlsx>  -> every derived number is an Excel formula
  (Assumptions = inputs: base FX B5:B6, monthly FX, TDC monthly x SN, TDC rate table via SUMIFS; Data = TWIN lines + row formulas; other sheets = SUMIFS/INDEX).
  Then recalc + cache values + error scan:  powershell -File recalc_check.ps1 -Path <abs path> -OutJson <json>   (needs Excel; run from PowerShell, not git-bash)
  Values differ from the value version by <0.2% on TDC lines: the rate table includes zero-tonne rows (F&I-only) that build_model.py skipped.

26-Oct-2026 (v7): all worksheet text is ENGLISH (Por's instruction) - keep it English in every future version.
  Por's edits to the Data sheet 'country' column (used as a tag, e.g. Heinz / Wings) are stored in ..\memory\twin-customer-country.json
  and re-applied by build_model.py; By customer / By customer-product read country & currency from Data by formula; 'By country-tag' sheet summarises by that column.
  To sync new edits: copy Por's latest file, diff Data!country vs model, add to the json (see git history of _patch_country.py pattern).

FORMAT PROFILE (26-Oct-2026): Por's manual column groups / hidden columns / column-A highlights live in ..\memory\twin-format-profile.json
  and are re-applied by build_formula_xlsx.py on every build.  When Por re-formats a file: python sync_format_profile.py "<file Por edited>"
  (the profile is keyed by sheet name + column letter + column-A label, so keep the column layout identical between versions:
   By customer = 4 fixed cols + 27 metrics per period; By customer-product = 4 fixed cols (customer, product, currency, source)).

26-Oct-2026: sheet 'CFO one-page' (2nd tab) = Total / Heinz / Wings / The rest, YTD Sep-25 -> YTD Sep-26: KPI table, GP bridge
  (volume / price-cost-mix ex-FX / FX split 3 ways), 5 hypotheses with live evidence + verdict formulas. Groups = tag in Data!H.
  Print area set to fit one landscape page.

26-Oct-2026 (v8): sheet 'Indonesia portfolio' (Por's handwritten template) + 'Data TDC SN'.
  python extract_tdc_sn.py <tdc.xlsx> <dir>  -> tdc_sn.csv (ALL TDC customers by month x segment x customer x SN; segment = TWIN / Indonesia direct / Non-Indonesia)
  build_model.py keeps country_src (source country before Por's tag) -> Data col BC; portfolio TWIN rows = country_src = Indonesia.
  Order: extract_tdc_sn.py -> build_model.py <dir> excl -> build_formula_xlsx.py -> recalc_dump_sheet.ps1 (PowerShell).

27-Oct-2026 (v9): sheet 'CEO summary' (tab 4): A by channel / B by customer / C by product (SN), TDC direct vs TDC->TWIN->customer side by side,
  YTD Sep-25 vs YTD Sep-26, benchmark = Total TDC full GP/kg on the same SN mix, gap = Indonesia - benchmark (negative = red).
  Indonesia portfolio: direct customers now also one summary line + SN breakdown (outline); port_rows registry links the CEO sheet to the portfolio rows.

28-Oct-2026: memory/twin-customer-country.json also holds 'pinned_customers' (label prefixes always shown as their own line, e.g. GARUDAFOOD) - edit there, not in code.

28-Oct-2026 (v13): Por hand-edited the CEO summary sheet (column B inserted, short customer names, route-to-market rows, reaction column).
  From v13 on HER FILE IS THE MASTER: do not rebuild it with build_formula_xlsx.py. To refresh data: regenerate tdc_sn.csv / model rows,
  then overwrite only the 'Data', 'Data TDC SN' and Assumptions monthly-FX rows inside her latest file (keep column layout), recalc with Excel.

28-Oct-2026: CEO one-picture of the GP/kg tiers: python tier_chart_svg.py <dir with tdc_cust_rx.csv> out.svg out.html  (pure Python, no matplotlib)
  then PNG via Edge headless:  msedge --headless=new --disable-gpu --hide-scrollbars --window-size=1500,660 --screenshot=out.png file:///.../out.html
  (tdc_cust_rx.csv is written by the inline export in the session; see add_tier_sheet.py for its columns). Floor/target/capacity are constants at the top of the script.
