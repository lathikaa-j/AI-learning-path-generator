import streamlit as st

from utils import (
    generate_learning_path,
    get_youtube_videos,
    send_to_notion
)

st.set_page_config(
    page_title="AI Learning Path Generator",
    layout="wide"
)

st.title("🚀 AI Learning Path Generator")

st.write(
    "Generate a structured step-by-step learning roadmap with projects and videos."
)

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "roadmap_data" not in st.session_state:
    st.session_state.roadmap_data = None

if "goal" not in st.session_state:
    st.session_state.goal = ""

# -----------------------------------
# USER INPUT
# -----------------------------------
goal = st.text_input(
    "📚 What do you want to learn?",
    placeholder="Example: Python in 10 days"
)

# -----------------------------------
# GENERATE BUTTON
# -----------------------------------
if st.button("Generate Learning Path"):

    if not goal.strip():
        st.warning("⚠️ Please enter a learning topic")
        st.stop()

    with st.spinner("Generating roadmap..."):

        data = generate_learning_path(goal)

    st.session_state.roadmap_data = data
    st.session_state.goal = goal

# -----------------------------------
# DISPLAY ROADMAP
# -----------------------------------
if st.session_state.roadmap_data:

    data = st.session_state.roadmap_data
    goal = st.session_state.goal

    if "error" in data:
        st.error(data["error"])
        st.stop()

    st.subheader("📘 Learning Roadmap")

    st.write(data.get("roadmap", ""))

    st.divider()

    days = data.get("days", [])

    full_notes = f"Learning Goal: {goal}\n\n"
    full_notes += data.get("roadmap", "") + "\n\n"

    if not days:
        st.warning("⚠️ No roadmap generated")
        st.stop()

    # -----------------------------------
    # DAY LOOP
    # -----------------------------------
    for d in days:

        day = d.get("day", "")
        topic = d.get("topic", "")

        st.markdown(f"## 📅 Day {day}: {topic}")

        focus = d.get("focus", "")

        if focus:
            st.info(f"📌 {focus}")

        full_notes += f"\nDay {day}: {topic}\n"

        # -------------------------------
        # STEPS
        # -------------------------------
        st.write("### 🪜 Step-by-step Guide:")

        steps = d.get("steps", [])

        if steps:

            for step in steps:

                st.write(f"- {step}")

                full_notes += f"- {step}\n"

        # -------------------------------
        # PRACTICE
        # -------------------------------
        practice = d.get("practice", "")

        if practice:

            st.write(f"🧪 **Practice Task:** {practice}")

            full_notes += f"\nPractice: {practice}\n"

        # -------------------------------
        # PROJECT
        # -------------------------------
        project = d.get("project", "")

        if project:

            st.write(f"🚀 **Mini Project:** {project}")

            full_notes += f"Project: {project}\n"

        # -------------------------------
        # YOUTUBE VIDEOS
        # -------------------------------
        youtube_query = d.get("youtube_query", "")

        st.write("### 🎥 Recommended Videos")

        try:

            videos = get_youtube_videos(youtube_query)

            items = videos.get("videos", [])

            if not items:

                st.warning("⚠️ No videos found")

            else:

                for item in items:

                    st.markdown(
                        f"🎬 [{item['title']}]({item['url']})"
                    )

        except Exception as e:

            st.error(f"YouTube Error: {str(e)}")

        st.divider()

    # -----------------------------------
    # SAVE TO NOTION
    # -----------------------------------
    st.subheader("💾 Save Notes")

    if st.button("Save to Notion"):

        with st.spinner("Saving to Notion..."):

            result = send_to_notion(
                goal,
                full_notes
            )

        if isinstance(result, dict) and "error" in result:

            st.error(f"❌ {result['error']}")

        else:

            st.success("✅ Successfully saved to Notion")