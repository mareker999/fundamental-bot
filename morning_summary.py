import requests
from datetime import datetime, timedelta

DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1427170379734057022/vV6SwUHRXhBfIGhQ6E9uGjqGpm-Q9jBrObebkq1PTbnKoYo9zNg6r_W9KlOsMwe3234_"

FLAGS = {
    "United States": "🇺🇸 USD",
    "Euro Area": "🇪🇺 EUR",
    "United Kingdom": "🇬🇧 GBP",
    "Japan": "🇯🇵 JPY",
    "Switzerland": "🇨🇭 CHF",
    "Canada": "🇨🇦 CAD",
    "Australia": "🇦🇺 AUD",
    "New Zealand": "🇳🇿 NZD",
    "China": "🇨🇳 CNY"
}

def get_high_impact_events():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

    url = f"https://api.tradingeconomics.com/calendar?d1={today}&d2={tomorrow}&importance=3"

    print(f"📡 Stahuji data z: {url}")

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Chyba při načítání dat: {e}")
        return []

    events = []
    for item in data:
        country = item.get("Country", "Unknown")
        title = item.get("Event", "Neznámý event")
        time_utc = item.get("Date", "")  # UTC čas
        time_local = convert_to_czech_time(time_utc)
        events.append({
            "time": time_local,
            "country": country,
            "title": title
        })

    print(f"🔎 Nalezeno {len(events)} červených zpráv pro dnešek.")
    return events

def convert_to_czech_time(utc_time):
    try:
        dt = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%S")
        dt_czech = dt + timedelta(hours=2)
        return dt_czech.strftime("%H:%M")
    except:
        return "??:??"

def send_to_discord(events):
    today = datetime.now().strftime("%d.%m.%Y")

    if not events:
        msg = {"content": f"📅 **{today}** – Dnes nejsou žádné červené fundamentální zprávy."}
    else:
        text = f"🌅 **Ranní fundamentální přehled – {today}**\n\n"
        for e in events:
            flag = FLAGS.get(e["country"], "💱")
            text += f"🕒 {e['time']} | {flag} – **{e['title']}**\n"
        text += "\n📊 **Poznámka:** Sleduj měny s vysokým dopadem – možné zvýšení volatility."
        msg = {"content": text}

    try:
        response = requests.post(DISCORD_WEBHOOK, json=msg, timeout=10)
        if response.status_code in [200, 204]:
            print("✅ Zpráva úspěšně odeslána na Discord.")
        else:
            print(f"⚠️ Discord vrátil kód: {response.status_code}")
    except Exception as e:
        print(f"❌ Chyba při odesílání na Discord: {e}")

if __name__ == "__main__":
    events = get_high_impact_events()
    send_to_discord(events)




