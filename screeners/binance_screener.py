import requests
import time
from typing import Dict, Any, List
import decimal
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class BinanceScreener:
    BASE_URL = "https://api.binance.com"
    FUNDING_RATE_ENDPOINT = "/fapi/v1/premiumIndex"
    EXCHANGE_INFO_ENDPOINT = "/fapi/v1/exchangeInfo"

    def __init__(self):
        self.name = "Binance"
        self.contracts = self.get_all_contracts()
        logger.info(f"Initialized with {len(self.contracts)} contracts")

    def get_all_contracts(self) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}{self.EXCHANGE_INFO_ENDPOINT}"
        response = requests.get(url)
        response.raise_for_status()
        contracts = []
        for symbol in response.json()['symbols']:
            if symbol['contractType'] == 'PERPETUAL':
                contracts.append({
                    'symbol': symbol['symbol'],
                    'takerFeeRate': decimal.Decimal(symbol.get('takerFee', '0')),
                    'makerFeeRate': decimal.Decimal(symbol.get('makerFee', '0'))
                })
        return contracts

    def get_current_funding_rate(self, symbol: str) -> decimal.Decimal:
        url = f"{self.BASE_URL}{self.FUNDING_RATE_ENDPOINT}"
        params = {"symbol": symbol}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return self.format_funding_rate(response.json())

    def format_funding_rate(self, funding_rate_data):
        funding_rate = funding_rate_data['lastFundingRate']
        return decimal.Decimal(funding_rate).quantize(decimal.Decimal('1E-6'))

    def calculate_potential_profit(self, funding_rate: decimal.Decimal, contract: Dict[str, Any]) -> decimal.Decimal:
        total_fee = contract['takerFeeRate'] + contract['makerFeeRate']
        return funding_rate - total_fee

    def analyze_funding_rates(self):
        funding_rates = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.get_current_funding_rate, contract['symbol']): contract for contract in self.contracts}
            for future in as_completed(futures):
                contract = futures[future]
                try:
                    rate = future.result()
                    potential_profit = self.calculate_potential_profit(rate, contract)
                    funding_rates.append({
                        'ticker': contract['symbol'],
                        'funding_rate': rate,
                        'potential_profit': potential_profit
                    })
                except Exception as e:
                    logger.error(f"Error analyzing {contract['symbol']}: {e}")
        
        sorted_rates = sorted(funding_rates, key=lambda x: x['potential_profit'], reverse=True)
        return sorted_rates

    def run(self):
        try:
            best_contracts = self.analyze_funding_rates()
            logger.info(f"BinanceScreener completed. Found {len(best_contracts)} contracts.")
            return best_contracts
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return []

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    screener = BinanceScreener()
    screener.run()
