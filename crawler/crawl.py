import requests as r
import re, json, os, datetime

# ENVIRONMENT VARIABLES
# youtube API key to fetch videos and their description
SECRET_YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]

# github personal API token, to post the parsed data to a gist to host the JSON for free
SECRET_GITHUB_GIST_TOKEN = os.environ["GIST_API_KEY"]

# your channel id
CHANNEL_ID = os.environ['CHANNEL_ID']

# github gist's id to which we post the data to, you might have to create two empty files called `data.json` and `processed.json` while creating the gist
# github's personal token created above should have perms to creating/updating gists 
DB_GIST_ID = os.environ["DB_GIST_ID"]

# regex for timestamps in the video desc.
ts_regex = re.compile(r"^(\d+)+:(\d+)+:?(\d+)? (.*)$")

# helper function to expand out youtube API queries
def api(query):
    return f'https://www.googleapis.com/youtube/v3/{query}&key={SECRET_YOUTUBE_API_KEY}'

# if we already parsed a video, skip it, otherwise call an API to fetch the data for a video_id
def get_video_info(video_id, processed_vids):
    if video_id in processed_vids:
        print(f'skipping already processed {video_id}')
        return None
    print(f"Fetching info for {video_id}")
    q = f'videos?id={video_id}&part=snippet'
    res = r.get(api(q)).json()
    item = res['items'][0]['snippet']
    return {
        'id':video_id,
        'published_at': item['publishedAt'],
        'title':item['title'],
        'desc':item['description'],
        'thumbnail':item['thumbnails']['standard']['url']
    }

# get parsed vod data
def get_vods():
    next_page = '1'
    video_ids = []
    # get list of video ids, API limits max results to 50 per query 
    # so we keep calling until there are no videos 
    while next_page is not None:
        q = f'search?channelId={CHANNEL_ID}&maxResults=50&order=date&type=video'
        if next_page != None and next_page != '1':
            q = f'{q}&pageToken={next_page}'
        res = r.get(api(q)).json()
        try:
            next_page = res['nextPageToken']
        except:
            next_page = None
        video_ids += [x['id']['videoId'] for x in res['items']]

    # we keep track of already processed vids to our gist, so we don't parse them twice
    processed_res = r.get(f'https://api.github.com/gists/{DB_GIST_ID}').json()
    processed_vids = json.loads(processed_res['files']['processed.json']['content'])
    
    vods = []
    
    for video_id in video_ids:
        vod = get_video_info(video_id, processed_vids)
        if vod is not None:
            vods.append(vod)
    
    print(f'fetched {len(vods)} videos.')
    return vods

# parse the video desc for timestamps
# vid is a result of `get_video_info`
def parse_desc(vid): 
    lines = vid['desc'].split('\n')
    matches = []
    for line in lines:
        r_matches = ts_regex.findall(line)
        if r_matches is None:
            continue
        for single_match in r_matches:
            sm = []
            for m in single_match:
                if m != '':
                    sm.append(m)
            # timestamp only has mins and seconds
            if(len(sm) == 3):
                matches.append({
                    "title":f'{sm[2]} - {vid["title"]}', 
                    "url":f'https://youtube.com/watch?v={vid["id"]}&t={sm[0]}m{sm[1]}s', 
                    'published_at':vid['published_at'],
                    "thumbnail": vid['thumbnail']
                    })
            # timestamp has hours mins and seconds
            elif(len(sm) == 4):
                matches.append({
                    'title':f'{sm[3]} - {vid["title"]}',
                    "url": f'https://youtube.com/watch?v={vid["id"]}&t={sm[0]}h{sm[1]}m{sm[2]}s', 
                    'published_at':vid['published_at'],
                    "thumbnail":vid['thumbnail']})
    return matches

# helper function to call `parse_desc` on each `vid` dict   
def parse_vods(vods):
    res = []
    for i in range(len(vods)):
        for match in parse_desc(vods[i]):
            if match is not None:
                res.append(match)
    return res

# helper function for using github gists api
def gist_api(method, query, data):
    headers = { 
        "Accept":"application/vnd.github+json", 
        "Authorization": f"Bearer {SECRET_GITHUB_GIST_TOKEN}", 
        "X-GitHub-Api-Version": "2022-11-28"
    }
    BASE = 'https://api.github.com'
    if method == "GET":
        res = r.get(BASE+query, headers=headers).json()
    elif method == "PATCH":
        res = r.patch(BASE+query, headers=headers, data=data).json()
    return res

# post processed data to gist
def post_vods_to_gist(vods, raw_vods):
    existing_data = r.get(f'https://api.github.com/gists/{DB_GIST_ID}').json()
    existing_vods = []
    try:
        existing_vods_r = json.loads(existing_data['files']['data.json']['content'])
        existing_vods = existing_vods_r['items']
    except:
        pass
    existing_processed = []
    try:
        existing_processed_r = json.loads(existing_data['files']['processed.json']['content'])
        existing_processed = existing_processed_r
    except:
        pass

    # sort the results based on `published_at` so more recent videos come to the top
    vods = sorted(vods, key=lambda x: datetime.datetime.fromisoformat(x['published_at'][:-1]), reverse=True)

    vods += existing_vods

    # idk sometimes we might fetch twice, so we remove duplicates from the result, probably don't need this
    vods = list({x['url']:x for x in vods}.values())
    

    vods_content = json.dumps({
        "updated_at":datetime.datetime.isoformat(datetime.datetime.now()),
        "items": vods
    })
    processed_content = [x['id'] for x in raw_vods]
    processed_content += existing_processed
    processed_content = json.dumps(list(set(processed_content)))
    data = {
        "files":{
            "data.json":{
                "content":vods_content
            },
            "processed.json":{
                "content":processed_content
            }
        }
    }
    gist_api('PATCH', f'/gists/{DB_GIST_ID}', json.dumps(data))


# this will be called from the lambda_event
def main():
    raw_vods = get_vods()
    parsed_vods = parse_vods(raw_vods)
    post_vods_to_gist(parsed_vods, raw_vods)

if __name__ == 'main':
    main()
