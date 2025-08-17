select
  cast(tx_id as integer) as tx_id,
  cast(customer_id as integer) as customer_id,
  cast(account_id as integer) as account_id,
  cast(branch_id as integer) as branch_id,
  cast(amount as double) as amount,
  channel,
  merchant_code,
  cast(ts as timestamp) as ts
from {{ source('raw','transactions') }}
