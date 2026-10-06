"""Builds india_data.js for india_sector_leadership.html.  pip install yfinance pandas
Run daily after market close:  python fetch_india_data.py
Edit SECTORS / THEMES freely. Tickers are Yahoo format (.NS = NSE, ^ = index)."""
import json, sys
import pandas as pd, yfinance as yf

INDICES = {  # optional "Indices" tab; Yahoo drops some of these, they are skipped if no data
    "Bank": "^NSEBANK", "IT": "^CNXIT", "Auto": "^CNXAUTO", "Pharma": "^CNXPHARMA",
    "FMCG": "^CNXFMCG", "Metal": "^CNXMETAL", "Realty": "^CNXREALTY", "Energy": "^CNXENERGY",
    "PSU Bank": "^CNXPSUBANK", "Financial Services": "^CNXFIN", "Media": "^CNXMEDIA",
    "Infrastructure": "^CNXINFRA", "PSE": "^CNXPSE", "Commodities": "^CNXCMDT",
}
SECTORS = {  # sector -> large NSE stocks (reliable on Yahoo). Edit freely.
    "Private Banks": ["HDFCBANK","ICICIBANK","AXISBANK","KOTAKBANK","INDUSINDBK","FEDERALBNK","IDFCFIRSTB","AUBANK","BANDHANBNK"],
    "PSU Banks": ["SBIN","BANKBARODA","PNB","CANBK","UNIONBANK","INDIANB","BANKINDIA","IOB"],
    "Financial Services": ["BAJFINANCE","BAJAJFINSV","SHRIRAMFIN","CHOLAFIN","MUTHOOTFIN","HDFCLIFE","SBILIFE","ICICIGI","PFC","RECLTD"],
    "IT": ["TCS","INFY","HCLTECH","WIPRO","TECHM","LTM","PERSISTENT","COFORGE","MPHASIS","OFSS"],
    "Pharma": ["SUNPHARMA","CIPLA","DRREDDY","DIVISLAB","LUPIN","ZYDUSLIFE","TORNTPHARM","AUROPHARMA","ALKEM","MANKIND"],
    "Auto": ["MARUTI","M&M","BAJAJ-AUTO","EICHERMOT","HEROMOTOCO","TVSMOTOR","ASHOKLEY","BOSCHLTD","MOTHERSON"],
    "FMCG": ["HINDUNILVR","ITC","NESTLEIND","BRITANNIA","DABUR","GODREJCP","MARICO","COLPAL","TATACONSUM","VBL"],
    "Metals": ["TATASTEEL","JSWSTEEL","HINDALCO","VEDL","JINDALSTEL","SAIL","NMDC","NATIONALUM","HINDZINC","APLAPOLLO"],
    "Realty": ["DLF","GODREJPROP","OBEROIRLTY","PRESTIGE","LODHA","PHOENIXLTD","BRIGADE","SOBHA"],
    "Oil & Gas / Energy": ["RELIANCE","ONGC","BPCL","IOC","GAIL","COALINDIA","HINDPETRO","OIL","PETRONET"],
    "Capital Goods": ["LT","SIEMENS","ABB","BHEL","CUMMINSIND","HAVELLS","POLYCAB","BEL","HAL","CGPOWER"],
    "Consumer Durables": ["TITAN","DIXON","VOLTAS","BLUESTARCO","CROMPTON","KALYANKJIL","HAVELLS","POLYCAB"],
    "Telecom": ["BHARTIARTL","IDEA","INDUSTOWER","TATACOMM","HFCL"],
    "Cement": ["ULTRACEMCO","GRASIM","AMBUJACEM","SHREECEM","DALBHARAT","ACC","JKCEMENT"],
    "Chemicals": ["PIDILITIND","SRF","UPL","DEEPAKNTR","NAVINFLUOR","TATACHEM","AARTIIND","PIIND","ATUL"],
}
THEMES = {  # theme -> list of NSE stocks (edit to taste)
    "Defence": ["HAL", "BEL", "BDL", "MAZDOCK", "COCHINSHIP", "BEML", "SOLARINDS"],
    "Railways": ["RVNL", "IRFC", "IRCON", "RAILTEL", "TITAGARH", "JWL", "TEXRAIL"],
    "Power T&D": ["POWERGRID", "SIEMENS", "POWERINDIA", "CGPOWER", "KEC", "KPIL", "APARINDS"],
    "Renewables": ["SUZLON", "INOXWIND", "NTPC", "TATAPOWER", "ADANIGREEN", "WAAREEENER", "PREMIERENE"],
    "Capital Mkts": ["BSE", "CDSL", "ANGELONE", "360ONE", "MCX", "KFINTECH", "CAMS"],
    "Hospitals": ["APOLLOHOSP", "MAXHEALTH", "FORTIS", "NH", "KIMS", "RAINBOW"],
    "EV & Auto Ancillary": ["EXIDEIND", "OLECTRA", "SONACOMS", "UNOMINDA", "JBMA", "TVSMOTOR", "MOTHERSON"],
    "Data Centers & AI Infra": ["ANANTRAJ", "NETWEB", "E2E", "TATACOMM", "HFCL", "STLTECH", "TEJASNET"],
    "Shipbuilding & Ports": ["COCHINSHIP", "MAZDOCK", "GRSE", "ADANIPORTS", "JSWINFRA", "SCI", "GESHIP"],
    "Electronics & EMS": ["DIXON", "KAYNES", "SYRMA", "AMBER", "CYIENTDLM", "AVALON"],
    "New-Age Tech": ["ETERNAL", "SWIGGY", "PAYTM", "POLICYBZR", "NYKAA", "NAUKRI", "JIOFIN"],
    "Cables & Wires": ["POLYCAB", "KEI", "FINCABLES", "HAVELLS", "APARINDS", "RRKABEL"],
    "Building Materials": ["ASTRAL", "SUPREMEIND", "KAJARIACER", "CERA", "ASIANPAINT", "BERGEPAINT", "PIDILITIND"],
    "Gold & Jewellery": ["TITAN", "KALYANKJIL", "SENCO", "THANGAMAYL"],
    "Hotels & Travel": ["INDHOTEL", "LEMONTREE", "CHALET", "EIHOTEL", "IRCTC", "INDIGO"],
    "Fertilizers & Agri": ["CHAMBLFERT", "COROMANDEL", "PIIND", "RALLIS", "UPL", "DHANUKA", "RCF"],
    "Insurance": ["HDFCLIFE", "SBILIFE", "ICICIPRULI", "ICICIGI", "STARHEALTH", "LICI"],
    "Logistics": ["DELHIVERY", "BLUEDART", "CONCOR", "TCI", "MAHLOG", "ALLCARGO"],
    "Hydro & Power Gen": ["NHPC", "SJVN", "NTPC", "JSWENERGY", "TORNTPOWER", "ADANIPOWER"],
}
BENCH = "^NSEI"

