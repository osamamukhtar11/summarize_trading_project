# summarize_trading_project
Trading summarizer for Capital.com

git clone https://github.com/osamamukhtar11/summarize_trading_project.git

# get required libraries
`pip install -r requirements.txt`

# Input file format (export an Activity report for OPENED and CLOSED activities from your Capital.com account)
`Trade Id,Exec Id,Account Id,Instrument Symbol,Instrument Name,Order Id,Currency,Execution Type,Quantity,Price,Take Profit,Stop Loss,gsl,Source,Status,rpl,Rpl Converted,Swap,Swap Converted,Fee,Timestamp,Account type`

# Output file format
`tradeId,trade_type,trade_currency,opened_date,closed_date,price_1,price_2,price_1_in_euros,price_2_in_euros,quantity_1,quantity_2,purchase_price,sales_price,profit_loss_in_original_currency,profit_loss_in_euros,profit_loss_in_euros_calculated`