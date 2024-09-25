import requests
import time
from typing import Dict, Any, List
import decimal
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BybitScreener:
    BASE_URL = "https://api.bybit.com"
    FUNDING_RATE_ENDPOINT = "/v5/market/funding/history"
    INSTRUMENTS_INFO_ENDPOINT = "/v5/market/instruments-info"

    def __init__(self):
        self.name = 'Bybit'
        self.contracts = self.get_all_contracts()
        logger.info(f"Initialized with Bybit Screener{len(self.contracts)} contracts")

    def get_all_contracts(self) -> List[Dict[str, Any]]:
      logger.info("Fetching all contracts")
      url = f"{self.BASE_URL}{self.INSTRUMENTS_INFO_ENDPOINT}"
      params = {"category": "linear"}
      try:
         response = requests.get(url, params=params)
         response.raise_for_status()
         contracts = []
         current_date = datetime.now()
         for contract in response.json()['result']['list']:
               symbol = contract['symbol']
               if not self.is_future_dated_contract(symbol, current_date):
                  contracts.append({
                     'symbol': symbol,
                     'takerFeeRate': decimal.Decimal(contract.get('takerFee', '0')),
                     'makerFeeRate': decimal.Decimal(contract.get('makerFee', '0'))
                  })
         logger.info(f"Successfully fetched {len(contracts)} contracts")
         return contracts
      except requests.RequestException as e:
         logger.error(f"Error fetching contracts: {e}")
         return []

    def is_future_dated_contract(self, symbol: str, current_date: datetime) -> bool:
      match = re.search(r'-(\d{2})([A-Z]{3})(\d{2})$', symbol)
      if match:
         day, month, year = match.groups()
         contract_date = datetime.strptime(f"20{year}-{month}-{day}", "%Y-%b-%d")
         return contract_date > current_date
      return False

    def get_current_funding_rate(self, symbol: str) -> decimal.Decimal:
        url = f"{self.BASE_URL}{self.FUNDING_RATE_ENDPOINT}"
        params = {"symbol": symbol, "category": "linear", "limit": 1}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            funding_rate_data = response.json()['result']['list'][0]
            return self.format_funding_rate(funding_rate_data)
        except (requests.exceptions.HTTPError, IndexError, KeyError) as e:
            logger.warning(f"Error fetching funding rate for {symbol}: {e}")
            return decimal.Decimal('0')


    def format_funding_rate(self, funding_rate_data):
        funding_rate = funding_rate_data.get('fundingRate', '0')
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
        logger.info("Starting BybitScreener")
        try:
            best_contracts = self.analyze_funding_rates()
            logger.info(f"BybitScreener completed. Found {len(best_contracts)} contracts.")
            return best_contracts
        except Exception as e:
            logger.error(f"An error occurred during BybitScreener execution: {e}")
            return []

