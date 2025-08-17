select
  cast(account_id as integer) as account_id,
  cast(customer_id as integer) as customer_id,
  product_type,
  status,
  cast(open_date as date) as open_date
from {{ source('raw','accounts') }}
