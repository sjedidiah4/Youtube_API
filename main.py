
from Youtube import YTstats

API_KEY = "AIzaSyA2QaZVQFz13wa4pggMMlJR3DRn27tRHPA"

channel_id = "UCFbNIlppjAuEX4znoulh0Cw"
yt = YTstats(API_KEY, channel_id)
yt.get_channel_statistics()
yt.get_channel_video_data()
yt.dump()
