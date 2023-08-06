import uuid
import random
from datetime import datetime, timedelta
from collections import defaultdict

symbol_choices = ["ZM", "AAPL", "FB", "TSLA", "UCO", "FORD"]


def create_signal():
    date = datetime.fromisoformat("2022-01-22")
    signals_x = [date.timestamp()]
    signals_y = [random.random() * 500 + 100]
    for i in range(500):
        date += timedelta(minutes=1)
        signals_x.append(date.timestamp())
        signals_y.append(signals_y[-1] + random.random() * 20 - 10)
    return list(zip(signals_x, signals_y))


def price_data_iter():
    index = 0
    all_signals = defaultdict(create_signal)
    while True:
        price_data = {
            id_: {
                "id": id_,
                "symbol": p,
                "position": "Long" if random.random() > 0.5 else "Short",
                "quantity": int(random.random() * 20) + 1,
                "signal": all_signals[p][:index],
                "p": (all_signals[p][index][1] - all_signals[p][0][1])
                / all_signals[p][0][1],
                "d": all_signals[p][index][1] - all_signals[p][0][1],
            }
            for id_, p in [
                (uuid.uuid1().hex, random.choice(symbol_choices)) for _ in range(10)
            ]
        }
        index = index + 1 if index < 200 else 1
        yield price_data


def invested_data_iter():
    index = 1
    all_signals = defaultdict(create_signal)
    while True:
        data = {
            t: {
                "id": t,
                "signal": all_signals[t][:index],
                "p": (all_signals[t][index][1] - all_signals[t][0][1])
                / all_signals[t][0][1],
                "d": all_signals[t][index][1] - all_signals[t][0][1],
            }
            for t in ["d", "w", "m", "y"]
        }
        index = index + 1 if index < 200 else 1
        yield data


positions = {
    "1": {
        "id": "1",
        "symbol": "AAPL",
        "position": "long",
        "quantity": 2,
        "created_at": "2021-10-25 22:24",
        "original_price": 125.3,
        "current_price": 156.6,
        "total_return": 12,
        "tag": "MACD",
    },
    "2": {
        "id": "2",
        "symbol": "AMZN",
        "position": "short",
        "quantity": 3,
        "created_at": "2021-11-04 02:56",
        "original_price": 2256.4,
        "current_price": 2832.2,
        "total_return": 8,
        "tag": "MACD",
    },
    "3": {
        "id": "3",
        "symbol": "FB",
        "position": "short",
        "quantity": 3,
        "created_at": "2021-03-04 02:56",
        "original_price": 256.4,
        "current_price": 248.2,
        "total_return": 4,
        "tag": "MACD",
    },
    "4": {
        "id": "4",
        "symbol": "ZOOM",
        "position": "long",
        "quantity": 4,
        "created_at": "2021-06-01 02:56",
        "original_price": 350.4,
        "current_price": 250.6,
        "total_return": 27,
        "tag": "MACD",
    },
    "5": {
        "id": "5",
        "symbol": "AMD",
        "position": "long",
        "quantity": 10,
        "created_at": "2020-03-05 02:56",
        "original_price": 145.4,
        "current_price": 275.6,
        "total_return": 45,
        "tag": "MACD",
    },
    "6": {
        "id": "6",
        "symbol": "UCO",
        "position": "long",
        "quantity": 50,
        "created_at": "2020-01-05 13:03",
        "original_price": 22.4,
        "current_price": 85.6,
        "total_return": 50,
        "tag": "MACD",
    },
    "7": {
        "id": "7",
        "symbol": "NGR",
        "position": "short",
        "quantity": 6,
        "created_at": "2021-09-05 13:03",
        "original_price": 22.4,
        "current_price": 18.6,
        "total_return": 7.6,
        "tag": "MACD",
    },
    "8": {
        "id": "8",
        "symbol": "FB",
        "position": "short",
        "quantity": 3,
        "created_at": "2021-03-04 02:56",
        "original_price": 256.4,
        "current_price": 248.2,
        "total_return": 4,
        "tag": "MACD",
    },
    "9": {
        "id": "9",
        "symbol": "ZOOM",
        "position": "long",
        "quantity": 4,
        "created_at": "2021-06-01 02:56",
        "original_price": 350.4,
        "current_price": 250.6,
        "total_return": 27,
        "tag": "MACD",
    },
    "10": {
        "id": "10",
        "symbol": "AMD",
        "position": "long",
        "quantity": 10,
        "created_at": "2020-03-05 02:56",
        "original_price": 145.4,
        "current_price": 275.6,
        "total_return": 45,
        "tag": "MACD",
    },
    "11": {
        "id": "11",
        "symbol": "UCO",
        "position": "long",
        "quantity": 50,
        "created_at": "2020-01-05 13:03",
        "original_price": 22.4,
        "current_price": 85.6,
        "total_return": 50,
        "tag": "MACD",
    },
    "12": {
        "id": "12",
        "symbol": "NGR",
        "position": "short",
        "quantity": 6,
        "created_at": "2021-09-05 13:03",
        "original_price": 22.4,
        "current_price": 18.6,
        "total_return": 7.6,
        "tag": "MACD",
    },
    "13": {
        "id": "13",
        "symbol": "FB",
        "position": "short",
        "quantity": 3,
        "created_at": "2021-03-04 02:56",
        "original_price": 256.4,
        "current_price": 248.2,
        "total_return": 4,
        "tag": "MACD",
    },
    "14": {
        "id": "14",
        "symbol": "ZOOM",
        "position": "long",
        "quantity": 4,
        "created_at": "2021-06-01 02:56",
        "original_price": 350.4,
        "current_price": 250.6,
        "total_return": 27,
        "tag": "MACD",
    },
    "15": {
        "id": "15",
        "symbol": "AMD",
        "position": "long",
        "quantity": 10,
        "created_at": "2020-03-05 02:56",
        "original_price": 145.4,
        "current_price": 275.6,
        "total_return": 45,
        "tag": "MACD",
    },
    "16": {
        "id": "16",
        "symbol": "UCO",
        "position": "long",
        "quantity": 50,
        "created_at": "2020-01-05 13:03",
        "original_price": 22.4,
        "current_price": 85.6,
        "total_return": 50,
        "tag": "MACD",
    },
    "17": {
        "id": "17",
        "symbol": "NGR",
        "position": "short",
        "quantity": 6,
        "created_at": "2021-09-05 13:03",
        "original_price": 22.4,
        "current_price": 18.6,
        "total_return": 7.6,
        "tag": "MACD",
    },
}
