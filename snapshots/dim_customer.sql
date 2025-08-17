{% snapshot snap_dim_customer %}
{{
  config(
    target_schema='snapshots',
    unique_key='customer_id',
    strategy='check',
    check_cols=['age','tenure_months','risk_score','province']
  )
}}
select * from {{ source('raw','customers') }}
{% endsnapshot %}
