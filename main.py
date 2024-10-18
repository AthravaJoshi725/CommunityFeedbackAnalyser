import os
import googleapiclient.discovery
import csv
import re
import json
import pickle
import pandas as pd

def banner():
    print("******************************")
    print("****  YouTube Comments    ****")
    print("******************************")

class Ycom(object):
    def __init__(self):
        self.rpcom = ""
        self.rppubat = ""
        self.rpauth = ""
        self.rplike = ""
        self.tcomment_count = ""
        self.response = ""
        self.video_title = ""

    def make_youtube(self):
        # Disable OAuthlib's HTTPS verification when running locally.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = "AIzaSyBv-jnkjGCMffLa8IyhCc-Z1xC_R0_B9m8"

        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY)

    def extract_video_id(self, url):
        video_id_match = re.search(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|v\/|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
        if video_id_match:
            return video_id_match.group(1)
        else:
            raise ValueError("Invalid YouTube URL")

    def get_video_title(self):
        request = self.youtube.videos().list(
            part="snippet",
            id=self.video_id
        )
        response = request.execute()
        self.video_title = response['items'][0]['snippet']['title']

        def display_comments(self, video_url):
            self.video_id = self.extract_video_id(video_url)
            self.get_video_title()
            comments = []
            try:
                next_page_token = None
                while True:
                    request = self.youtube.commentThreads().list(
                        part="snippet,replies",
                        videoId=self.video_id,
                        maxResults=100,
                        pageToken=next_page_token
                    )
                    res = request.execute()
                    for item in res['items']:
                        comment = {
                            'text': item['snippet']['topLevelComment']['snippet']['textOriginal'],
                            'published_at': item['snippet']['topLevelComment']['snippet']['publishedAt'],
                            'author': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            'like_count': item['snippet']['topLevelComment']['snippet']['likeCount']
                        }
                        comments.append(comment)
                    next_page_token = res.get('nextPageToken')
                    if not next_page_token:
                        break
                return comments
            except Exception as e:
                return {'error': str(e)}
            
        def request_comments(self, video_url):
            self.video_id = self.extract_video_id(video_url)
            self.get_video_title()

            try:
                next_page_token = None
                while True:
                    request = self.youtube.commentThreads().list(
                        part="snippet,replies",
                        videoId=self.video_id,
                        maxResults=100,
                        pageToken=next_page_token
                    )
                    res = request.execute()
                    self.response = res

                    comments_found = False
                    for item in res['items']:
                        self.rpcom = item['snippet']['topLevelComment']['snippet']['textOriginal']
                        self.rppubat = item['snippet']['topLevelComment']['snippet']['publishedAt']
                        self.rpauth = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                        self.rplike = item['snippet']['topLevelComment']['snippet']['likeCount']
                        
                        comments_found = True

                        self.make_csv()

                    next_page_token = res.get('nextPageToken')
                    if not next_page_token:
                        break

                if not comments_found:
                    self.make_csv()
                    return f"No comments found for video ID: {self.video_id}"
                
                return f"Comments successfully extracted for video ID: {self.video_id}"

            except Exception as e:
                return f"Error retrieving comments: {e}"

    def make_csv_json(self):
        file_exists = os.path.isfile('comments.csv')

        with open('comments.csv', 'a', encoding='utf-8', newline='') as csvfile:
            headers = [
                'video_id',
                'comment',
                'published_at',
                'author_display_name',
                'comment_like_count',
                'comment_count',
            ]
            writer = csv.DictWriter(csvfile, delimiter=',',
                                    lineterminator='\n',
                                    fieldnames=headers)

            if not file_exists:
                writer.writeheader()

            try:
                if self.rpcom:
                    writer.writerow({
                        'video_id': self.video_id,
                        'comment': self.rpcom,
                        'published_at': self.rppubat,
                        'author_display_name': self.rpauth,
                        'comment_like_count': self.rplike,
                        'comment_count': self.tcomment_count,
                    })
                else:
                    writer.writerow({
                        'video_id': self.video_id,
                        'comment': 'No comments available',
                        'published_at': self.rppubat,
                        'comment_count': self.tcomment_count,
                    })
            except Exception as e:
                print(f"Error writing to CSV: {e}")

        # Save comments as JSON
        comments = []
        if self.rpcom:
            comments.append({
                'video_id': self.video_id,
                'comment': self.rpcom,
                'published_at': self.rppubat,
                'author_display_name': self.rpauth,
                'comment_like_count': self.rplike,
                'comment_count': self.tcomment_count,
            })
        else:
            comments.append({
                'video_id': self.video_id,
                'comment': 'No comments available',
                'published_at': self.rppubat,
                'comment_count': self.tcomment_count,
            })

        with open('comments.json', 'w') as jsonfile:
            json.dump(comments, jsonfile, indent=2)


    def perform_sentiment_analysis(self):
        # Load the trained model and vectorizer
        model_filename = 'trained_model.sav'
        logistic_model = pickle.load(open(model_filename, 'rb'))

        vectorizer_filename = 'tfidf_vectorizer.sav'
        vectorizer = pickle.load(open(vectorizer_filename, 'rb'))

        # Read comments from JSON
        with open('comments.json', 'r') as jsonfile:
            comments = json.load(jsonfile)

        comments_list = [comment['comment'] for comment in comments]

        # Vectorize the comments
        comments_transformed = vectorizer.transform(comments_list)

        # Predict sentiments
        sentiment_predictions = logistic_model.predict(comments_transformed)

        # Calculate the percentage of positive and negative comments
        positive_percentage = (sum(sentiment_predictions == 1) / len(sentiment_predictions)) * 100
        negative_percentage = (sum(sentiment_predictions == 0) / len(sentiment_predictions)) * 100

        # Return the results as a dictionary
        return {
            'positive': f"{positive_percentage:.2f}%",
            'negative': f"{negative_percentage:.2f}%"
        }


from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    video_title = None
    if request.method == 'POST':
        video_url = request.form['link']
        ycom = Ycom()
        ycom.make_youtube()
        ycom.request_comments(video_url)
        video_title = ycom.video_title
        result = ycom.perform_sentiment_analysis()

    return render_template('index2.html', result=result, video_title=video_title)

if __name__ == '__main__':
    app.run(debug=True)
