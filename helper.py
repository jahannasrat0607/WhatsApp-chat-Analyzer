from collections import Counter
import pandas as pd
from wordcloud import WordCloud
import emoji
from urlextract import URLExtract

extractor = URLExtract()


def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Check if df is empty
    if df.empty:
        return 0, 0, 0, 0

    # 1. Fetch number of messages
    num_messages = df.shape[0]

    # 2. Fetch number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # 3. Fetch number of media shared
    num_media_messages = df[df['message'] == '<Media omitted>'].shape[0]

    # 4. Fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    new_df = df[df['user'] != 'group_notification']

    if new_df.empty:
        return pd.Series(), pd.DataFrame()

    x = new_df['user'].value_counts().head()
    new_df = round(new_df['user'].value_counts() / new_df.shape[0] * 100, 2).reset_index().rename(
        columns={'user': 'name', 'count': 'percent'})

    return x, new_df


def create_wc(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    # Filter out group notifications and media omitted messages
    new_df = df[df['user'] != 'group_notification']
    new_df = new_df[new_df['message'] != '<Media omitted>']

    if selected_user != 'Overall':
        new_df = new_df[new_df['user'] == selected_user]

    # If the filtered DataFrame is empty, return None (don't plot the WordCloud)
    if new_df.empty:
        return None

    def remove_stopwords(message):
        return ' '.join([word for word in str(message).lower().split() if word not in stop_words])

    # Apply the stopwords removal and filter out empty messages
    new_df['message'] = new_df['message'].apply(remove_stopwords)
    new_df = new_df[new_df['message'] != '']  # Remove any empty strings after processing
    # Check if there are still valid messages after filtering
    if new_df.empty:
        return None  # If no valid messages are left, return None
    # Combine all messages into one string for WordCloud
    combined_message = ' '.join(new_df['message'].values)

    # Check if the combined string is empty
    if len(combined_message.strip()) == 0:
        return None  # Return None if no valid words are left

    # Generate the WordCloud
    wc = WordCloud(width=800, height=400, background_color='white').generate(combined_message)

    return wc

def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    new_df = df[df['user'] != 'group_notification']
    new_df = new_df[new_df['message'] != '<Media omitted>']

    if new_df.empty:
        return pd.DataFrame(columns=['word', 'appeared'])

    words = []
    for message in new_df['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    # Handle cases where no words are found
    if not words:
        print("No valid words found for most common words analysis.")
        return pd.DataFrame(columns=['word', 'appeared'])

    common_words_df = pd.DataFrame(Counter(words).most_common(20)).rename(columns={0: 'word', 1: 'appeared'})
    return common_words_df


def emoji_counts(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    new_df = df[df['user'] != 'group_notification']
    new_df = new_df[new_df['message'] != '<Media omitted>']

    if new_df.empty:
        return pd.DataFrame(columns=[0, 1])

    emojis = []
    for message in new_df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame(columns=['year', 'month_num', 'month', 'message', 'time'])

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = [timeline['month'][i] + '-' + str(timeline['year'][i]) for i in range(timeline.shape[0])]
    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame(columns=['date_only', 'message'])

    timeline = df.groupby('date_only').count()['message'].reset_index()
    return timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.Series()

    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.Series()

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame()

    hm = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return hm
