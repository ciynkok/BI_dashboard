import streamlit as st
import pandas as pd
import re

def highlight_keywords(text, keywords):
    if not keywords.strip():
        return text
    
    # Разбиваем строку на слова
    words = [w.strip() for w in keywords.split() if w.strip()]
    if not words:
        return text

    # Создаём регулярку: (слово1|слово2|слово3)
    pattern = re.compile(r"(" + "|".join(map(re.escape, words)) + r")", re.IGNORECASE)

    # Подсвечиваем
    return pattern.sub(r"<mark>\1</mark>", text)

# ---- Заголовок ----

st.set_page_config(page_title="BI Дашборд Отзывов", layout="wide")
st.title("📊 BI-Дашборд: Аналитика отзывов")
# ---- Загрузка данных ----
@st.cache_data
def load_data():
    doctors = pd.read_csv("doctors.csv")
    reviews = pd.read_csv("reviews.csv")
    return doctors, reviews

doctors, reviews = load_data()

st.sidebar.header("Фильтры врачей")

name_query = st.sidebar.text_input(
    "Имя:",
    value=""
)

specialities = st.sidebar.text_input(
    "Специальность:",
    value=""
)

degree = st.sidebar.multiselect(
    "Ученая степень:",
    options=doctors["Ученая степень"].unique(),
    default=doctors["Ученая степень"].unique()
)

work_places = st.sidebar.text_input(
    "Учереждение:",
    value=""
)

# Фильтр по минимальному стажу
min_exp = st.sidebar.number_input(
    "Минимальный стаж (лет):",
    min_value=0,
    max_value=int(doctors["Сумма Стаж"].max()),
    value=0,
    step=1
)

# Фильтр по минимальному рейтингу
min_rating = st.sidebar.number_input(
    "Минимальный рейтинг:",
    min_value=float(0),
    max_value=doctors["Сумма Рейтинг"].max(),
    value=float(0),
    step=doctors["Сумма Рейтинг"].max() / 10
)

search_text = st.text_input("Поиск по отзывам (введите ключевые слова):")

if search_text:
    filtered_reviews = reviews[reviews["Отзыв"].str.contains(search_text, case=False, na=False)]
else:
    filtered_reviews = reviews.copy()



filtered = doctors.copy()
# фильтр по имени врача (поиск подстроки)
if name_query.strip() != "":
    filtered = filtered[filtered["Имя врача"].str.contains(name_query, case=False, na=False)]

if specialities.strip() != "":
    filtered = filtered[filtered["Специальность"].str.contains(specialities, case=False, na=False)]

if work_places.strip() != "":
    filtered = filtered[filtered["Работает в клиниках"].str.contains(work_places, case=False, na=False)]


# ---------------- Применение фильтров ----------------
if len(filtered["Ученая степень"].isin(degree).unique()) != 1 or min_exp != 0 or min_rating != 0: #len(filtered["Ученая степень"].isin(degree).unique()) != 1
    filtered = filtered[
        (filtered["Ученая степень"].isin(degree)) &
        (filtered["Сумма Стаж"] >= min_exp) &
        (filtered["Сумма Рейтинг"] >= min_rating)
    ]


# ---------------- Кнопки "Показать отзывы" ----------------

output_placeholder = st.empty()

rows_per_page = st.sidebar.number_input(
    "Врачей на странице:",
    min_value=5,
    max_value=100,
    value=10,
    step=5
)

def gen_pagination(filt):
    total_rows = len(filt)
    total_pages = (total_rows - 1) // rows_per_page + 1

    if "page" not in st.session_state:
        st.session_state.page = 1

    # Кнопки навигации
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Назад") and st.session_state.page > 1:
            st.session_state.page -= 1

    with col3:
        if st.button("Вперёд ➡️") and st.session_state.page < total_pages:
            st.session_state.page += 1

    # Показ номера страницы
    with col2:
        st.markdown(f"### Страница {st.session_state.page} / {total_pages}")

    # Индексы текущей страницы
    start = (st.session_state.page - 1) * rows_per_page
    end = start + rows_per_page

    filtered_page = filt.iloc[start:end]

    return filtered_page

