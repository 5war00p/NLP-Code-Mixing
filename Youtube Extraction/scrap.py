# -*- coding: utf-8 -*-

# Sample Python code for youtube.commentThreads.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import json
from dotenv import load_dotenv
import googleapiclient.discovery


load_dotenv()

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = os.getenv('YOUTUBE_API_KEY')

YOUTUBE = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)

def reqCommentThreads(videoId, maxResults=100, pageToken=None):

    request = YOUTUBE.commentThreads().list(
        part="snippet,replies",
        maxResults=maxResults,
        textFormat="plainText",
        videoId=videoId, 
        pageToken = pageToken,
    )

    response = request.execute()

    return response

def main():

    videoId = input('Enter videoID: ')

    # maxResults = input('Enter max CommentThread count: ')
    

    response = reqCommentThreads(videoId)

    rawResponse = [response]
    finalData = []

    data = filterJSON(response)
    finalData.extend(data)

    try:
        totalPages = response['pageInfo']['totalResults']
        for _ in range(totalPages):
            
            if 'nextPageToken' not in response:
                break

            nextPageToken = response['nextPageToken']
            response = reqCommentThreads(videoId, nextPageToken)
            rawResponse.append(response)
            data = filterJSON(response)
            finalData.extend(data)


    except KeyError:
        print('totalResults Key not Found!!')
        print(response)

    with open('raw.json', 'w', encoding='utf-8') as outfile:
        json.dump(rawResponse, outfile)

    with open('data.txt', 'w', encoding='utf-8') as outfile:
        for line in finalData:
            outfile.write("%s\n" % line)


def filterJSON(response):
    items = response['items']

    comments_data = []
    for item in items:
        try:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comment = comment.replace('\n', ' ')
            comments_data.append(comment)

            if 'replies' in item:
               comment_replies= item['replies']['comments']
               for reply in comment_replies:
                    comment_reply = reply['snippet']['textDisplay']
                    comment_reply = comment_reply.replace('\n', ' ')
                    comments_data.append(comment_reply)
        except KeyError:
            print('textDisplay Key not Found!!')

    return comments_data

if __name__ == "__main__":
    main()