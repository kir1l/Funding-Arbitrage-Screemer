import logging
from screeners.mexc_screener import MexcScreener
from screeners.bybit_screener import BybitScreener
from screeners.okx_screener import OkxScreener

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScreenerManager:
    def __init__(self):
        self.screeners = [MexcScreener(), BybitScreener(), OkxScreener()]

    def run_screeners(self):
        all_results = []
        for screener in self.screeners:
            data = screener.run()
            data = data[:20]

            result = {
               'ex_name': screener.name,
               'coins': data
            }
            all_results.append(result)
        
        with open('results.txt', 'w') as f:
            for exchange in all_results:
               logger.info(f"Top {len(exchange['coins'])} coins in {exchange['ex_name']}")
               f.write(f"============ Top {len(exchange['coins'])} coins in {exchange['ex_name']} ============\n")
               for coin in exchange['coins']:
                  f.write(f"{coin['ticker']}. Funding rate: {coin['funding_rate']} - Potential Profit: {coin['potential_profit']:.6%}\n")
                  logger.info(f"{coin['ticker']}. Funding rate: {coin['funding_rate']} - Potential Profit: {coin['potential_profit']:.6%}")
        return all_results

if __name__ == "__main__":
    screener_manager = ScreenerManager()
    screener_manager.run_screeners()
