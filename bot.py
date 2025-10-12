import requests
from bs4 import BeautifulSoup
import datetime
import os

# Discord webhook z GitHub Secrets
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")

# URL Forex Factory
FOREX_FACTORY_URL = "https://www.forexfactory.com/"

# Načtení HTML obsahu
response = requests.get(FOREX_FACTORY_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Vyhledání všech událostí
events = soup.find_all("tr", class_="calendar__row")

important_events = []
today = datetime.date.today().strftime("%b %d")  # např. Oct 12

for event in events:
    impact = event.find("span", class_="impact")
    if impact and "high" in impact.get("class", []):  # pouze červené (High Impact)
        time_el = event.find("td", class_="calendar__time")
        title_el = event.find("td", class_="calendar__event")
        currency_el = event.find("td", class_="calendar__currency")
        actual_el = event.find("td", class_="calendar__actual")
        forecast_el = event.find("td", class_="calendar__forecast")
        previous_el = event.find("td", class_="calendar__previous")

        if not title_el or not currency_el:
            continue

        title = title_el.get_text(strip=True)
        currency = currency_el.get_text(strip=True)
        actual = actual_el.get_text(strip=True) if actual_el else "-"
        forecast = forecast_el.get_text(strip=True) if forecast_el else "-"
        previous = previous_el.get_text(strip=True) if previous_el else "-"
        time = time_el.get_text(strip=True) if time_el else "All day"

        # Základní analýza dopadu
        def interpret(actual, forecast):
            try:
                actual_val = float(actual.replace("%", "").replace(",", ""))
                forecast_val = float(forecast.replace("%", "").replace(",", ""))
                if actual_val > forecast_val:
                    return f"📈 Lepší než očekávání → Posiluje {currency}"
                elif actual_val < forecast_val:
                    return f"📉 Horší než očekávání → Oslabuje {currency}"
                else:
                    return f"⚖️ Shodné s očekáváním → Neutrální vliv"
            except:
                return "❓ Nedostatek dat pro přesnou analýzu"

        analysis = interpret(actual, forecast)

        important_events.append({
            "time": time,
            "currency": currency,
            "title": title,
            "actual": actual,
            "forecast": forecast,
            "previous": previous,
            "analysis": analysis
        })

# Pokud nejsou žádné nové důležité zprávy
if not important_events:
    message = {
        "content": f"🕒 {today} – Žádné nové červené fundamentální zprávy dnes."
    }
    requests.post(DISCORD_WEBHOOK, json=message)
    exit()

# Formátování zprávy pro Discord
message_lines = [f"📊 **Fundamentální analýza – {today}**\n"]
for e in important_events:
    msg = (
        f"**{e['currency']} | {e['title']}** ({e['time']})\n"
        f"📍 Actual: {e['actual']} | Forecast: {e['forecast']} | Previous: {e['previous']}\n"
        f"🧠 {e['analysis']}\n"
    )
    message_lines.append(msg)

final_message = "\n".join(message_lines)

# Odeslání na Discord
requests.post(DISCORD_WEBHOOK, json={"content": final_message})
S
