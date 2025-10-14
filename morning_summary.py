import requests
from datetime import datetime

DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1427170379734057022/vV6SwUHRXhBfIGhQ6E9uGjqGpm-Q9jBrObebkq1PTbnKoYo9zNg6r_W9KlOsMwe3234_"
# Mapa měn na vlajky
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
    today = datetime.utcnow().strftime("%Y-%m-%d")
    url = f"https://cdn-nfs.fxfactory.com/ffcal/week-{today}.json"
    r = requests.get(url)
    if r.status_code != 200:
        print("❌ Chyba při načítání dat z ForexFactory.")
        return []

    data = r.json()
    events = []

    for event in data.get("events", []):
        if event.get("impact") == "High":  # Pouze červené zprávy
            date_str = event.get("date")
            time_str = event.get("time", "")
            currency = event.get("currency", "")
            title = event.get("title", "")

            events.append({
                "time": f"{date_str} {time_str}",
                "currency": currency,
                "title": title
            })
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
            text += f"🕒 {e['time']} | {flag} **{e['currency']}** – {e['title']}\n"
        text += "\n📊 **Poznámka:** Sleduj měny s vysokým dopadem – možné zvýšení volatility."
        msg = {"content": text}

    response = requests.post(DISCORD_WEBHOOK, json=msg)
    if response.status_code == 204:
        print("✅ Ranní přehled odeslán.")
    else:
        print(f"⚠️ Chyba při odesílání: {response.status_code}")

if __name__ == "__main__":
    events = get_high_impact_events()
    send_to_discord(events)

