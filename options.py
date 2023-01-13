from optionprice import Option
import pandas as pd
from yahoo_fin.stock_info import *
from  yahoo_fin import options
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta


today_string = datetime.now().strftime("%m-%d-%Y")

one_yr_ago = datetime.now() - relativedelta(years=1)


def StockStats(ticker, start_date):
    stock_Price = get_data(ticker, start_date = start_date, end_date = datetime.now())

    mean = stock_Price['adjclose'].mean()
    std = stock_Price['adjclose'].std()

    std_pct = std/mean

    current_Price = stock_Price['adjclose'][-1]

    exp_dates = options.get_expiration_dates(ticker)

    options_data = {}
    for date in exp_dates:
        options_data[date] = options.get_options_chain(ticker)
    
    summary = {}
    summary['Price_History'] = stock_Price
    summary['Mean'] = mean
    summary['Std'] = std
    summary['Current_Price'] = current_Price
    summary['Options_Data'] = options_data
    return summary

def Call_spread(price1, price2,strike1, strike2):
    stats = {}
    if strike1 > strike2:
        premium = price2 - price1
        max_loss = strike2-strike1 +premium
        max_gain = premium
        break_even = strike2+premium
        stats['Direction'] = 'Bearish'
    else:
       premium = price2 - price1
       max_loss = premium
       max_gain = strike2-strike1+premium
       break_even = strike1-premium
       stats['Direction'] = 'Bullish'
    stats['Premium'] = premium
    stats['Max_Loss'] = max_loss
    stats['Max_Gain'] = max_gain
    stats['Break_Even'] = break_even
    return stats

def Put_spread(price1, price2,strike1, strike2):
    stats = {}
    if  strike2 > strike1:
        premium = price2 - price1
        max_loss = strike1-strike2 + premium
        max_gain = premium
        break_even = strike2-premium
        stats['Direction'] = 'Bullish'
    else:
        premium = price2 - price1
        max_loss = premium
        max_gain = strike1 - strike2 + premium
        stats['Direction'] = 'Bearish'
        break_even = strike1+premium
    stats['Premium'] = premium
    stats['Max_Loss'] = max_loss
    stats['Max_Gain'] = max_gain
    stats['Break_Even'] = break_even
    return stats

        
Stocks = ['MU','AMD']
data = {}

for stock in Stocks:
    data[stock] = StockStats(stock,one_yr_ago)
    
spreads = {}

for stock in Stocks:
    data_df = data[stock]['Options_Data'][list(data[stock]['Options_Data'].keys())[1]]['calls'][['Strike', 'Ask', 'Bid']]
    call_spreads = {}
    for i in range(len(data_df)):
        for j in range(len(data_df)):
            call_spreads[data_df['Strike'].iloc[i],data_df['Strike'].iloc[j]] = Call_spread(data_df['Ask'].iloc[i],data_df['Bid'].iloc[j],data_df['Strike'].iloc[i],data_df['Strike'].iloc[j])
    call_df = pd.DataFrame.from_dict(call_spreads, orient='index',columns=['Direction','Premium','Max_Loss', 'Max_Gain','Break_Even'])
    call_df['Current_Price'] = data[stock]['Current_Price']
    call_df = call_df[call_df['Max_Gain'] >= 0]
    call_df['Risk_Ratio'] = call_df['Max_Loss'] / call_df['Max_Gain']
    spreads[stock, 'calls'] = call_df
    
for stock in Stocks:
    data_df = data[stock]['Options_Data'][list(data[stock]['Options_Data'].keys())[1]]['puts'][['Strike', 'Ask', 'Bid']]
    put_spreads = {}
    for i in range(len(data_df)):
        for j in range(len(data_df)):
            put_spreads[data_df['Strike'].iloc[i],data_df['Strike'].iloc[j]] = Put_spread(data_df['Ask'].iloc[i],data_df['Bid'].iloc[j],data_df['Strike'].iloc[i],data_df['Strike'].iloc[j])
    put_df = pd.DataFrame.from_dict(put_spreads, orient='index',columns=['Direction','Premium','Max_Loss', 'Max_Gain','Break_Even'])
    put_df['Current_Price'] = data[stock]['Current_Price']
    put_df = put_df[put_df['Max_Gain'] >= 0]
    put_df['Risk_Ratio'] = put_df['Max_Loss'] / put_df['Max_Gain']
    spreads[stock, 'puts'] = put_df
