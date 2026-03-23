"""Feast entities and feature views for the fraud workshop (minimal)."""
from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32

# Notebook step: create parquet from CSV before `feast apply`:
#   python -c "import pandas as pd; df=pd.read_csv('data/transactions.csv'); df.to_parquet('data/transactions.parquet')"
transactions_source = FileSource(
    name="transactions_parquet",
    path="data/transactions.parquet",
    timestamp_field="event_timestamp",
)

user = Entity(name="user", join_keys=["user_id"])

user_transaction_features = FeatureView(
    name="user_transaction_features",
    entities=[user],
    ttl=timedelta(days=365),
    schema=[
        Field(name="amount", dtype=Float32),
        Field(name="is_fraud", dtype=Float32),
    ],
    online=True,
    source=transactions_source,
)
