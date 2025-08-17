select account_id, customer_id, product_type, status, open_date
from {{ ref('stg_accounts') }}