if search_text:

    st.subheader("📋 Список отзывов")

    filtered_reviews = reviews[reviews["Отзыв"].str.contains(search_text, case=False, na=False)]

    filtered = filtered_reviews.merge(filtered, on="Ссылка", how="left")
    filtered = filtered.sort_values(by=["Имя врача"])


    filtered["Имя врача"] = filtered.groupby("Ссылка")["Имя врача"] \
        .transform(lambda x: [x.iloc[0]] + [""] * (len(x)-1))

    # --- То же для специальности ---
    # Перед этим сохраняем специальность (у врача она одна)
    filtered["Специальность"] = filtered.groupby("Ссылка")["Специальность"] \
        .transform(lambda x: [x.iloc[0]] + [""] * (len(x)-1))

    filtered["Ссылка"] = filtered.groupby("Ссылка")["Ссылка"] \
        .transform(lambda x: [x.iloc[0]] + [""] * (len(x)-1))

    filtered_page = gen_pagination(filtered)


    header_cols = st.columns([2, 2, 2, 1, 6])

    with header_cols[0]:
        st.markdown("**Ссылка**")
    with header_cols[1]:
        st.markdown("**Имя врача**")
    #with header_cols[2]:
    #   st.markdown("**Стаж (лет)**")
    with header_cols[2]:
        st.markdown("**Специальность**")
    with header_cols[3]:
        st.markdown("**Оценка**")
    with header_cols[4]:
        st.markdown("**Отзывы**")
    #with header_cols[4]:
    #    st.markdown("**Клиники**")
    #with header_cols[5]:
    #    st.markdown("**Отзывов**")
    #with header_cols[6]:
    #    st.markdown("**Рейтинг**")


    for idx, row in filtered_page.iterrows():
        with st.container():
            st.markdown("""
            <div style="padding:10px; border-bottom:1px solid #ccc;">
            """, unsafe_allow_html=True)

            columns = st.columns([2, 2, 2, 1, 6])
            with columns[0]:
                st.write(row['Ссылка'])
            with columns[1]:
                if row["Имя врача"]:
                    st.write(f"**{row['Имя врача']}**")
                    with st.expander("Подробнее о враче"):
                        st.write(f"**Стаж:** {row.get('Сумма Стаж', '—')} лет")
                        st.write(f"**Ученая степень:** {row.get('Ученая степень', '—')}")
                        st.write(f"**Учереждения:** {row.get('Работает в клиниках', '—')}")
                        st.write(f"**Отзывов:** {row.get('Сумма Отзывов', '—')}")
                        st.write(f"**Рейтинг:** {row.get('Сумма Рейтинг', '—')}")
            with columns[2]:
                st.write(row["Специальность"])
            with columns[3]:
                st.write(row.get("Рейтинг_1", "—"))
            with columns[4]:
                if search_text.strip() == "":
                    st.write(row["Отзыв"])
                else:
                    highlighted = highlight_keywords(row["Отзыв"], search_text)
                    st.markdown(highlighted, unsafe_allow_html=True)
                with st.expander("Подробнее об отзыве"):
                    st.write(f"**Имя клиента:** {row.get('Имя клиента', '—')}")
                    st.write(f"**Дата отзыва:** {row.get('Дата отзыва', '—')}")
                    st.write(f"**Оценка:** {row.get('Рейтинг_1', '—')}")
                    st.write(f"**Подтверждение записи:** {row.get('Подтверждение записи', '—')}")

            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.subheader("📋 Список врачей")

    filtered_page = gen_pagination(filtered)

    st.divider()

    output_placeholder = st.empty()

    for idx, row in filtered_page.iterrows():
        columns = st.columns([3, 3, 2, 2, 4, 2, 2, 2])

        with columns[0]:
            st.write(row['Ссылка'])
        with columns[1]:
            st.write(f"**{row['Имя врача']}**")
        with columns[2]:
            st.write(f"**Стаж:** {row.get('Сумма Стаж', '—')} лет")
        with columns[3]:
            st.write(f"**Ученая степень:** {row.get('Ученая степень', '—')}")
        with columns[4]:
            st.write(f"**Учереждения:** {row.get('Работает в клиниках', '—')}")
        with columns[5]:
            st.write(f"**Отзывов:** {row.get('Сумма Отзывов', '—')}")
        with columns[6]:
            st.write(f"**Рейтинг:** {row.get('Сумма Рейтинг', '—')}")
        with columns[7]:
            if st.button("Отзывы", key=f"rev_{row['Ссылка']}"):
                dr_reviews = reviews[reviews["Ссылка"] == row["Ссылка"]][['Рейтинг_1', 'Отзыв']]
                
                with output_placeholder.container():
                    st.markdown(f"### 📝 Отзывы о враче: {row['Имя врача']}")

                    st.dataframe(
                        dr_reviews,
                        width='stretch',
                        column_config={
                            "Рейтинг": st.column_config.NumberColumn("Рейтнг_1", width="50px"),
                            "Отзыв": st.column_config.TextColumn("Отзыв"),
                        }
                    )

                    st.divider()

