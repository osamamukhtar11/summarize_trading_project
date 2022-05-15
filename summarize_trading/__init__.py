import logging

import pandas as pd
from currency_converter import CurrencyConverter, RateNotFoundError
from datetime import datetime, timedelta

def get_trade_type(quantity_1):
    """ Get trade type based on quantity of last trade activity

    :param quantity_1: quantity of the first trade activity is used to identify if it is a LONG or SHORT trade
    :return: trade_type based on quantity
    """
    if quantity_1 > 0:
        return "SHORT"
    else:
        return "LONG"


def get_prices_and_dates(trade_activities):
    """Loop through all rows of dataframe and find prices for OPENED and CLOSED

    :param trade_activities: iterrows object containing OPENED/CLOSED activities
    :return: price_1, price_2, closed_date
    """
    price_1_in_euros = price_2_in_euros = price_1 = price_2 = 0
    closed_date = opened_date = '2000-01-01 00:00:00'
    for trade_activity in trade_activities.iterrows():
        if trade_activity[1][14] == 'CLOSED':
            price_1 = trade_activity[1][9]
            closed_date = trade_activity[1][20]
            input_currency = trade_activity[1][6]
        else:
            price_2 = trade_activity[1][9]
            opened_date = trade_activity[1][20]
            input_currency = trade_activity[1][6]
    c = CurrencyConverter()
    datetime_obj_opened = datetime.strptime(opened_date[0:10], '%Y-%m-%d').date()
    datetime_obj_closed = datetime.strptime(opened_date[0:10], '%Y-%m-%d').date()
    counter = 0
    while True:
        try:
            price_1_in_euros = c.convert(price_1, input_currency, 'EUR', datetime_obj_opened - timedelta(days=counter))
        except RateNotFoundError:
            logging.error("RateNotFoundError for ID: " + trade_activity[1][0] + ", date = " + opened_date[0:10])
            logging.error("Trying for the next possible date, counter = " + str(counter))
            counter = counter+1
            continue
        else:
            break

    counter = 0
    while True:
        try:
            price_2_in_euros = c.convert(price_2, input_currency, 'EUR', datetime_obj_closed - timedelta(days=counter))
        except RateNotFoundError:
            logging.error("RateNotFoundError for ID: " + trade_activity[1][0] + ", date = " + closed_date[0:10])
            logging.error("Trying for the next possible date, counter = " + str(counter))
            counter = counter+1
            continue
        else:
            break
    #print(price_1, price_2, opened_date, closed_date, input_currency, price_1_in_euros, price_2_in_euros)
    return price_1, price_2, opened_date, closed_date, input_currency, price_1_in_euros, price_2_in_euros


