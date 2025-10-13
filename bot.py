import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# 🔗 Tvůj Discord webhook (vložit sem!)
DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1427170379734057022/vV6SwUHRXhBfIGhQ6E9uGjqGpm-Q9jBrObebkq1PTbnKoYo9zNg6r_W9KlOsMwe3234_"

# 🌍 Forex Factory kalendář
URL = "https://www.forexfactory.com/calendar?day=today"

def get_fundamental_news():
    """Načte červené (high impact) zprávy z Forex Factory"""
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    
    news_data = []
    rows = soup.select("tr.calendar__row.calendar_row")
    
    for row in rows:
        impact = row.select_one(".calendar__impact-icon.calendar__impact-icon--high")
        if impact:
            time = row.select_one(".calendar__time")
            currency = row.select_one(".calendar__currency")
            event = row.select_one(".calendar__event-title")
            actual = row.select_one(".calendar__actual")
            forecast = row.select_one(".calendar__forecast")
            previous = row.select_one(".calendar__previous")
            
            if all([time, currency, event]):
                news_data.append({
                    "time": time.text.strip(),
                    "currency": currency.text.strip(),
                    "event": event.text.strip(),
                    "actual": actual.text.strip() if actual else "—",
                    "forecast": forecast.text.strip() if forecast else "—",
                    "previous": previous.text.strip() if previous else "—",
                })
    return news_data

def analyze_impact(actual, forecast, event_name):
    """Určí, zda je výsledek pozitivní nebo negativní pro měnu"""
    if actual == "—" or forecast == "—":
        return "⏳ Čeká se na výsledek."
    
    try:
        actual_val = float(actual.replace("%", "").replace(",", ""))
        forecast_val = float(forecast.replace("%", "").replace(",", ""))
    except ValueError:
        return "📊 Nelze vyhodnotit (nečíselná data)."

    # Základní logika podle typu události
    if any(x in event_name.lower() for x in ["unemployment", "jobless", "claims"]):
        return "📉 Negativní pro měnu" if actual_val > forecast_val else "📈 Pozitivní pro měnu"
    elif any(x in event_name.lower() for x in ["cpi", "inflation", "ppi", "price"]):
        return "📈 Pozitivní pro měnu" if actual_val > forecast_val else "📉 Negativní pro měnu"
    elif any(x in event_name.lower() for x in ["gdp", "sales", "employment", "payrolls", "pmi"]):
        return "📈 Pozitivní pro měnu" if actual_val > forecast_val else "📉 Negativní pro měnu"
    else:
        # Neutrální default
        if actual_val > forecast_val:
            return "📈 Pozitivní pro měnu"
        elif actual_val < forecast_val:
            return "📉 Negativní pro měnu"
        else:
            return "⚪ Neutrální výsledek"

def create_message(news_data):
    """Vytvoří zprávu pro Discord"""
    if not news_data:
        return {
            "content": f"📅 **{datetime.now().strftime('%b %d')}** – Žádné nové červené fundamentální zprávy dnes."
        }

    message_lines = [f"📊 **Fundamentální analýza – {datetime.now().strftime('%b %d')}**\n"]

    for item in news_data:
        analysis = analyze_impact(item["actual"], item["forecast"], item["event"])
        message_lines.append(
            f"🇨🇭 **{item['currency']} – {item['event']}**\n"
            f"🕒 {item['time']}\n"
            f"📊 Actual: {item['actual']} | Forecast: {item['forecast']} | Previous: {item['previous']}\n"
            f"💬 {analysis}\n"
        )

    return {"content": "\n".join(message_lines)}

def send_to_discord(message):
    """Odešle výsledek na Discord"""
    if not DISCORD_WEBHOOK or not DISCORD_WEBHOOK.startswith("https://"):
        raise ValueError("❌ Discord webhook URL není správně nastaven.")
    requests.post(DISCORD_WEBHOOK, json=message)

if __name__ == "__main__":
    news_data = get_fundamental_news()
    message = create_message(news_data)
    send_to_discord(message)
    print("✅ Zpráva odeslána na Discord.")
