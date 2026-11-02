AP2027 group consolidation deck (CEO), built 01-Nov-2026
1) python ap27_data.py ap27_data.json          (reads FC\comparison-data.json = P&L_AP2027-2028_LE9+3 file)
2) python ap27_deck_data.py ap27_data.json ap27_deck.json
3) powershell -File build_ap27.ps1 ap27_deck.json "<out>.pptx" <png dir>
   PowerPoint open? set $env:DECK_ALLOW_RUNNING_PPT=1 -> builds in a hidden presentation, never quits PowerPoint.
