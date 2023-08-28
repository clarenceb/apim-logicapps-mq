#!/usr/bin/env python

from faker import Faker
import json
fake = Faker()

def gen_payload():
    tradeId=fake.pyint(100000,999999)
    tradeDate=fake.date(pattern="%Y-%m-%d")
    notional=fake.pyint(1,1000000)
    accountNumber=fake.pystr_format()
    trader=fake.pystr_format(string_format='????######')
    currencyPair=fake.random_element(elements=('EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'EURGBP', 'EURJPY', 'EURCHF', 'AUDUSD', 'USDCAD'))   
    buySell=fake.random_element(elements=('BUY', 'SELL'))
    counterparty=fake.company()
    rate=fake.pyfloat(positive=True, min_value=0.5, max_value=3.5)
    status=fake.random_element(elements=('NEW', 'UPDATE', 'CANCEL'))

    # Convert to a JSON string.
    return {
        "tradeId": tradeId,
        "tradeDate": tradeDate,
        "notional": notional,
        "accountNumber": accountNumber,
        "trader": trader,
        "currencyPair": currencyPair,
        "buySell": buySell,
        "counterparty": counterparty,
        "rate": rate,
        "status": status
    }

if __name__ == "__main__":
    # Convert map to JSON string.
    payload = gen_payload()
    print(json.dumps(payload))

