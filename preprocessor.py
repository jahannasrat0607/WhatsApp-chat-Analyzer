import re
import pandas as pd


def preprocess(data):
    pattern = r"\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}\s?[apm]{2} - "
    # Splitting messages by the pattern
    messages = re.split(pattern, data)[1:]
    # Finding the corresponding dates
    dates = re.findall(pattern, data)
    # Creating a DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # Cleaning the 'message_date' column
    df['message_date'] = df['message_date'].str.replace('\u202f', ' ')
    df['message_date'] = df['message_date'].str.replace(' - ', '')
    # Convert to datetime, handling am/pm
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %I:%M %p')
    df.rename(columns={'message_date': 'date'}, inplace=True)
    # Separate users and messages
    users = []
    messages = []

    for message in df['user_message']:
        # Used regex to identify user and message, where user is either a phone number or a name
        entry = re.split(r'(^[^:]+):\s', message.strip())  # Split at the first colon

        if len(entry) > 2:  # Valid user and message pair
            user = entry[1].strip()
            if re.match(r"^\+?\d{10,}$", user):  # If it's a phone number
                users.append(user)
            else:
                users.append(user)  # Append saved contact name
            messages.append(entry[2].strip())  # Append the actual message
        else:
            users.append('group_notification')  # For group notifications or system messages
            messages.append(entry[0].strip())  # Append the message content

    df['user'] = users
    df['message'] = messages

    # Drop the original 'user_message' column as it's no longer needed
    df.drop(columns=['user_message'], inplace=True)
    # df.head()
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['month_num'] = df['date'].dt.month
    df['date_only'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()

    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + '-' + str('00'))
        elif hour == 0:
            period.append(str(0) + '-' + str(hour + 1))
        else:
            period.append(str(hour) + '-' + str(hour + 1))
    df['period'] = period
    return df
