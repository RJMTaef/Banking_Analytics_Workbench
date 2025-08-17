select tx_id, customer_id, account_id, branch_id, amount, channel, merchant_code, ts
from {{ ref('stg_transactions') }}
