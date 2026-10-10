with staging as (
    select * from {{ ref('stg_github_events') }}
),

daily_metrics as (
    select
        date_trunc('day', created_at) as event_date,
        repo_name,
        count(distinct event_id) as total_events,
        count(distinct actor_login) as unique_contributors,
        
        -- Event-type counts
        count(case when event_type = 'PushEvent' then 1 end) as push_count,
        count(case when event_type = 'WatchEvent' then 1 end) as star_count,
        count(case when event_type = 'PullRequestEvent' then 1 end) as pr_count,
        count(case when event_type = 'IssuesEvent' then 1 end) as issue_count

    from staging
    group by 1, 2
)

select * from daily_metrics
order by event_date desc, total_events desc