def stock(t): return t if t.startswith("^") else t + ".NS"
views = {"Sectors": {k: [stock(x) for x in v] for k, v in SECTORS.items()},
         "Indices": {k: [v] for k, v in INDICES.items()},
         "Themes": {k: [stock(s) for s in v] for k, v in THEMES.items()}}
tickers = sorted({s for v in views.values() for m in v.values() for s in m} | {BENCH})
df = yf.download(tickers, period="2y", auto_adjust=True, progress=False, group_by="ticker", threads=True)
idx = df[BENCH]["Close"].dropna().index          # trading calendar = Nifty 50
series, names = {}, {}
for t in tickers:
    if t == BENCH or t not in df.columns.get_level_values(0): continue
    d = df[t].reindex(idx).ffill()
    if d["Close"].isna().all(): print("skipped (no data):", t, file=sys.stderr); continue
    r = lambda c: [None if pd.isna(x) else round(float(x), 2) for x in d[c]]
    series[t] = {"c": r("Close"), "h": r("High"), "l": r("Low")}
for v in views.values():
    for g in list(v):
        v[g] = [s for s in v[g] if s in series]
        if not v[g]: del v[g]
out = {"generated": str(idx[-1].date()), "dates": [str(x.date()) for x in idx], "views": views, "series": series}
open("india_data.js", "w").write("const DATA=" + json.dumps(out, separators=(",", ":")) + ";")
print("wrote india_data.js", out["generated"], len(series), "series")
