
SCHEMA_FILENAME = "schema.json"
STORAGE_BUCKET_NAME = ""
FACEBOOK_CREDENTIALS_NAME = ""
SECRET_PROJECT_ID = ""

API_VERSION = "v10.0/"
HOST = "https://graph.facebook.com/"

ACCOUNT_GENERAL_DATA_ENDPOINT = HOST + API_VERSION + "{}"
ACCOUNT_INSIGHTS_ENDPOINT = HOST + API_VERSION + "{}/insights"
MEDIA_ID_ENDPOINT = HOST + API_VERSION + "{}/posts"
MEDIA_GENERAL_DATA_ENDPOINT = HOST + API_VERSION + "{}"
MEDIA_INSIGHTS_ENDPOINT = HOST + API_VERSION + "{}/insights"

ACCOUNT_FIELDS = [
    "id",
    "about",
    "username",
    "bio",
    "link",
    "fan_count",
    "followers_count",
    "engagement",
    "checkins",
    "new_like_count",
    "talking_about_count",
    "were_here_count",
    "unread_message_count",
    "unread_notif_count",
    "unseen_message_count"
]
ACCOUNT_METRICS = {
    "day": [
        "page_messages_new_conversations_unique",
        "page_video_views",
        "page_views_total",
        "page_total_actions",
        "page_daily_follows_unique",
        "page_impressions",
        "page_impressions_unique",
        "page_impressions_paid",
        "page_impressions_paid_unique",
        "page_impressions_organic",
        "page_impressions_organic_unique",
        "page_impressions_viral",
        "page_impressions_viral_unique",
        "page_engaged_users",
        "page_post_engagements",
        "page_consumptions",
        "page_consumptions_unique",
        "page_places_checkin_total",
        "page_places_checkin_total_unique",
        "page_places_checkin_mobile",
        "page_places_checkin_mobile_unique",
        "page_negative_feedback",
        "page_negative_feedback_unique",   
        "page_posts_impressions",
        "page_posts_impressions_unique",
        "page_posts_impressions_paid",
        "page_posts_impressions_paid_unique",
        "page_posts_impressions_organic",
        "page_posts_impressions_organic_unique",
        "page_posts_impressions_viral",
        "page_posts_impressions_viral_unique",
        "page_posts_impressions_nonviral",
        "page_posts_impressions_nonviral_unique",
        "page_actions_post_reactions_like_total",
        "page_actions_post_reactions_love_total",
        "page_actions_post_reactions_wow_total",
        "page_actions_post_reactions_haha_total",
        "page_actions_post_reactions_sorry_total",
        "page_actions_post_reactions_anger_total"       
    ],
    "lifetime": [
    ]
}
MEDIA_FIELDS = [
    "id",
    "actions",
    "full_picture",
    "created_time",
    "from",
    "message"
]
MEDIA_METRICS = [
        "post_impressions", 
        "post_impressions_unique", 
        "post_impressions_paid", 
        "post_impressions_paid_unique", 
        "post_impressions_fan", 
        "post_impressions_fan_unique", 
        "post_impressions_fan_paid", 
        "post_impressions_fan_paid_unique", 
        "post_impressions_organic", 
        "post_impressions_organic_unique", 
        "post_impressions_viral", 
        "post_impressions_viral_unique", 
        "post_impressions_nonviral", 
        "post_impressions_nonviral_unique", 
        "post_engaged_users", 
        "post_negative_feedback", 
        "post_negative_feedback_unique", 
        "post_engaged_fan", 
        "post_clicks", 
        "post_clicks_unique", 
        "post_reactions_like_total", 
        "post_reactions_love_total", 
        "post_reactions_wow_total", 
        "post_reactions_haha_total", 
        "post_reactions_sorry_total", 
        "post_reactions_anger_total", 
        "post_video_avg_time_watched",
        "post_video_complete_views_organic",
        "post_video_complete_views_organic_unique", 
        "post_video_complete_views_paid", 
        "post_video_complete_views_paid_unique", 
        "post_video_views_organic", 
        "post_video_views_organic_unique", 
        "post_video_views_paid", 
        "post_video_views_paid_unique", 
        "post_video_length", 
        "post_video_views", 
        "post_video_views_unique",
    ]
