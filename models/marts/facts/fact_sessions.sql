select
  cast(session_id as integer) as session_id,
  cast(customer_id as integer) as customer_id,
  device_type,
  cast(start_ts as timestamp) as start_ts,
  cast(duration_s as integer) as duration_s,
  cast(events_count as integer) as events_count,
  cast(conv_flag as integer) as conv_flag
from {{ source('raw','digital_sessions') }}
