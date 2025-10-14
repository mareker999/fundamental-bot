import requests
from datetime import datetime, timedelta
import json

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

def get_current_week_url():
    """Vypočítá pondělí aktuálního týdne a vytvoří URL feedu."""
    today = datetime.utcnow()
    monday = today - timedelta(days=today.weekday())
    week_str = monday.strftime("%Y-%m-%d")
    return f"https://cdn-nfs.fxfactory.com/ffcal/week-{week_str}.json"

def get_high_impact_events():
    url = get_current_week_url()
    print(f"📡 Stahuji data z: {url}")

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Chyba při načítání dat: {e}")
        return []

    try:
        data = r.json()
    except json.JSONDecodeError:
        print("❌ Chyba: odpověď není validní JSON.")
        return []

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    events = []

    for event in data.get("events", []):
        if event.get("impact") == "High" and event.get("date") == today_str:
            events.append({
                "time": event.get("time", "").strip(),
                "currency": event.get("currency", "").strip(),
                "title": event.get("title", "").strip()
            })

    print(f"🔎 Nalezeno {len(events)} červených zpráv pro dnešek.")
    return events

def send_to_discord(events):
    today = datetime.now().strftime("%d.%m.%Y")

    if not events:
        msg = {
            "content": f"📅 **{today}** – Dnes nejsou žádné červené fundamentální zprávy."
        }
    else:
        text = f"🌅 **Ranní fundamentální přehled – {today}**\n\n"
        for e in events:
            flag = FLAGS.get(e["currency"], "💱")
            time_display = e["time"] if e["time"] else "??:??"
            text += f"🕒 {time_display} | {flag} **{e['currency']}** – {e['title']}\n"
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

