import streamlit as st
import datetime
import os
import json

# Storage file for diary entries
STORAGE_FILE = "diary_entries.json"

# Load existing diary entries
def load_entries():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as file:
            try:
                entries = json.load(file)
                if isinstance(entries, list):
                    for entry in entries:
                        # Ensure each entry has the necessary fields
                        entry.setdefault("title", "Untitled")  # Default title
                        entry.setdefault("tags", [])
                        entry.setdefault("username", "Unknown User")  # Default value
                        entry.setdefault("image", None)  # Default value
                    return entries
                else:
                    return []
            except json.JSONDecodeError:
                return []
    return []

# Save diary entries
def save_entries(entries):
    with open(STORAGE_FILE, "w") as file:
        json.dump(entries, file, indent=4)

# Load diary entries
entries = load_entries()

# ---------------------------- UI Setup ----------------------------
st.set_page_config(page_title="📖 My Daily Diary", layout="wide")

# Sidebar (History)
st.sidebar.title("📜 History")  # Fixed wording

# ---------------------------- Mood Selection ----------------------------
st.title("📖 My Daily Diary")
selected_date = st.date_input("📅 Select Date", datetime.date.today())
formatted_date = selected_date.strftime("%Y-%m-%d (%A)")

st.subheader("😊 How are you feeling today?")
mood_options = {
    "😀 Happy": ("Happy", "#9b59b6"),  # Light purple for Happy
    "😢 Sad": ("Sad", "#3498DB"),
    "😠 Angry": ("Angry", "#E74C3C"),
    "😴 Tired": ("Tired", "#f4b400"),
    "😎 Excited": ("Excited", "#F1C40F")
}

selected_mood = st.radio("", list(mood_options.keys()))
mood_text, mood_color = mood_options[selected_mood]

# ---------------------------- Mood Display ----------------------------
st.markdown(f"""
    <div style="background:{mood_color}; padding: 12px; border-radius: 12px; color: white; text-align:center;">
        😊 Mood: {mood_text}
    </div>
""", unsafe_allow_html=True)

# ---------------------------- Title Input ----------------------------
st.subheader("📜 Title of Your Entry")
title = st.text_input("Give a title to your entry", "")

# ---------------------------- User Information ----------------------------
st.subheader("👤 Your Name (Optional)")
username = st.text_input("Enter your name (Optional)", "")

# ---------------------------- Upload Image ----------------------------
st.subheader("🖼 Upload an Image")
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

# ---------------------------- Diary Entry ----------------------------
st.subheader("📝 Write your daily thoughts")
diary_text = st.text_area("Start writing here...", height=150)

# ---------------------------- Add Tags ----------------------------
st.subheader("🏷 Add Tags")
tags_input = st.text_input("Separate multiple tags with commas (e.g., Travel, Work, Health)")
tags_list = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

# ---------------------------- Save Entry Button ----------------------------
button_style = f"""
    <style>
    div.stButton > button {{
        background-color: {mood_color} !important;
        color: white !important;
        font-size: 16px;
        padding: 10px;
        border-radius: 10px;
        border: none;
        cursor: pointer;
    }}
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

if st.button("💾 Save Entry"):
    image_path = None
    if uploaded_image:
        image_path = f"uploaded_images/{uploaded_image.name}"
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())

    entry = {
        "title": title or "Untitled",  # Default to "Untitled" if no title
        "date": formatted_date,
        "mood": mood_text,
        "text": diary_text,
        "tags": tags_list,
        "username": username or "Unknown User",  # Default to "Unknown User" if no name
        "image": image_path
    }
    entries.append(entry)
    save_entries(entries)
    st.success("✅ Diary entry saved successfully! 🎉")

# ---------------------------- Sidebar Enhancements ----------------------------
sidebar_bg_color = f"""
    <style>
    [data-testid="stSidebar"] {{
        background-color: {mood_color} !important;
        padding: 20px;
        border-radius: 10px;
        color: #fff;
    }}
    [data-testid="stSidebar"] * {{
        color: #001F3F !important;
        font-weight: bold;
    }}
    .entry-button {{
        background-color: #fff !important;
        color: {mood_color} !important;
        padding: 8px;
        border-radius: 10px;
        margin: 5px 0;
        font-size: 14px;
        cursor: pointer;
        text-align: left;
        width: 100%;
    }}
    .entry-button:hover {{
        background-color: {mood_color};
        color: white;
    }}
    </style>
"""
st.sidebar.markdown(sidebar_bg_color, unsafe_allow_html=True)

# ---------------------------- Search and Date Filter ----------------------------
# Search Input for Title or Tags
search_query = st.sidebar.text_input("🔍 Search by Title or Tags", key="search_query")
if search_query:
    st.sidebar.button("❌ Clear Search", on_click=lambda: st.session_state.update({"search_query": ""}))

# Date Filter (Allow users to filter by date range)
date_range = st.sidebar.date_input("📅 Select Date Range", value=(datetime.date.today(), datetime.date.today()), key="date_range")
start_date, end_date = date_range

# Filter entries based on search query and date range
filtered_entries = [
    entry for entry in entries
    if (search_query.lower() in entry.get("title", "").lower() or any(search_query.lower() in tag.lower() for tag in entry.get("tags", [])))
    and start_date <= datetime.datetime.strptime(entry['date'], "%Y-%m-%d (%A)").date() <= end_date
]

# ---------------------------- Display Entries with Preview ----------------------------
st.sidebar.subheader("📜 Previous Entries")

# Initialize selected_entry as None
selected_entry = None

# Display each filtered entry with a brief preview
for idx, entry in enumerate(reversed(filtered_entries)):  # Show newest first
    # Mood icon and color code
    mood_icon = {
        "Happy": "😀",
        "Sad": "😢",
        "Angry": "😠",
        "Tired": "😴",
        "Excited": "😎"
    }.get(entry["mood"], "😊")

    # Entry Preview Button with Mood Icon
    entry_preview = st.sidebar.button(
        f"{mood_icon} {entry['title'][:30]}...", 
        key=f"{entry['date']}-{idx}", 
        help=f"Date: {entry['date']}\nMood: {entry['mood']}\n{entry['text'][:60]}..."
    )

    if entry_preview:
        selected_entry = entry

# ---------------------------- Display Selected Entry ----------------------------
if selected_entry:
    st.subheader(f"📅 Date: {selected_entry['date']}")
    st.markdown(f"**Mood:** {selected_entry['mood']}")
    st.markdown(f"**Diary Entry:** {selected_entry['text']}")
    if selected_entry['tags']:
        st.markdown(f"🏷 **Tags:** {', '.join(selected_entry['tags'])}")
    if selected_entry['image']:
        st.image(selected_entry['image'], use_column_width=True)
else:
    st.info("No diary entry selected. Click on a title in the sidebar to view an entry.")

# ---------------------------- Footer ----------------------------
st.markdown("""
    <div style="text-align: center; padding: 20px; font-size: 20px; color: #555;">
        <p>All rights reserved to Tabsheera Shakeel</p>
    </div>
""", unsafe_allow_html=True)
