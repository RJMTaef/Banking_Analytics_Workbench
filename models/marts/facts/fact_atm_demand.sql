select
  cast(branch_id as integer) as branch_id,
  cast(date as date) as date,
  cast(cash_withdrawn as double) as cash_withdrawn,
  cast(withdrawals_cnt as integer) as withdrawals_cnt
from {{ source('raw','atm_withdrawals') }}
