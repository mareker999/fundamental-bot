import requests
from bs4 import BeautifulSoup
from datetime import datetime

DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1427170379734057022/vV6SwUHRXhBfIGhQ6E9uGjqGpm-Q9jBrObebkq1PTbnKoYo9zNg6r_W9KlOsMwe3234_"
URL = "https://www.forexfactory.com/calendar?day=today"

# Mapování měn na emoji vlajky
CURRENCY_FLAGS = {
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

def get_todays_high_impact_events():
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    events = []
    rows = soup.select("tr.calendar__row.calendar_row")
    for row in rows:
        impact = row.select_one(".calendar__impact-icon.calendar__impact-icon--high")
        if impact:
            time = row.select_one(".calendar__time")
            currency = row.select_one(".calendar__currency")
            event = row.select_one(".calendar__event-title")
            if all([time, currency, event]):
                events.append({
                    "time": time.text.strip(),
                    "currency": currency.text.strip(),
                    "event": event.text.strip(),
                })
    return events

def send_to_discord(events):
    today = datetime.now().strftime("%d.%m.%Y")

    if not events:
        message = {
            "content": f"📅 **{today}** – Dnes nejsou žádné červené fundamentální zprávy."
        }
    else:
        text = f"🌅 **Ranní fundamentální přehled – {today}**\n\n"
        for e in events:
            flag = CURRENCY_FLAGS.get(e["currency"], "💱")
            text += f"🕒 {e['time']} | {flag} **{e['currency']}** – {e['event']}\n"
        text += "\n📊 **Poznámka:** Sleduj měny s vysokým dopadem – možné zvýšení volatility."
        message = {"content": text}

    response = requests.post(DISCORD_WEBHOOK, json=message)
    if response.status_code == 204:
        print("✅ Ranní přehled odeslán na Discord.")
    else:
        print(f"⚠️ Chyba při odesílání na Discord: {response.status_code}")

if __name__ == "__main__":
    events = get_todays_high_impact_events()
    send_to_discord(events)

