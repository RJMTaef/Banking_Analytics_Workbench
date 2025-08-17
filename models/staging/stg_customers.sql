select
  cast(customer_id as integer) as customer_id,
  cast(age as integer) as age,
  cast(tenure_months as integer) as tenure_months,
  cast(risk_score as integer) as risk_score,
  province,
  cast(join_date as date) as join_date
from {{ source('raw','customers') }}
