{{
    config(
        materialized='incremental',
        unique_key='event_id'
    )
}}

with source as (
    select * from {{ source('raw_data', 'raw_github_events') }}
    
    {% if is_incremental() %}
        -- Only process events ingested since the latest event in the target table
        where ingested_at > (select max(ingested_at) from {{ this }})
    {% endif %}
),

renamed_and_parsed as (
    select
        event_id,
        event_type,
        actor_login,
        repo_name,
        created_at,
        ingested_at,
        
        -- JSON parsing
        json_extract_string(raw_payload, '$.public')::boolean as is_public,
        json_extract_string(raw_payload, '$.org.login') as org_login,
        json_extract_string(raw_payload, '$.payload.action') as action,
        json_extract_string(raw_payload, '$.payload.ref') as git_ref

    from source
)

select * from renamed_and_parsed