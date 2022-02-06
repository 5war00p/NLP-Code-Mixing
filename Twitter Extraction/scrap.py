import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.getenv('TWITTER_API_KEY')

def getComments(tweets):

    MAX_SEARCH_TWT_LIMIT = 270

    text = []
    next_token = ''
    count = 0
    for index, tweet in enumerate(tweets):

        if count == MAX_SEARCH_TWT_LIMIT:
            break
        
        while True:

            if count == MAX_SEARCH_TWT_LIMIT:
                break

            if next_token != '':
                url = f'https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{tweet}&max_results=100&next_token={next_token}'
            else:
                url = f'https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{tweet}&max_results=100'

            
            response = connect_to_endpoint(url)

            count += 1
            
            print('tweet-{}_{}_{}'.format(index+1, tweet, next_token))
            
            if 'data' in response:
                for twt in response['data']:
                    text.append(twt['text'])

            if 'meta' in response and 'next_token' in response['meta']:
                next_token = response['meta']['next_token']
            else:
                break

    return text

def getTweetComments(data):

    MAX_TWT_LOOKUP = 900

    tweetIDs = {}
    next_token = ''
    
    window_count = 0

    for user in data:

        id = user["id"]
        tweetIDs[id] = []
        
        if window_count == MAX_TWT_LOOKUP:
            break

        while True:
            
            if window_count == MAX_TWT_LOOKUP:
                break

            if next_token != '':
                url = f'https://api.twitter.com/2/users/{id}/tweets?&max_results=100&pagination_token={next_token}'
            else:
                url = f'https://api.twitter.com/2/users/{id}/tweets?&max_results=100'

            response = connect_to_endpoint(url)
            window_count += 1

            if 'data' in response:
                tweetIDs[id].extend([twt['id'] for twt in response['data']])
            
            if 'meta' in response and 'next_token' in response['meta']:
                next_token = response['meta']['next_token']
            else:
                break

        text = getComments(tweetIDs[id])
        with open(user['username'] + '.txt', 'w', encoding='utf-8') as outfile:
            for line in text:
                outfile.write("%s\n" % line)

def getUserIDs(usernames):
    usernames = f"usernames={usernames}"

    url = "https://api.twitter.com/2/users/by?{}".format(usernames)
    response = connect_to_endpoint(url)

    return response['data']


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def main():
    usernames = input('Enter username: ')
    users = getUserIDs(usernames)
    getTweetComments(users)


if __name__ == "__main__":
    main()