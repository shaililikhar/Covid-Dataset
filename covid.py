import pandas as pd
from collections import defaultdict

df = pd.read_csv('covidTrain.csv')
df['symptoms'] = df['symptoms'].astype(str)

#task 1 
def calculate_average_age(age):
    if '-' in age:  
        start, end = map(int, age.split('-'))
        return round((start + end) / 2) 
    else:
        try:
            return int(age) 
        except ValueError:
            return float('nan')

df['age'] = df['age'].apply(calculate_average_age)
df['age'] = df['age'].fillna(df['age'].mean())
df['age'] = df['age'].astype(int)

#task 2 
df['date_onset_symptoms'] = pd.to_datetime(df['date_onset_symptoms'], format='%d.%m.%Y').dt.strftime('%m.%d.%Y')
df['date_admission_hospital'] = pd.to_datetime(df['date_admission_hospital'], format='%d.%m.%Y').dt.strftime('%m.%d.%Y')
df['date_confirmation'] = pd.to_datetime(df['date_confirmation'], format='%d.%m.%Y').dt.strftime('%m.%d.%Y')

#task 3 
province_avg_latitude = df.groupby('province')['latitude'].mean()
province_avg_longitude = df.groupby('province')['longitude'].mean()
df['latitude'] = df.apply(lambda row: round(province_avg_latitude[row['province']], 5) if pd.isnull(row['latitude']) else row['latitude'], axis=1)
df['longitude'] = df.apply(lambda row: round(province_avg_longitude[row['province']], 5) if pd.isnull(row['longitude']) else row['longitude'], axis=1)

print(df[['latitude', 'longitude']])

#task 4 
df['city'] = df.groupby('province')['city'].transform(lambda x: x.fillna(x.mode().sort_values().iloc[0]))

# Task 5
df['symptoms'] = df['symptoms'].str.split(r'; ?')
symptom_counts = df.explode('symptoms').groupby(['province', 'symptoms']).size().reset_index(name='count')

def fill_missing_symptoms(row):
    province = row['province']
    symptoms = row['symptoms']
    if isinstance(symptoms, list):
        most_frequent = symptom_counts[symptom_counts['province'] == province].sort_values(['count', 'symptoms'], ascending=[False, True])['symptoms'].iloc[0]
        return most_frequent
    else:
        return symptoms

df['symptoms'] = df.apply(fill_missing_symptoms, axis=1)
df['symptoms'] = df['symptoms'].apply(lambda x: '; '.join(sorted(x)) if isinstance(x, list) else x)
df['symptoms'] = df['symptoms'].fillna('Unknown')
df.to_csv('covidResult.csv', index=False)