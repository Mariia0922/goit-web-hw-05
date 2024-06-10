import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta

class CurrencyRateFetcher:
    BASE_URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

    def __init__(self, days: int):
        self.days = days
        self.dates = [self.get_date_str(days_ago=i) for i in range(days)]

    def get_date_str(self, days_ago: int) -> str:
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime('%d.%m.%Y')

    async def fetch_rates(self, session: aiohttp.ClientSession, date: str):
        url = f'{self.BASE_URL}{date}'
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.parse_rates(date, data)
                else:
                    print(f"Failed to fetch data for {date}: HTTP {response.status}")
        except aiohttp.ClientError as e:
            print(f"Failed to fetch data for {date}: {e}")

    def parse_rates(self, date: str, data: dict):
        rates = {}
        for rate in data.get('exchangeRate', []):
            if rate.get('currency') in ['USD', 'EUR']:
                rates[rate['currency']] = {
                    'sale': rate.get('saleRate', None),
                    'purchase': rate.get('purchaseRate', None)
                }
        return {date: rates}

    async def fetch_all_rates(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_rates(session, date) for date in self.dates]
            results = await asyncio.gather(*tasks)
            return [result for result in results if result]

def main():
    if len(sys.argv) != 2:
        print("Usage: py main.py <number_of_days>")
        return

    try:
        days = int(sys.argv[1])
        if days < 1 or days > 10:
            raise ValueError("Number of days must be between 1 and 10")
    except ValueError as e:
        print(e)
        return

    fetcher = CurrencyRateFetcher(days)
    rates = asyncio.run(fetcher.fetch_all_rates())
    print(rates)

if __name__ == "__main__":
    main()