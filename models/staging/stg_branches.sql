select
  cast(branch_id as integer) as branch_id,
  name,
  province,
  cast(lat as double) as lat,
  cast(lon as double) as lon
from {{ source('raw','branches') }}
