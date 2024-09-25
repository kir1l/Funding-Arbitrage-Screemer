import requests
import time
from typing import Dict, Any, List
import decimal
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger('main.py')

class MexcScreener:
    BASE_URL = "https://contract.mexc.com/"
    FUNDING_RATE_ENDPOINT = "api/v1/contract/funding_rate/{symbol}"
    CONTRACT_DETAILS_ENDPOINT = "api/v1/contract/detail"

    def __init__(self):
        self.name = 'Mexc'
        self.contracts = self.get_all_contracts()
        logger.info(f"Initialized Mexc Screener with {len(self.contracts)} contracts")

    def get_all_contracts(self) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}{self.CONTRACT_DETAILS_ENDPOINT}"
        response = requests.get(url)
        response.raise_for_status()
        contracts = []
        for contract in response.json()['data']:
            contracts.append({
                'symbol': contract['symbol'],
                'takerFeeRate': decimal.Decimal(contract['takerFeeRate']),
                'makerFeeRate': decimal.Decimal(contract['makerFeeRate'])
            })
        return contracts

    def get_current_funding_rate(self, symbol: str) -> decimal.Decimal:
        url = f"{self.BASE_URL}{self.FUNDING_RATE_ENDPOINT.format(symbol=symbol)}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return self.format_funding_rate(response.json()['data'])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get funding rate for {symbol}: {e}")
            return None

    def format_funding_rate(self, funding_rate_data):
        funding_rate = funding_rate_data['fundingRate']
        return decimal.Decimal(funding_rate).quantize(decimal.Decimal('1E-6'))

    def calculate_potential_profit(self, funding_rate: decimal.Decimal, contract: Dict[str, Any]) -> decimal.Decimal:
        total_fee = contract['makerFeeRate'] * 2
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
            logger.info(f"MexcScreener analyze completed. Found {len(best_contracts)} contracts.")
            return best_contracts
        except Exception as e:
            logger.error(f"An error occurred: {e}")