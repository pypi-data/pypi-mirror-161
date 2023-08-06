# constant are defined here to ease access across all project
CLIENTS_PARAM = 'authorized_clients'
ALL_CLIENTS_RIGHTS = 'all'

class UserRightsEnum:
    ADSCALE = 'adscale_media'
    FDA = 'fda'
    ADMIN_TOOLS = 'admin_tools'
    AMS_FEED = 'ams_feed'
    AMS_MEDIA = 'ams_media'
    HUBMETRICS = 'hubmetrics'
    ADSCALE_GTP = 'adscale_gtp'
    AMS_GTP = 'ams_gtp'
    AMS_LAB = 'ams_lab'
    USERS = 'users'

class RightsLevelEnum:
    NONE = 0
    VIEWER = 1
    EDITOR = 2
    ADMIN = 3
