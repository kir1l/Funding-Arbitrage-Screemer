# Crypto Funding Rate Arbitrage Screener

This project is a comprehensive tool for screening and analyzing funding rate arbitrage opportunities across multiple cryptocurrency exchanges. It currently supports Binance, Bybit, OKX, and MEXC exchanges.

## Features

- Screens multiple exchanges for funding rate arbitrage opportunities
- Supports Binance, Bybit, OKX, and MEXC
- Calculates potential profit considering exchange fees
- Concurrent processing for efficient data retrieval
- Outputs results to both console and a text file

## Installation

1. Clone this repository:
```bash
git clone https://github.com/kir1l/Funding-Arbitrage-Screemer.git cd funding-arbitrage-screener
```

2. Install the required dependencies:
```bash
pip install requests
```

## Usage

Run the main script to start the screener:
```bash
python main.py
```

The script will run all screeners and output the results to both the console and a `results.txt` file.

## Project Structure

- `main.py`: The entry point of the application. It manages and runs all the screeners.
- `screeners/`:
  - `binance_screener.py`: Screener for Binance exchange
  - `bybit_screener.py`: Screener for Bybit exchange
  - `okx_screener.py`: Screener for OKX exchange
  - `mexc_screener.py`: Screener for MEXC exchange

## How It Works

1. The `ScreenerManager` in `main.py` initializes and runs all the screeners.
2. Each screener:
   - Fetches all available perpetual contracts from the exchange
   - Retrieves the current funding rates for each contract
   - Calculates the potential profit considering the exchange fees
   - Sorts the results by potential profit
3. The top 20 results from each exchange are compiled and written to `results.txt`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is for educational purposes only. Always do your own research before making any investment decisions. Cryptocurrency trading carries a high level of risk and may not be suitable for all investors.

