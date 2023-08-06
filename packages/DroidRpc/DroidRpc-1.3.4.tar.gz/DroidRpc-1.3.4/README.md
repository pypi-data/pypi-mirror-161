# LORA Technologies' Bot Client
Client for LORA Tech's bot services.

**Example**  
A working example script that you can try can be found at https://github.com/asklora/Droid-Client/blob/production/example_usage.py


## Usage:  
### Bot Creation
```
Client.create_bot(args, **kwargs)

Args:
    ticker (str): cRIC code for which stock to create a bot for
    spot_date (str): Date for bot creations.
    investment_amount (float): Amount of cash the bot can use.
    bot_id (str): The type of bot to use (e.g. CLASSIC_classic_025)

Kwargs:
    margin (int): Amount of margin the bot is allowed to use. Defaults to 1.
    price (float): Price of the stock (any currency). Defaults to None (current price).
    fractionals (bool): Whether the bot should use fractional shares. Defaults to False.

Returns:
    dict: Parsed bot service response.
        {
            barrier (float),              # 
            bot_id (str),                 # This bot's bot type
            classic_vol (float),          # 
            created (str),                # Date of bot creation
            delta (float),                # 
            entry_price (float),          # Price of stock when this bot was created
            expiry (str),                 # Date of expiry
            fractionals (bool),           # Whether this bot is allowed to use fractional shares
            margin (int),                 # Amount of margin this bot is allowed to use
            max_loss_amount (float),      # 
            max_loss_pct (float),         # 
            max_loss_price (float),       # 
            option_price (float),         # 
            q (float),                    # 
            r (float),                    # 
            share_num (float),            # Number of shares bought
            side (str),                   # 
            spot_date (str),              # [For internal use]
            status (str),                 # Status of this bot (i.e. active)
            strike (float),               # 
            strike_2 (float),             # 
            t (int),                      # 
            target_profit_amount (float), # 
            target_profit_pct (float),    # 
            target_profit_price (float),  # 
            ticker (str),                 # RIC code
            total_bot_share_num (int),    # Number of shares held by this bot
            v1 (float),                   # 
            v2 (float),                   # 
            vol (float),                  # 
        }
```

### Hedging using an existing bot
```
Client.hedge(*args, **kwargs)

Args:
    bot_id (str): Type of bot.
    ticker (str): RIC code.
    current_price (float): Current price (any currency).
    entry_price (float): Price when the bot was created.
    last_share_num (float): Number of shares currently held by the bot.
    last_hedge_delta (float): Number of shares last sold/bought by the bot.
    investment_amount (float): Total cash value the bot is allowed to manage.
    bot_cash_balance (float): Remaining cash the bot has.
    stop_loss_price (float): Stop loss level of the bot.
    take_profit_price (float): Take profit level of the bot.
    expiry (str): Date when the bot expires.

Kwargs:
    strike (Optional[float]): _description_. Defaults to None.
    strike_2 (Optional[float]): _description_. Defaults to None.
    margin (Optional[int]): Amount of margin the bot can use. Defaults to 1.
    fractionals (Optional[bool]): Whether this bot is allowed to use fractional shares. Defaults to False.
    option_price (Optional[float]): _description_. Defaults to None.
    barrier (Optional[float]): _description_. Defaults to None.
    current_low_price (Optional[float]): _description_. Defaults to None.
    current_high_price (Optional[float]): _description_. Defaults to None.
    ask_price (Optional[float]): _description_. Defaults to None.
    bid_price (Optional[float]): _description_. Defaults to None.
    trading_day (Optional[str]): _description_. Defaults to datetime.strftime(datetime.now().date(), "%Y-%m-%d  ").

Returns:
    dict: Parsed bot service response
        {
            barrier (float),           # Take profit
            current_price (float),     # Current price of stock
            delta (float),             # 
            entry_price (float),       # 
            last_hedge_delta (float),  # 
            option_price (float),      # 
            q (float),                 # 
            r (float),                 # 
            share_change (float),      # 
            share_num (float),         # 
            side (str),                # 
            status (str),              # 
            strike (float),            # Target price
            strike_2 (float),          # For ucdc we have two strikes
            t (int),                   # 
            total_bot_share_num (int), # 
            v1 (float),                # 
            v2 (float),                # 
        }
```

### Stopping a bot
```
Client.stop(*args, **kwargs)

Args:
    bot_id (str): Type of bot.
    ticker (str): RIC code.
    current_price (float): Current price (any currency).
    entry_price (float): Price when the bot was created.
    last_share_num (float): Number of shares currently held by the bot.
    last_hedge_delta (float): Number of shares last sold/bought by the bot.
    investment_amount (float): Total cash value the bot is allowed to manage.
    bot_cash_balance (float): Remaining cash the bot has.
    stop_loss_price (float): Stop loss level of the bot.
    take_profit_price (float): Take profit level of the bot.
    expiry (str): Date when the bot expires.

Kwargs:
    strike (Optional[float]): _description_. Defaults to None.
    strike_2 (Optional[float]): _description_. Defaults to None.
    margin (Optional[int]): Amount of margin the bot can use. Defaults to 1.
    fractionals (Optional[bool]): Whether this bot is allowed to use fractional shares. Defaults to False.
    option_price (Optional[float]): _description_. Defaults to None.
    barrier (Optional[float]): _description_. Defaults to None.
    current_low_price (Optional[float]): _description_. Defaults to None.
    current_high_price (Optional[float]): _description_. Defaults to None.
    ask_price (Optional[float]): _description_. Defaults to None.
    bid_price (Optional[float]): _description_. Defaults to None.
    trading_day (Optional[str]): _description_. Defaults to datetime.strftime(datetime.now().date(), "%Y-%m-%d  ").

Returns:
    dict: Parsed bot service response
        {
            barrier (float),           # Take profit
            current_price (float),     # Current price of stock
            delta (float),             # 
            entry_price (float),       # 
            last_hedge_delta (float),  # 
            option_price (float),      # 
            q (float),                 # 
            r (float),                 # 
            share_change (float),      # 
            share_num (float),         # 
            side (str),                # 
            status (str),              # 
            strike (float),            # Target price
            strike_2 (float),          # For ucdc we have two strikes
            t (int),                   # 
            total_bot_share_num (int), # 
            v1 (float),                # 
            v2 (float),                # 
        }
```
