import requests
from datetime import datetime
import re

DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1427170379734057022/vV6SwUHRXhBfIGhQ6E9uGjqGpm-Q9jBrObebkq1PTbnKoYo9zNg6r_W9KlOsMwe3234_"

FLAGS = {
    "USD": "🇺🇸",
    "EUR": "🇪🇺",
    "GBP": "🇬🇧",
    "JPY": "🇯🇵",
    "CHF": "🇨🇭",
    "CAD": "🇨🇦",
    "AUD": "🇦🇺",
    "NZD": "🇳🇿",
    "CNY": "🇨🇳"
}

def get_high_impact_events():
    url = "https://cdn-nfs.forexfactory.net/ffcal_week_this.ics"
    print(f"📡 Stahuji data z: {url}")
    
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Chyba při načítání dat: {e}")
        return []

    data = r.text
    today = datetime.utcnow().strftime("%Y%m%d")
    events = []

    matches = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", data, re.S)
    for match in matches:
        if "Impact: High" in match:
            date_match = re.search(r"DTSTART:(\d+)", match)
            title_match = re.search(r"SUMMARY:(.+)", match)
            currency_match = re.search(r"Currency: ([A-Z]{3})", match)

            if date_match and title_match and currency_match:
                date_str = date_match.group(1)
                event_date = date_str[:8]
                if event_date == today:
                    time_utc = f"{date_str[9:11]}:{date_str[11:13]}"
                    events.append({
                        "time": time_utc,
                        "currency": currency_match.group(1),
                        "title": title_match.group(1)
                    })

    print(f"🔎 Nalezeno {len(events)} červených zpráv pro dnešek.")
    return events

def send_to_discord(events):
    today = datetime.now().strftime("%d.%m.%Y")

    if not events:
        msg = {"content": f"📅 **{today}** – Dnes nejsou žádné červené fundamentální zprávy."}
    else:
        text = f"🌅 **Ranní fundamentální přehled – {today}**\n\n"
        for e in events:
            flag = FLAGS.get(e["currency"], "💱")
            text += f"🕒 {e['time']} | {flag} **{e['currency']}** – {e['title']}\n"
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

