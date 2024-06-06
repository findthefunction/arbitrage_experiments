# Arbitrage Bot

This project is an arbitrage bot designed to detect and capitalize on price discrepancies between different decentralized exchanges (DEXs) on the Solana blockchain. The bot fetches token prices from multiple DEXs, identifies arbitrage opportunities, and stores the data for analysis.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- Python 3.10+
- PostgreSQL
- Django
- pandas
- requests

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/arbitrage_bot.git
   cd arbitrage_bot


Usage
Apply database migrations:

```python manage.py makemigrations```
```python manage.py migrate```

Run the fetch data command: 

```python manage.py fetch_data ```

Run the visualize data command (for analysis):

```python manage.py visualize_data ```