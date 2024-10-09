import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
from wordcloud import WordCloud
import emoji
from urlextract import URLExtract

extractor = URLExtract()


def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    # 1.Fetch number of messages
    num_messages = df.shape[0]
    # 2. fetch number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # 3.fetch number of media shared
    num_media_messages = df[df['message'] == '<Media omitted>'].shape[0]

    # 4.fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))
    return num_messages,len(words),num_media_messages, len(links)


# Most busy users
def most_busy_users(df):
    new_df = df[df['user'] != 'group_notification']
    x = new_df['user'].value_counts().head()

    new_df = round(new_df['user'].value_counts() / new_df.shape[0] * 100, 2).reset_index().rename(
        columns={'user': 'name', 'count': 'percent'})
    return x, new_df


def create_wc(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    new_df = df[df['user'] != 'group_notification']
    new_df = new_df[new_df['message'] != '<Media omitted>']
    if selected_user != 'Overall':
        new_df = new_df[new_df['user'] == selected_user]

    def remove_stopwords(message):
        l = []
        for word in message.lower().split():
            if word not in stop_words:
                l.append(word)
        return ' '.join(l)
    wc = WordCloud(width=800, height=400,background_color='white')
    new_df['message'] = new_df['message'].apply(remove_stopwords)
    df_wc = wc.generate(new_df['message'].str.cat(sep=' '))
    return df_wc


# To get the most common words
def most_common_words(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    new_df = df[df['user'] != 'group_notification']
    new_df = new_df[new_df['message'] != '<Media omitted>']

    words = []
    for message in new_df['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    # Counter(words).most_common(20)
    common_words_df = pd.DataFrame(Counter(words).most_common(20)).rename(columns={0: 'word', 1: 'appeared'})
    return common_words_df


def emoji_counts(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    new_df = df[df['user'] != 'group_notification']
    new_df = new_df[new_df['message'] != '<Media omitted>']

    emojis = []
    for message in new_df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df


def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline


def daily_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby('date_only').count()['message'].reset_index()
    return timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    plt.figure(figsize=(16, 6))
    hm = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return hm
