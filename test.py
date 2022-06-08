from youtubesearchpython import VideosSearch , VideosSearch.result
l = input('your song: ')
video = VideosSearch(l,limit = 1)
print(video.result()['result'][0]['link'])