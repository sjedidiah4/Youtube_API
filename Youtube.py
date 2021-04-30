import requests
import json
from tqdm import tqdm #To add a progress bar in order to track the progress of the application


class YTstats:

    def __init__(self, api_key, channel_id):
        self.api_key = api_key
        self.channel_id = channel_id
        self.channel_statistics = None
        self.video_data = None
    
    def get_channel_statistics(self):
        url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id={self.channel_id}&key={self.api_key}'
        #print (url)
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        #print (data)
        try:
            data = data["items"][0]["statistics"]
        except:
            data = None
        
        self.channel_statistics = data
        return data
    def get_channel_video_data(self):
        channel_videos = self._get_channel_videos(limit=50)
        #print (channel_videos)
        #print (len(channel_videos)) #The number of the videos found - in this case, 298

        parts = ["snippet", "statistics", "contentDetails"]

        for video_id in tqdm(channel_videos):     #tqdm implemented here
            for part in parts:
                data = self._get_single_video_data(video_id, part)
                channel_videos[video_id].update(data)

        self.video_data = channel_videos
        return channel_videos
            
    def _get_single_video_data(self, video_id, part):
        url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key={self.api_key}"
        json_url = requests.get(url)
        data = json.loads(json_url.text) #Now a dictionary
        try:
            data = data['items'][0][part]
        except:
            print('Try again')
            data = dict()

        return data

    
    def _get_channel_videos(self, limit = None):
        url = f"https://www.googleapis.com/youtube/v3/search?key={self.api_key}&channelId={self.channel_id}&part=id&order=date"
        if limit is not None and isinstance(limit, int):
            url += "&maxResults=" + str(limit)
        #print (url)

        vid, npt = self._get_channel_videos_per_page(url)
        idx = 0
        while(npt is not None and idx < 5):
            nexturl = url +"&pageToken=" + npt
            next_vid, npt = self._get_channel_videos_per_page(nexturl)
            vid.update(next_vid)
            idx+=1
        return vid
    


    def _get_channel_videos_per_page(self, url):
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        channel_videos = dict() #empty dictionary
        if 'items' not in data:
            return channel_videos, None

        item_data = data['items']
        nextPageToken = data.get("nextPageToken", None)
        for item in item_data:
            try:
                kind = item['id']['kind']
                if kind == 'youtube#video':
                    video_id = item['id']['videoId']
                    channel_videos[video_id]=dict()
            except KeyError:
                print('Try again')
        return channel_videos, nextPageToken


    def dump(self):
        if self.channel_statistics is None or self.video_data is None:
            print ("There is no data")
            return

        fused_data = {self.channel_id:{"channel_statistics": self.channel_statistics, "video_data": self.video_data}}
        channel_title = self.video_data.popitem()[1].get('channelTitle', self.channel_id)
        channel_title = channel_title.replace(" ", "_").lower()
        file_name = channel_title + '.json'
        with open(file_name, 'w') as f:
            json.dump(fused_data, f, indent = 4)

        print('file dumped')