def get_trade_details(tradeId: str, df):
    """Returns details for each trade using its ID

    # Examples of valid examples from test file
    #    SHORT: get_trade_details("00001344-0001-54c4-0000-000080172ebd", input_df)
    #    LONG: get_trade_details("0008e1cf-0001-54c4-0000-0000800000b0", input_df)
    #    SHORT (CLOSED order split): get_trade_details("00513301-0001-54c4-0000-00008002e8a6", input_df)
    :param tradeId: str
    :param df: dataframe

    """
    # print(df.loc[df['Trade Id'] == tradeId])
    if len(df.loc[df['Trade Id'] == tradeId]) >= 2:
        sales_price_in_euros = purchase_price_in_euros = profit_loss_in_euros_calculated = price_1_in_euros = price_2_in_euros = price_1 = price_2 = quantity_1 = quantity_2 = profit_loss_in_euros = trade_type = purchase_price = sales_price = profit_loss_in_original_currency = closed_date = 0;
        for (columnName, columnData) in df.loc[df['Trade Id'] == tradeId].groupby(["Status"]).sum().iteritems():
            # if there is only a single OPENED or CLOSED, it means row has already been processed or is still open
            # So we can skip the rows with columns < 2.
            if len(columnData) >= 2:
                if columnName == 'Quantity':
                    quantity_1 = columnData.values[0]
                    quantity_2 = columnData.values[1]
                    trade_type = get_trade_type(quantity_1)
                if columnName == 'Rpl Converted':
                    profit_loss_in_euros = columnData.values[0]

        price_1, price_2, opened_date, closed_date, trade_currency, price_1_in_euros, price_2_in_euros = get_prices_and_dates(
            df.loc[df['Trade Id'] == tradeId])

        if trade_type == 'SHORT':
            purchase_price = float("{:.2f}".format(abs(price_2 * quantity_2)))
            sales_price = float("{:.2f}".format(price_1 * quantity_1))
            purchase_price_in_euros = float("{:.2f}".format(abs(price_2_in_euros * quantity_2)))
            sales_price_in_euros = float("{:.2f}".format(price_1_in_euros * quantity_1))
            profit_loss_in_original_currency = float("{:.2f}".format(purchase_price - sales_price))
            profit_loss_in_euros_calculated = float("{:.2f}".format(purchase_price_in_euros - sales_price_in_euros))
        elif trade_type == 'LONG':
            purchase_price = float("{:.2f}".format(price_2 * quantity_2))
            sales_price = float("{:.2f}".format(abs(price_1 * quantity_1)))
            purchase_price_in_euros = float("{:.2f}".format(price_2_in_euros * quantity_2))
            sales_price_in_euros = float("{:.2f}".format(abs(price_1_in_euros * quantity_1)))
            profit_loss_in_original_currency = float("{:.2f}".format(sales_price - purchase_price))
            profit_loss_in_euros_calculated = float("{:.2f}".format(sales_price_in_euros - purchase_price_in_euros))

        logging.info(
            str(tradeId) + "," + str(trade_type) + "," + str(closed_date) + "," + str(price_1) + "," + str(
                price_2) + "," + str(
                quantity_1) + "," + str(quantity_2) + "," + str(purchase_price) + "," + str(sales_price) + "," + str(
                profit_loss_in_original_currency) + "," + str(profit_loss_in_euros) + str(profit_loss_in_euros_calculated))
        return [tradeId, trade_type, trade_currency, opened_date, closed_date, price_1, price_2, price_1_in_euros, price_2_in_euros, quantity_1, quantity_2, purchase_price,
                sales_price,
                profit_loss_in_original_currency, profit_loss_in_euros, profit_loss_in_euros_calculated]
    else:
        logging.error(
            "Incomplete trade or Invalid number of rows (not >= 2): " + str(len(df.loc[df['Trade Id'] == tradeId])))
        logging.error("=> Trade ID = " + df.loc[df['Trade Id'] == tradeId]['Trade Id'])
        return [tradeId]


def summarize_trading(filename):
    input_directory = "input/"
    output_directory = "output/"
    logs_directory = "logs/"
    logging.basicConfig(level=logging.INFO, filename=logs_directory + "app.log", filemode='w',
                        format='%(name)s - %(levelname)s - %(message)s')
    input_df = pd.read_csv(input_directory + filename)
    output_df = pd.DataFrame(
        columns=['tradeId', 'trade_type', 'trade_currency', 'opened_date', 'closed_date', 'price_1', 'price_2', 'price_1_in_euros', 'price_2_in_euros', 'quantity_1',
                 'quantity_2', 'purchase_price', 'sales_price', 'profit_loss_in_original_currency',
                 'profit_loss_in_euros', 'profit_loss_in_euros_calculated'])
    invalid_df = pd.DataFrame(['tradeId'])
    # drop duplicates from the list used for iterations so that we don't waste time repetition of operations for the same trade
    trade_ids = input_df["Trade Id"].drop_duplicates()
    count = count_for_invalid = 0
    for trade_id in trade_ids:
        print(trade_id)
        to_append = get_trade_details(trade_id, input_df)
        if len(to_append) > 1:
            a_series = pd.Series(to_append, index=output_df.columns)
            output_df.loc[count] = a_series
            count = count + 1
        else:
            a_series = pd.Series(to_append, index=invalid_df.columns)
            invalid_df.loc[count_for_invalid] = a_series
            count_for_invalid = count_for_invalid + 1

    output_df.to_csv(output_directory + "output.csv", index=False)
    invalid_df.to_csv(output_directory + "invalid.csv", index=False)


if __name__ == '__main__':
    filename = "input.csv";
    summarize_trading(filename)
