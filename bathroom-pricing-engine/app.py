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

generate = st.button("Generate Quote")

if generate and transcript.strip():
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
            with open(latest_file) as f:
                quote = json.load(f)
            st.success("Quote generated!")
            st.subheader("Quote Output")
            st.json(quote)
            st.markdown("---")
            st.subheader("Feedback")
            feedback = st.radio(
                "Was this quote accurate?", ("👍 Yes", "👎 No"), horizontal=True
            )
            notes = st.text_area("Additional feedback (optional)", key="feedback_notes")
            if st.button("Submit Feedback"):
                # Save feedback to a simple file (or call your feedback logic)
                feedback_entry = {
                    "quote_file": latest_file,
                    "feedback": feedback,
                    "notes": notes,
                }
                with open(os.path.join(output_dir, "ui_feedback.jsonl"), "a") as fb:
                    fb.write(json.dumps(feedback_entry) + "\n")
                st.success("Thank you for your feedback!")
