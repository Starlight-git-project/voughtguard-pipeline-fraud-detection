import random
from pathlib import Path

import pandas as pd

random.seed(42)

transaction_types_validos = ["POS", "Online", "ATM", "QR"]
transaction_types_invalidos = ["PIX", "Transfer", "", None]

rows = []

# Linhas válidas
for i in range(1, 36):
    rows.append(
        {
            "transaction_id": i,
            "amount": round(random.uniform(10, 5000), 2),
            "hour": random.randint(0, 23),
            "transaction_type": random.choice(transaction_types_validos),
            "is_fraud": random.choice([0, 1]),
            "device_risk_score": random.randint(0, 100),
            "ip_risk_score": random.randint(0, 100),
        }
    )

# Linhas com problemas
for i in range(36, 51):
    rows.append(
        {
            "transaction_id": i if i % 4 != 0 else None,
            "amount": round(random.uniform(10, 5000), 2) if i % 5 != 0 else None,
            "hour": str(random.randint(0, 23)) if i % 3 == 0 else random.randint(0, 23),
            "transaction_type": random.choice(transaction_types_invalidos),
            "is_fraud": random.choice([0, 1, 2, None]),
            "device_risk_score": random.randint(0, 100),
            "ip_risk_score": random.randint(0, 100),
        }
    )

df = pd.DataFrame(rows)
output = Path(__file__).with_name("transacoes_sample.csv")
df.to_csv(output, index=False)