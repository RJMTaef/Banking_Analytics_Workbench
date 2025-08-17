select customer_id, age, tenure_months, risk_score, province, join_date
from {{ ref('stg_customers') }}
