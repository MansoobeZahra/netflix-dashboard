# 🎬 Netflix Data Dashboard

An interactive and intelligent **data visualization and exploration app** built with **Streamlit**, based on the Netflix dataset.  
This dashboard helps users **analyze, filter, and visualize** Netflix content across genres, countries, ratings, and time — all with dynamic visualizations, sentiment analysis, and machine learning predictions.

---

## 🌟 Features

### 🔍 Search & Filter
- Filter by **Type** (Movie / TV Show)
- Filter by **Country**, **Rating**, and **Genre**
- Full-text search across **title**, **cast**, and **director**

### 📊 Data Visualizations
- 📅 Titles added to Netflix over time (by year)
- 🔞 Distribution of content ratings
- 🍿 Most common genres
- ⏱️ Average durations (Movies: minutes, TV Shows: seasons)
- 🌍 Top countries with Netflix content (Choropleth world map)

### 💬 Sentiment Analysis
- Analyzes content **descriptions** using `TextBlob`
- Visualizes sentiment polarity from -1 (negative) to +1 (positive)
 
### 📥 Data Export
- Download the **filtered dataset** as CSV

---

## 📁 Project Structure
├── app.py # Streamlit main app
├── netflix_titles.csv # Dataset file
├── requirements.txt # Python dependencies
├── .gitignore # Ignored files
└── README.md # You're reading it!


---

## 🚀 Getting Started Locally

### 🧰 Prerequisites

- Python 3.8+
- pip

### 🔧 Installation

```bash
# 1. Clone the repo
git clone https://github.com/mansoobezahra/netflix-dashboard.git
cd netflix-dashboard

# 2. Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate     # On Windows
source venv/bin/activate # On Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py

