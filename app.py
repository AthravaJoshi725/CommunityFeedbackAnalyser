import os
import googleapiclient.discovery
import re
import pickle
import streamlit as st

def banner():
    st.title("YouTube Comments Sentiment Analysis")

class Ycom(object):
    def __init__(self):
        self.video_title = ""

    def make_youtube(self):
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

    def perform_sentiment_analysis(self, comments):
        model_filename = 'trained_model.sav'
        logistic_model = pickle.load(open(model_filename, 'rb'))

        vectorizer_filename = 'tfidf_vectorizer.sav'
        vectorizer = pickle.load(open(vectorizer_filename, 'rb'))

        comments_list = [comment['text'] for comment in comments]

        comments_transformed = vectorizer.transform(comments_list)
        sentiment_predictions = logistic_model.predict(comments_transformed)

        # Add the sentiment label to each comment
        for comment, sentiment in zip(comments, sentiment_predictions):
            comment['sentiment'] = 'positive' if sentiment == 1 else 'negative'

        positive_percentage = (sum(sentiment_predictions == 1) / len(sentiment_predictions)) * 100
        negative_percentage = (sum(sentiment_predictions == 0) / len(sentiment_predictions)) * 100

        return {
            'positive': f"{positive_percentage:.2f}%",
            'negative': f"{negative_percentage:.2f}%",
            'comments_with_sentiment': comments
        }

    def perform_spam_detection(self, comments):
        model_filename = 'model_spamDetect.pkl'    
        spam_model = pickle.load(open(model_filename,'rb'))

        comment_texts = [comment['text'] for comment in comments]
        spam_predictions = spam_model.predict(comment_texts)

        spam_percentage = (sum(spam_predictions == 1) / len(spam_predictions)) * 100
        filtered_comments = [comment for comment, spam in zip(comments, spam_predictions) if spam == 0]

        return {
            'spam_percentage': spam_percentage,
            'filtered_comments': filtered_comments
        }
    
    def perform_emotion_detection(self, comments):
        model_filename = 'emotion_detect.pkl'
        emotion_model = pickle.load(open(model_filename, 'rb'))
        
        comments_text = [comment['text'] for comment in comments]

        emotion_predictions = emotion_model.predict(comments_text)

        sad_comments = [comment for comment, label in zip(comments, emotion_predictions) if label == 0]
        joy_comments = [comment for comment, label in zip(comments, emotion_predictions) if label == 1]
        anger_comments = [comment for comment, label in zip(comments, emotion_predictions) if label == 2]

        return {
            'sad_comments': sad_comments,
            'joy_comments': joy_comments,
            'anger_comments': anger_comments,
        }
    
    
def main():
    st.title("CommentCraftr")
    st.write("Enter a social media link to extract comments and perform sentiment analysis.")

    # Text input for video URL with a unique key
    video_url = st.text_input("YouTube Video URL", key="video_url")

    # Sidebar for filter options
    st.sidebar.header("Filter Options")
    remove_spam = st.sidebar.checkbox("Filter Spam Comments", value=True, key="remove_spam")

    st.sidebar.subheader("Filter comments based on emotion:")
    filter_sad = st.sidebar.checkbox("Sad", key="filter_sad")
    filter_joy = st.sidebar.checkbox("Joy", key="filter_joy")
    filter_anger = st.sidebar.checkbox("Anger", key="filter_anger")

    st.sidebar.subheader("Filter comments based on sentiment:")
    filter_positive = st.sidebar.checkbox("Positive", key="filter_positive")
    filter_negative = st.sidebar.checkbox("Negative", key="filter_negative")

    # Sentiment analysis bars at the top
    if st.button("Submit", key="submit_button"):
        if video_url:
            ycom = Ycom()
            ycom.make_youtube()

            with st.spinner("Extracting comments..."):
                comments = ycom.display_comments(video_url)

            if isinstance(comments, dict) and 'error' in comments:
                st.error(comments['error'])
            else:
                st.write(f"Extracted comments from: **{ycom.video_title}**")

                # Perform spam detection
                if remove_spam:
                    with st.spinner("Detecting and removing spam..."):
                        spam_result = ycom.perform_spam_detection(comments)
                        spam_percentage = spam_result['spam_percentage']
                        filtered_comments = spam_result['filtered_comments']

                    if spam_percentage > 0:
                        st.success(f"Spam Filter: {spam_percentage:.2f}% of comments were identified as spam and removed.")
                        comments = filtered_comments
                    else:
                        st.success("No spam comments were detected.")

                # Perform emotion-based filtering
                if filter_sad or filter_joy or filter_anger:
                    with st.spinner("Filtering comments based on emotion..."):
                        emotion_result = ycom.perform_emotion_detection(comments)

                    if filter_sad:
                        st.success("Displaying Sad comments:")
                        for comment in emotion_result['sad_comments']:
                            st.write(f"- {comment['author']}: {comment['text']} (Likes: {comment['like_count']})")

                    if filter_joy:
                        st.success("Displaying Joy comments:")
                        for comment in emotion_result['joy_comments']:
                            st.write(f"- {comment['author']}: {comment['text']} (Likes: {comment['like_count']})")

                    if filter_anger:
                        st.success("Displaying Anger comments:")
                        for comment in emotion_result['anger_comments']:
                            st.write(f"- {comment['author']}: {comment['text']} (Likes: {comment['like_count']})")

                # Perform sentiment analysis
                with st.spinner("Performing sentiment analysis..."):
                    sentiment_result = ycom.perform_sentiment_analysis(comments)

                # Display sentiment analysis results at the top
                st.write("### Sentiment Analysis Overview")

                # Convert positive and negative percentages to floats after removing the '%' sign
                positive_percentage = float(sentiment_result['positive'].strip('%'))
                negative_percentage = float(sentiment_result['negative'].strip('%'))

                # Display positive and negative progress bars
                st.progress(positive_percentage / 100)  # Progress bar takes a float between 0 and 1
                st.progress(negative_percentage / 100)

                st.write(f"**Positive Comments:** {positive_percentage}%")
                st.write(f"**Negative Comments:** {negative_percentage}%")


                # Display filtered sentiment comments based on selection
                if filter_positive or filter_negative:
                    st.write("### Filtered Sentiment Comments")
                    if filter_positive:
                        st.success("Displaying Positive comments:")
                        for comment in sentiment_result['comments_with_sentiment']:
                            if comment['sentiment'] == 'positive':
                                st.write(f"- {comment['author']}: {comment['text']} (Likes: {comment['like_count']})")

                    if filter_negative:
                        st.error("Displaying Negative comments:")
                        for comment in sentiment_result['comments_with_sentiment']:
                            if comment['sentiment'] == 'negative':
                                st.write(f"- {comment['author']}: {comment['text']} (Likes: {comment['like_count']})")
        else:
            st.error("Please enter a valid YouTube video URL.")



if __name__ == "__main__":
    main()
