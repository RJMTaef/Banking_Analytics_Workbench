select branch_id, name, province, lat, lon
from {{ ref('stg_branches') }}
