import requests
import json

# NSE से डेटा लेने का URL
url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
headers = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
session.headers.update(headers)
response = session.get(url)
data = response.json()

# OI और IV आधारित कॉल्स और पुट्स
for record in data["records"]["data"]:
    if "CE" in record and "PE" in record:
        ce = record["CE"]
        pe = record["PE"]
        strike = ce["strikePrice"]
        oi_call = ce["openInterest"]
        oi_put = pe["openInterest"]
        iv_call = ce.get("impliedVolatility", 0)
        iv_put = pe.get("impliedVolatility", 0)

        if oi_call > 100000 and iv_call > 15:
            print(f"CALL - Strike: {strike}, OI: {oi_call}, IV: {iv_call}")
        if oi_put > 100000 and iv_put > 15:
            print(f"PUT - Strike: {strike}, OI: {oi_put}, IV: {iv_put}")
