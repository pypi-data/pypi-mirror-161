# Meta configs
META_API_GRAPH_URL = "https://graph.facebook.com/"
META_API_GRAPH_VERSION = "v14.0"

# Fields
INSTAGRAM_BUSINESS_ACCOUNT = "instagram_business_account"
MEDIA_FIELDS = "caption,media_product_type,media_type,media_url,permalink,timestamp"
ACCESS_TOKEN = "access_token"

# Enpoints or operations
LONG_LIVED_TOKEN = "/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={api_key_secret}&fb_exchange_token={token}"
GET_ACCOUNTS = "/me/accounts"
GET_BUSINESS_ACCOUNT = "/{account_id}?fields=instagram_business_account"
SEARCH_IG_HASHTAG = "/ig_hashtag_search?user_id={ig_business_account_id}&q={query}"
RESENT_MEDIA = (
    "/{hashtag_id}/recent_media?fields={fields}&user_id={ig_business_account_id}"
)
TOP_MEDIA = "/{hashtag_id}/top_media?fields={fields}&user_id={ig_business_account_id}"
