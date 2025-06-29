import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  
from sklearn.model_selection import train_test_split
import requests 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import plotly.express as px
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multiclass import OneVsRestClassifier

st.set_page_config(page_title="Netflix Data Dashboard", layout="wide")

# -------------------------
# 🧹 Load and Clean Data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('netflix_titles.csv')

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert date_added to datetime
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['date_added'].fillna(df['date_added'].mode()[0], inplace=True)

    # Fill NA
    df['rating'].fillna('Not Rated', inplace=True)
    df['country'].fillna('Unknown', inplace=True)
    df['cast'].fillna('Not Available', inplace=True)
    df['director'].fillna('Not Available', inplace=True)
    df['description'].fillna('Not Available', inplace=True)

    # Drop missing critical rows
    df.dropna(subset=['title', 'type'], inplace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Extract numeric duration and unit
    df['duration_int'] = df['duration'].str.extract('(\d+)').astype(float)
    df['duration_type'] = df['duration'].str.extract('([a-zA-Z]+)').fillna('Unknown')

    # Explode genres for analysis
    df['genres'] = df['listed_in'].str.split(', ')
    return df

df = load_data()

# -------------------------
# 🎛 Sidebar Filters
# -------------------------
st.sidebar.header("🔍 Filter Netflix Data")

selected_type = st.sidebar.multiselect("Select Type", df['type'].unique(), default=df['type'].unique())
selected_country = st.sidebar.multiselect("Select Country", sorted(df['country'].unique()), default=['United States', 'India', 'Unknown'])
selected_rating = st.sidebar.multiselect("Select Rating", df['rating'].unique(), default=df['rating'].unique())

# Genre filtering
all_genres = sorted(set(g for sublist in df['genres'] for g in sublist))
selected_genres = st.sidebar.multiselect("Select Genre", all_genres)

# Apply filters
filtered_df = df[
    (df['type'].isin(selected_type)) &
    (df['country'].isin(selected_country)) &
    (df['rating'].isin(selected_rating))
]

if selected_genres:
    filtered_df = filtered_df[filtered_df['genres'].apply(lambda x: any(g in x for g in selected_genres))]

# -------------------------
# 📄 Data Overview
# -------------------------
st.title("🎬 Netflix Data Explorer (Cleaned & Interactive)")
st.markdown(f"Showing **{len(filtered_df)}** titles based on selected filters.")

st.dataframe(filtered_df[['title', 'type', 'country', 'release_year', 'rating', 'duration', 'listed_in']])

# -------------------------
# 📊 Visualizations
# -------------------------

col1, col2 = st.columns(2)

# 1. Content over years
with col1:
    st.subheader("📅 Titles Added to Netflix Over Time")
    year_counts = df['date_added'].dt.year.value_counts().sort_index()
    fig1, ax1 = plt.subplots()
    sns.barplot(x=year_counts.index, y=year_counts.values, ax=ax1, palette='coolwarm')
    ax1.set_xlabel("Year Added")
    ax1.set_ylabel("Number of Titles")
    st.pyplot(fig1)

# 2. Ratings distribution
with col2:
    st.subheader("🔞 Distribution of Content Ratings")
    rating_counts = df['rating'].value_counts().head(10)
    fig2, ax2 = plt.subplots()
    sns.barplot(x=rating_counts.values, y=rating_counts.index, ax=ax2, palette='mako')
    ax2.set_xlabel("Count")
    ax2.set_ylabel("Rating")
    st.pyplot(fig2)

# 3. Top genres
st.subheader("🍿 Top 10 Genres")
genre_counts = df['genres'].explode().value_counts().head(10)
fig3, ax3 = plt.subplots()
sns.barplot(x=genre_counts.values, y=genre_counts.index, ax=ax3, palette='viridis')
ax3.set_xlabel("Count")
ax3.set_ylabel("Genre")
st.pyplot(fig3)
 
# # Only calculate average movie durations in minutes
# movie_durations = df[df['duration_type'].str.contains('min', case=False)]
# tv_durations = df[df['duration_type'].str.contains('season', case=False)]

# avg_movie_duration = movie_durations['duration_int'].mean()
# avg_tv_seasons = tv_durations['duration_int'].mean()

# st.subheader("⏱️ Average Duration Separately")

# fig_dur, ax_dur = plt.subplots()
# ax_dur.bar(['Movies (minutes)', 'TV Shows (seasons)'], [avg_movie_duration, avg_tv_seasons], color=['#5DADE2', '#58D68D'])
# ax_dur.set_ylabel("Average (min / seasons)")
# st.pyplot(fig_dur)


# 5. Country analysis
st.subheader("🌍 Top Countries by Number of Titles")
country_counts = df['country'].value_counts().head(10)
fig5, ax5 = plt.subplots()
sns.barplot(y=country_counts.index, x=country_counts.values, ax=ax5, palette='flare')
ax5.set_xlabel("Number of Titles")
st.pyplot(fig5)


st.subheader("💬 Sentiment Analysis on Descriptions")

def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

# Calculate sentiment scores
filtered_df['sentiment_score'] = filtered_df['description'].apply(lambda x: get_sentiment(str(x)))

# Plot distribution
fig_sent, ax_sent = plt.subplots()
sns.histplot(filtered_df['sentiment_score'], bins=20, kde=True, ax=ax_sent, color='orange')
ax_sent.set_title("Sentiment Polarity Distribution")
ax_sent.set_xlabel("Sentiment Score (-1 = Negative, +1 = Positive)")
st.pyplot(fig_sent)

st.subheader("🌍 Top Countries on Netflix (Choropleth Map)")

country_df = df['country'].dropna().str.split(', ', expand=True).stack().reset_index(drop=True)
country_counts = country_df.value_counts().reset_index()
country_counts.columns = ['country', 'count']

fig_map = px.choropleth(
    country_counts,
    locations='country',
    locationmode='country names',
    color='count',
    hover_name='country',
    color_continuous_scale='reds',
    title='Number of Netflix Titles by Country'
)
fig_map.update_geos(projection_type="natural earth")

st.plotly_chart(fig_map, use_container_width=True)

st.subheader("🔍 Search Title, Director, or Cast")
search_query = st.text_input("Enter keyword(s) to search:")

if search_query.strip():
    results = filtered_df[
        filtered_df['title'].str.contains(search_query, case=False, na=False) |
        filtered_df['director'].str.contains(search_query, case=False, na=False) |
        filtered_df['cast'].str.contains(search_query, case=False, na=False)
    ]
    if not results.empty:
        st.write(f"✅ Found {len(results)} matching titles:")
        st.dataframe(results[['title', 'director', 'cast', 'release_year', 'rating']])
    else:
        st.warning("😕 No matching results found.")

st.subheader("📥 Download Filtered Dataset")

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_netflix_data.csv',
    mime='text/csv',
)


 
 
