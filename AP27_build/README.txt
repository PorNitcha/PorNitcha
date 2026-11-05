AP2027 group consolidation deck (CEO), built 01-Nov-2026
1) python ap27_data.py ap27_data.json          (reads FC\comparison-data.json = P&L_AP2027-2028_LE9+3 file)
2) python ap27_deck_data.py ap27_data.json ap27_deck.json
3) powershell -File build_ap27.ps1 ap27_deck.json "<out>.pptx" <png dir>
   PowerPoint open? set $env:DECK_ALLOW_RUNNING_PPT=1 -> builds in a hidden presentation, never quits PowerPoint.

v3 (02-Nov-2026, Option B, TW template, Aptos) - numbers read straight from the Excel (ConsoAll = source of truth):
1) python read_sheets.py sheets.json          (ConsoAll + BU/entity sheets, FY cols by header row; prints BU vs ConsoAll reconciliation)
2) python ap27_v2_data.py sheets.json ap27_v2.json
3) python ap27_v2_text.py ap27_v2.json        (all sentences + appendix tables; asserts BUs + Corp/Elim = ConsoAll on every line)
4) powershell -File build_ap27_v3.ps1 ap27_v2.json "<out>.pptx" <png dir> <copy of Finance BU review pptx as template>

v4 (02-Nov-2026): run v3 steps 1-3, then  python ap27_v4_data.py sheets.json ap27_v2.json  and  build_ap27_v4.ps1 (same arguments as v3).
v4 hides Corp & BU elim everywhere in the CEO deck (management buffer); totals stay ConsoAll. No reconciliation slide (it named Corp/ElimBU).
v5 (02-Nov-2026): same pipeline as v4 (read_sheets -> ap27_v2_data -> ap27_v2_text -> ap27_v4_data), builder build_ap27_v5.ps1. Scenarios now include 2024 Rebase (key R24).
v6 (02-Nov-2026): builder build_ap27_v6.ps1 (same data pipeline as v5).
v7 (02-Nov-2026): after ap27_v4_data.py run  python ap27_v7_data.py sheets.json ap27_v2.json  then build_ap27_v7.ps1 (16 slides incl. 6 BU deep dives with per-kg takeaways). read_sheets.py also reads 2023 (Y23) and FoodTH.Dom / FoodTH.Exp.
v8 (02-Nov-2026): Por edited v7 by hand -> NEVER rebuild over it. Flow: (1) dump_deck.ps1 Por file + my rebuild, diff_decks.py to see what Por changed; (2) build_ap27_v8.ps1 to a scratch deck (after add_target.py); (3) merge_v8.ps1 copies Por file to the new name and swaps in only the changed slides (7, 9-16) via InsertFromFile, re-applying Por deletions (source lines, slide 10 note).
v9 (02-Nov-2026): python admin_v9.py sheets.json ap27_v2.json (after the v8 steps), build_ap27_v9.ps1 to scratch, then merge_one.ps1 <v8> <scratch> <v9> 7 <png> swaps slide 7 only.
v10 (04-Nov-2026, admin p7-8 of AP27 Finance deck_5Nov): python admin_bridge.py <BU Review_Admin.xlsx> bridge.json; build_admin_v10.ps1 (v9 header + v10_pages.ps1) builds the 2 slides to scratch; merge_78.ps1 <copy of 5Nov deck> <scratch> <out> <png> swaps slides 7 and 8 only. Deck in SharePoint folder was locked -> always work from a copy.
v11 (04-Nov-2026, 5Nov deck v3 p7-9): admin_bridge.py -> bridge.json; admin_v9.py (TWIC in INTER) + admin_sheet7.py (slide-7 table straight from BU Review_Admin) -> ap27_v2.json; build_admin_v11.ps1 = v9 header + v9 section 7 (footnote patched) + v11_pages.ps1 (P / Non-P waterfalls item-for-item from Waterfall_TH); merge_v3.ps1 swaps slides 7-9 into a copy of Por v2.
v12 (04-Nov-2026, 5Nov deck v5 = in-place edits on a copy of Por v4, no rebuild/merge): read_sheets.py now also reads the 'Idle' line -> sheets.json; edit_v5.ps1 -Src <copy of v4> -Out <v5> -PngDir <png> -Sheets sheets.json -Bridge bridge.json -Admin2 ap27_v2.json : (A) slides 4,10-16 insert 'of which: idle cost' row under Cost of sales (shift rows below by one pitch, grow tint rects, Duplicate() the cost-row shapes); (B) slide 6 drop 'of which TDC 2.0' row, re-space columns, add AP27 Stretch column (AP27 less Waterfall_TH Saving); (C) slides 7-8 recolour waterfall to deck tone and round every number from bridge.json values (not from the 1-decimal text), p.7 -> p.6. Verify with dump_deck.ps1 + diff_decks.py (run python -X utf8): only slides 4,6,7,8,10-16 differ.
v13 (04-Nov-2026, 5Nov deck v6): edit_v6.ps1 -SourceDeck <copy of v5> -OutDeck <v6> -PngDir <png> -BridgeJson bridge.json : slide 6 right card -> Admin Thailand bridge table (P-Cost | Non-P | Admin TH) built from bridge.json (Waterfall_TH), tie-checked; all other slides untouched (diff vs the source copy).
v14 (05-Nov-2026, 5Nov deck v7): python read_sheets2.py sheets_new.json <P&L_..._final_breaklink.xlsx>; edit_v7.ps1 -DeckIn <copy of Por v5> -DeckOut <v7> -PngDir <png> -NewJson sheets_new.json -OldJson sheets.json [-DryRun] : recomputes every numeric cell on slides 2/3/4/10 (tables, slide-2 bars/oval/title/commitments, slide-3 OPBA table + insight), aborts on format drift (report in edit_v7_report.txt). 'Other op. income & FX' = OP - OPBA - admin (plug). sheets.json in the scratchpad now = final workbook (old copy: sheets_old_breaklink_02Nov.json).
v15 (05-Nov-2026, 5Nov deck v8): edit_v8.ps1 -DeckIn <copy of v7> -DeckOut <v8> -PngDir <png> -SheetsJson sheets.json : slide 3 numeric columns shifted 56pt left, '2028 AP' OPBA column cloned from the 2027 AP cells (values from sheets.json, final workbook).
