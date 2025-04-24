import random

def read():
    return {
        "temperature": round(20 + random.random() * 5, 2),
        "humidity":    round(40 + random.random() * 20, 1)
    }