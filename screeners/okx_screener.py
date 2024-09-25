import requests
import time
from typing import Dict, Any, List
import decimal
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class OkxScreener:
    BASE_URL = "https://www.okx.com"
    FUNDING_RATE_ENDPOINT = "/api/v5/public/funding-rate"
    INSTRUMENTS_INFO_ENDPOINT = "/api/v5/public/instruments"

    def __init__(self):
        self.name = 'Okx'
        self.contracts = self.get_all_contracts()
        logger.info(f"Initialized Okx Screener with {len(self.contracts)} contracts")

    def get_all_contracts(self) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}{self.INSTRUMENTS_INFO_ENDPOINT}"
        params = {"instType": "SWAP"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        contracts = []
        for contract in response.json()['data']:
            contracts.append({
                'symbol': contract['instId'],
                'takerFeeRate': decimal.Decimal(contract.get('takerFeeRate', '0')),
                'makerFeeRate': decimal.Decimal(contract.get('makerFeeRate', '0'))
            })
        return contracts

    def get_current_funding_rate(self, symbol: str) -> decimal.Decimal:
        url = f"{self.BASE_URL}{self.FUNDING_RATE_ENDPOINT}"
        params = {"instId": symbol}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return self.format_funding_rate(response.json()['data'][0])

    def format_funding_rate(self, funding_rate_data):
        funding_rate = funding_rate_data['fundingRate']
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
            return best_contracts
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return []
