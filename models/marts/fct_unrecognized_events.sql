with staging as (
    select * from {{ ref('stg_github_events') }}
)

select
    event_type,
    count(*) as occurrence_count,
    min(created_at) as first_seen,
    max(created_at) as last_seen
from staging
where event_type not in ('PushEvent', 'WatchEvent', 'PullRequestEvent', 'IssuesEvent', 'CreateEvent', 'ForkEvent')
group by 1