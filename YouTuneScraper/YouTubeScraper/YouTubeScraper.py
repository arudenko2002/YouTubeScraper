'''
Created on Jul 20, 2017

@author: Alexey
'''
import requests
import json
import time
from datetime import datetime
API_KEY="AIzaSyAXEt-F3-BiofCYbvhkZYcou6CKFX0s6wA"
SEARCH_VIDEO_LIST="https://www.googleapis.com/youtube/v3/search?channelId=%s&key=%s&part=snippet"
SEARCH_VIDEO_STAT = "https://www.googleapis.com/youtube/v3/videos?id=%s&part=statistics&key=%s"
SEARCH_SUBSCRIBERS = "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=%s&key=%s"
SCRAPE_DATE = str(datetime.utcnow()).replace(' ','T')[:23]+'Z'

class YouTubeScraper:
    def getVideoList(self,channelId):
        result=[]
        url = SEARCH_VIDEO_LIST % (channelId, API_KEY)
        url2=url
        nextPageToken="0"
        count=0
        subscriberCount = self.getChannelStats(channelId)
        
        while len(nextPageToken)>0:
            try:
                q = requests.get(url=url2)
            except:
                print "Slept 3 sec"
                time.sleep(3)
                continue  
            
            qq=json.loads(q.content)
            if "nextPageToken" in qq:
                nextPageToken=qq["nextPageToken"]
            else:
                nextPageToken=""
            list_count=int(qq["pageInfo"]["totalResults"])
            items = qq["items"]
            videoids=[]
            tmpresult={}
            for it in items:
                if "videoId" in it["id"]:
                    video={}
                    video["videoId"] = it["id"]["videoId"]
                    video["title"] = it['snippet']['title']
                    video["channelId"] = it['snippet']['channelId']
                    video["publishedAt"] = it['snippet']['publishedAt']
                    video["channelTitle"] = it['snippet']['channelTitle']
                    video["description"] = it['snippet']['description']
                    video["subscriberCount"] = subscriberCount
                    videoids.append(video["videoId"])    
                    tmpresult[video["videoId"]]=video   
                    count=count+1

            videos = ','.join(videoids)
            stats = self.getVideoStats(videos)
            for videoId in videoids:
                tmpresult[videoId]["stats"]=stats[videoId]
                result.append(tmpresult[videoId])
            if len(result)>=list_count:
                nextPageToken=""
                break
            url2=url+"&pageToken="+nextPageToken
        return result
    
    def getVideoStats(self,videoids):
        if len(videoids)==0:
            return None
        url = SEARCH_VIDEO_STAT % (videoids, API_KEY)

        print url
        while True:
            try:
                q = requests.get(url=url)
                break
            except:
                print "slept 3sec"
                time.sleep(3)

        qq = json.loads(q.content)
        items = qq["items"]
        result={}
        for it in items:
            videoId = it["id"]
            if "id" in it and "statistics" in  qq["items"][0]:
                stat = qq["items"][0]["statistics"]
                if "viewCount" not in stat:
                    stat["viewCount"]=0
                if "likeCount" not in stat:
                    stat["likeCount"]=0
                if "dislikeCount" not in stat:
                    stat["dislikeCount"]=0
                if "commentCount" not in stat:
                    stat["commentCount"]=0
                if "favoriteCount" not in stat:
                    stat["favoriteCount"]=0
                result[it["id"]] = stat
        return result
                
    def getChannelStats(self,channelId):
        url = SEARCH_SUBSCRIBERS % (channelId, API_KEY)
        
        while True:
            try:
                q = requests.get(url=url)
                break
            except:
                print "slept 3sec"
                time.sleep(3)
        
        qq = json.loads(q.content)
        subscriberCount = qq["items"][0]["statistics"]["subscriberCount"]
        return subscriberCount
    
    def processChannels(self,channels,output):
        for channel in channels:
            list = self.getVideoList(channel)
            self.addToFileCSV(list,output)
            
    def addToFileCSV(self,list,output):
        file = open(output,"a")
        for it in list:
            line = '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"' % (it["channelId"], it["channelTitle"], str(it["subscriberCount"]), it["videoId"], it["title"].replace('"',"'"), it["description"].replace('"',"'"), it["publishedAt"], str(it["stats"]["viewCount"]), str(it["stats"]["likeCount"]), str(it["stats"]["dislikeCount"]), str(it["stats"]["commentCount"]), SCRAPE_DATE)
            line=line.encode(encoding='UTF-8',errors='ignore')
            file.write(line+"\n")
        file.close()
        
if __name__ == '__main__':
    channels = [
        "UC-8Q-hLdECwQmaWNwXitYDw", 
        "UC8xDSf5LRGwEf5v9iH6xrwg", 
        "UCzH3iADRIq1IJlIXjfNgTpA", 
        "UCuVHOs0H5hvAHGr8O4yIBNQ", 
        "UCnPg1XCi1ZY7TbL3Yru__FQ", 
        "UCyhbeojvMcNcAVOIBlQ-41Q", 
        "UC2LgZ_4GzSFQS-3a87_Jc6w", 
        "UC3HlKrAmvpZItrX-tiITI4g", 
        "UCQ2IqAJyjCkVMGCd5kAZ2ow"
        ] 
    yts = YouTubeScraper() 
    yts.processChannels(channels,"channel_daily_stats.csv")
    pass