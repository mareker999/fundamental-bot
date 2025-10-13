import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1427170379734057022/vV6SwUHRXhBfIGhQ6E9uGjqGpm-Q9jBrObebkq1PTbnKoYo9zNg6r_W9KlOsMwe3234_"
URL = "https://www.forexfactory.com/calendar?day=today"

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
    if not DISCORD_WEBHOOK.startswith("https://"):
        raise ValueError("Webhook URL není správně nastaven.")
    
    if not events:
        message = {
            "content": f"📅 **{datetime.now().strftime('%d.%m.%Y')}** – Dnes nejsou žádné červené fundamentální zprávy."
        }
    else:
        text = f"🌅 **Ranní fundamentální přehled – {datetime.now().strftime('%d.%m.%Y')}**\n\n"
        for e in events:
            text += f"🕒 {e['time']} | 💱 {e['currency']} – {e['event']}\n"
        message = {"content": text}
    
    requests.post(DISCORD_WEBHOOK, json=message)
    print("✅ Ranní přehled odeslán.")

if __name__ == "__main__":
    events = get_todays_high_impact_events()
    send_to_discord(events)
