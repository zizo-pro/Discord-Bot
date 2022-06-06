from youtubesearchpython import VideosSearch
l = input('your song: ')
video = VideosSearch(l,limit = 1)
print(video.result()['result'][0]['link'])