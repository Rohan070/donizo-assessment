import streamlit as st
import subprocess
import json
import os

st.set_page_config(page_title="Donizo Smart Bathroom Pricing Engine", layout="centered")
st.title("Donizo Smart Bathroom Pricing Engine")
st.markdown(
    """
Enter your bathroom renovation transcript below. Optionally, specify a city. Click **Generate Quote** to get a detailed, data-driven price breakdown. You can also provide feedback to help us improve!
"""
)

transcript = st.text_area(
    "Transcript",
    height=150,
    placeholder="E.g. Remove old tiles and install new ones. Bathroom is 5 sqm. City: Paris.",
)
city = st.text_input("City (optional)")

if "latest_file" not in st.session_state:
    st.session_state.latest_file = None

if st.button("Generate Quote") and transcript.strip():
    with st.spinner("Generating quote..."):
        cmd = [
            "python3",
            "pricing_engine.py",
            "--transcript",
            transcript,
        ]
        if city.strip():
            cmd += ["--city", city.strip()]
        subprocess.run(cmd, check=True)
        # Find the latest output file
        output_dir = "output"
        files = [
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.endswith(".json")
        ]
        if not files:
            st.error("No output file found.")
        else:
            latest_file = max(files, key=os.path.getctime)
            st.session_state.latest_file = latest_file
            with open(latest_file) as f:
                quote = json.load(f)
            st.success("Quote generated!")
            st.subheader("Quote Output")
            st.json(quote)

# Only show feedback if a quote was generated
if st.session_state.latest_file:
    st.markdown("---")
    st.subheader("Feedback")
    feedback = st.radio(
        "Was this quote accurate?", ("👍 Yes", "👎 No"), key="feedback_radio"
    )
    notes = st.text_area("Additional feedback (optional)", key="feedback_notes")
    if st.button("Submit Feedback"):
        # Extract quote ID from filename
        quote_file = os.path.basename(st.session_state.latest_file)
        quote_id = quote_file.replace(".json", "")
        feedback_entry = {"negative": feedback == "👎 No", "notes": notes}
        feedback_path = "data/feedback.json"
        # Load or create feedback.json
        if os.path.exists(feedback_path):
            with open(feedback_path, "r") as f:
                all_feedback = json.load(f)
        else:
            all_feedback = {}
        # Update feedback
        all_feedback[quote_id] = feedback_entry
        with open(feedback_path, "w") as f:
            json.dump(all_feedback, f, indent=2)
        st.session_state.feedback_submitted = True
        st.experimental_rerun()
    # Show thank you message if feedback was just submitted
    if st.session_state.get("feedback_submitted", False):
        st.success("Thank you for your feedback!")
        del st.session_state["feedback_submitted"]
