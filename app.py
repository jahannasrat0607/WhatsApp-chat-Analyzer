import preprocessor, helper
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
# Layout configuration
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# File uploader
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    st.success("File uploaded successfully!")
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    #  to convert this file stream of byte to string
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,'Overall')

    selected_user = st.sidebar.selectbox('Show Analysis for ', user_list)

    if st.sidebar.button('Show Analysis'):
        # Fetch statistics
        if selected_user != 'Overall':
            df = df[df['user'] == selected_user]
            # Check if there are any messages for the selected user
        if df.empty:
            st.warning(f"No messages found for {selected_user}")

        else:
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

            # Top Statistics with smaller titles
            st.markdown("<h2 style='font-size:24px; color: #4CAF50;'>📊 Top Statistics</h2>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown("<h4 style='font-size:18px;'>Total Messages</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:20px;'>{num_messages}</p>", unsafe_allow_html=True)

            with col2:
                st.markdown("<h4 style='font-size:18px;'>Total Words</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:20px;'>{words}</p>", unsafe_allow_html=True)

            with col3:
                st.markdown("<h4 style='font-size:18px;'>Media Shared</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:20px;'>{num_media_messages}</p>", unsafe_allow_html=True)

            with col4:
                st.markdown("<h4 style='font-size:18px;'>Links Shared</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:20px;'>{num_links}</p>", unsafe_allow_html=True)

            # Monthly Timeline with smaller title
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h2 style='font-size:22px; color: #FFA500;'>📅 Monthly Timeline</h2>", unsafe_allow_html=True)
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots()
                plt.xticks(rotation='vertical')
                ax.plot(timeline['time'], timeline['message'], color='green')
                st.pyplot(fig)

            # Daily Timeline with smaller title
            with col2:
                st.markdown("<h2 style='font-size:22px; color: #FFA500;'>📅 Daily Timeline</h2>", unsafe_allow_html=True)
                timeline = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots()
                plt.xticks(rotation='vertical')
                ax.plot(timeline['date_only'], timeline['message'], color='violet')
                st.pyplot(fig)

            # Weekly Activity Map with smaller title
            st.markdown("<h2 style='font-size:24px; color: #FF4500;'>📅 Activity Map</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h3 style='font-size:20px; color: #FF6347;'>📅 Most Busy Day</h3>", unsafe_allow_html=True)
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                plt.xticks(rotation='vertical')
                ax.bar(busy_day.index, busy_day.values)
                st.pyplot(fig)
            with col2:
                st.markdown("<h3 style='font-size:20px; color: #FF6347;'>📅 Most Busy Month</h3>", unsafe_allow_html=True)
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                plt.xticks(rotation='vertical')
                ax.bar(busy_month.index, busy_month.values, color='orange')
                st.pyplot(fig)

            # Heatmap with smaller title
            st.markdown("<h2 style='font-size:24px; color: #FF6347;'>🗓️ Weekly Activity Heatmap</h2>", unsafe_allow_html=True)
            hm = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots(figsize=(10,4))
            ax = sns.heatmap(hm)
            st.pyplot(fig)

            # Most Busy Users with smaller title
            if selected_user == 'Overall':
                st.markdown("<h2 style='font-size:24px; color: #4CAF50;'>🔝 Most Busy Users</h2>", unsafe_allow_html=True)
                x, new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()
                col1, col2 = st.columns(2)
                with col1:
                    plt.xticks(rotation='vertical')
                    ax.bar(x.index, x.values, color='green')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

            # WordCloud
            st.markdown("<h2 style='font-size:24px; color: #008080;'>☁️ WordCloud</h2>", unsafe_allow_html=True)
            df_wc = helper.create_wc(selected_user, df)
            if df_wc:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(df_wc, interpolation='bilinear')
                ax.axis('off')  # Turn off the axes
                plt.title('WordCloud', fontsize=24)
                plt.xlabel('Words', fontsize=16)
                plt.ylabel('Frequency', fontsize=16)

                st.pyplot(fig)
            else:
                st.write("No valid messages available to generate a word cloud.")

            # Most Common Words
            st.markdown("<h2 style='font-size:24px; color: #808080;'>📝 Most Common Words</h2>", unsafe_allow_html=True)
            common_words_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            plt.xticks(rotation='vertical')
            ax.barh(common_words_df['word'], common_words_df['appeared'])
            st.pyplot(fig)

            # Emoji Analysis with smaller title
            st.markdown("<h2 style='font-size:24px; color: #FF69B4;'>😀 Emoji Analysis</h2>", unsafe_allow_html=True)
            emoji_df = helper.emoji_counts(selected_user, df)
            if not emoji_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(emoji_df)
                with col2:
                    fig, ax = plt.subplots()
                    ax.bar(emoji_df[0].head(10), emoji_df[1].head(10))
                    st.pyplot(fig)

            else:
                st.write("No emojis available for emoji analysis.")