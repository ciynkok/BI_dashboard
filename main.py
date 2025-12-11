import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Заголовок ----

st.set_page_config(page_title="BI Дашборд Отзывов", layout="wide")
st.title("📊 BI-Дашборд: Аналитика отзывов")
# ---- Загрузка данных ----
@st.cache_data

def load_data():
    return pd.read_excel("prodoctorov_ru - гастроэнтерологи - 2025_12_08.xlsx", engine="openpyxl")

df = load_data()
df['Отзыв'] = df['Отзыв'].str.replace('_x000D_', ' ')
#print(pd.read_csv("prodoctorov_ru.csv", sep=';').loc[:2]["Отзыв"])


# ---- Боковая панель ----
st.sidebar.header("Фильтры")

doctors = st.sidebar.multiselect(
    "Выберите врача:",
    options=df["Имя врача"].unique(),
    default=df["Имя врача"].unique()
)

search_keyword = st.sidebar.text_input("Поиск по отзывам (ключевое слово):")

# Фильтрация данных
filtered = df[df["Имя врача"].isin(doctors)]

if search_keyword:
    filtered = filtered[filtered["Отзыв"].str.contains(search_keyword, case=False, na=False)]

# ---- Метрики ----
col1, col2, col3 = st.columns(3)
col1.metric("Всего отзывов", len(filtered))
col2.metric("Уникальных врачей", filtered["Имя врача"].nunique())
col3.metric("Средний рейтинг", round(filtered["Рейтинг_1"].mean(), 2))

# ---- Таблица отзывов ----
st.subheader("Отзывы")
st.dataframe(filtered.sort_values("Дата отзыва", ascending=False))
