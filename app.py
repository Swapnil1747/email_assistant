import streamlit as st
from main import (
    authenticate_google_services,
    fetch_and_store_emails,
    init_db,
    SessionLocal,
    Email,
    summarize_email,
    generate_reply,
    extract_question_from_email,
    extract_meeting_datetime,
    create_event,
    generate_event_title
)
from email_actions import send_email
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from dateutil.tz import gettz

st.set_page_config(page_title="AI Email Assistant", page_icon="📬", layout="wide")

# -------------------- Session State Defaults --------------------
default_settings = {
    "max_emails": 10,
    "auto_reply_enabled": True,
    "custom_greeting": "Thank you for your email.",
    "meeting_duration": 30,
    "timezone": "Asia/Kolkata",
    "slack_enabled": True,
    "ai_temperature": 0.7,
    "selected_email_ids": set()
}
for key, value in default_settings.items():
    st.session_state.setdefault(key, value)

# -------------------- Auth State --------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'gmail_service' not in st.session_state:
    st.session_state.gmail_service = None
if 'calendar_service' not in st.session_state:
    st.session_state.calendar_service = None
if 'view' not in st.session_state:
    st.session_state.view = 'Dashboard'

# -------------------- Sidebar --------------------
with st.sidebar:
    st.title("📬 AI Email Assistant")
    if not st.session_state.authenticated:
        if st.button("🔐 Authenticate with Google"):
            try:
                gmail_service, calendar_service = authenticate_google_services()
                st.session_state.gmail_service = gmail_service
                st.session_state.calendar_service = calendar_service
                st.session_state.authenticated = True
                st.success("Authenticated!")
                st.rerun()
            except Exception as e:
                st.error(f"Auth Failed: {e}")
    else:
        st.success("✅ Authenticated")
        st.radio("View Mode", ["Dashboard", "Inbox", "AI Assistant", "Calendar", "Insights", "Settings"], key='view')
        st.markdown("---")
        st.subheader("Actions")
        if st.button("📥 Fetch Emails"):
            fetch_and_store_emails(st.session_state.gmail_service)
            st.success("Fetched!")
            st.rerun()
        if st.button("🤖 Auto Reply Emails"):
            session = SessionLocal()
            emails = session.query(Email).filter(Email.id.in_(st.session_state.selected_email_ids)).all()
            if not emails:
                st.warning("No selected emails to reply.")
            else:
                replied_count = 0
                for email in emails:
                    if '[Replied]' in email.subject:
                        continue
                    reply = generate_reply(email.body)
                    if reply and "Draft generation failed" not in reply.lower():
                        send_email(st.session_state.gmail_service, email.sender, f"Re: {email.subject} [Replied]", reply)
                        email.subject += " [Replied]"
                        parsed_dt = extract_meeting_datetime(email.body, email_received_date=email.date)
                        if parsed_dt:
                            start_time = parsed_dt.replace(tzinfo=gettz(st.session_state.timezone))
                            summary = generate_event_title(email.body)
                            create_event(st.session_state.calendar_service, summary, start_time.isoformat())
                        replied_count += 1
                session.commit()
                st.success(f"✅ {replied_count} email(s) replied.")
            session.close()
            st.session_state.selected_email_ids.clear()
            st.rerun()

# -------------------- Main --------------------
st.title("📨 AI Email Assistant")

if not st.session_state.authenticated:
    st.warning("Please authenticate to proceed.")
    st.stop()

init_db()
session = SessionLocal()
emails = session.query(Email).order_by(Email.date.desc()).all()
df = pd.DataFrame([{
    "ID": e.id,
    "Subject": e.subject,
    "Sender": e.sender,
    "Date": e.date,
    "Body": e.body
} for e in emails])

# -------------------- Dashboard --------------------
if st.session_state.view == "Dashboard":
    st.header("📊 Overview")
    col1, col2, col3 = st.columns(3)
    today = datetime.now().date()
    today_count = len(df[df['Date'].dt.date == today]) if not df.empty and 'Date' in df.columns else 0
    col1.metric("Total Emails", len(df))
    col2.metric("Today's Emails", today_count)
    col3.metric("Unique Senders", df['Sender'].nunique() if not df.empty else 0)

    if not df.empty:
        df['Hour'] = df['Date'].dt.hour
        st.subheader("📈 Email Distribution by Hour")
        fig = px.histogram(df, x='Hour', nbins=24, title='Hourly Email Volume')
        st.plotly_chart(fig, use_container_width=True)

# -------------------- Inbox --------------------
elif st.session_state.view == "Inbox":
    st.header("📥 Inbox")
    if df.empty:
        st.info("No emails fetched yet.")
    else:
        for _, row in df.iterrows():
            with st.expander(f"📧 {row['Subject']} - {row['Sender']}"):
                st.write(f"**Date:** {row['Date']}")
                st.write(f"**From:** {row['Sender']}")
                st.write(row['Body'])

                selected = st.checkbox("✅ Select this email", key=f"select_{row['ID']}")
                if selected:
                    st.session_state.selected_email_ids.add(row['ID'])
                else:
                    st.session_state.selected_email_ids.discard(row['ID'])

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🧠 Summarize", key=f"summary_{row['ID']}"):
                        st.success(summarize_email(row['Body']))
                with col2:
                    if st.button("✉️ Draft Reply", key=f"reply_{row['ID']}"):
                        st.info(generate_reply(row['Body']))
                with col3:
                    if st.button("📅 Schedule Meeting", key=f"meet_{row['ID']}"):
                        meeting_dt = extract_meeting_datetime(row['Body'], row['Date'])
                        if meeting_dt:
                            start_time = meeting_dt.replace(tzinfo=gettz(st.session_state.timezone))
                            summary = generate_event_title(row['Body'])
                            link = create_event(st.session_state.calendar_service, summary, start_time.isoformat())
                            if link:
                                st.success(f"Event Created! [View]({link})")
                            else:
                                st.error("Event creation failed.")
                        else:
                            st.warning("No valid datetime found.")

# -------------------- AI Assistant Playground --------------------
elif st.session_state.view == "AI Assistant":
    st.header("🤖 AI Assistant Playground")
    selected_text = st.text_area("📥 Paste email content or type manually", height=200)
    if selected_text:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🧠 Summarize Email"):
                st.write(summarize_email(selected_text))
        with col2:
            if st.button("✉️ Generate Reply"):
                st.write(generate_reply(selected_text))
        with col3:
            if st.button("❓ Extract Questions"):
                st.write(extract_question_from_email(selected_text) or "No question found")
        if st.button("📅 Generate Event Title"):
            st.info(generate_event_title(selected_text))

# -------------------- Calendar --------------------
elif st.session_state.view == "Calendar":
    st.header("📅 Manual Calendar Event")
    title = st.text_input("Event Title")
    date = st.date_input("Event Date")
    time = st.time_input("Start Time")
    if st.button("Create Calendar Event"):
        dt = datetime.combine(date, time).replace(tzinfo=gettz(st.session_state.timezone))
        link = create_event(st.session_state.calendar_service, title, dt.isoformat())
        if link:
            st.success(f"📅 Event created! [View]({link})")

# -------------------- Insights --------------------
elif st.session_state.view == "Insights":
    st.header("📊 Email Trends")
    if not df.empty and 'Date' in df.columns:
        st.subheader("Daily Volume")
        daily = df.groupby(df['Date'].dt.date).size().reset_index(name='Count')
        st.bar_chart(daily.set_index('Date'))

        st.subheader("Top Senders")
        top = df['Sender'].value_counts().head(10)
        st.dataframe(top)

# -------------------- Settings --------------------
elif st.session_state.view == "Settings":
    st.header("⚙️ Settings & Preferences")
    st.subheader("🔢 Max Emails to Fetch")
    st.session_state.max_emails = st.slider("How many emails to fetch?", 5, 50, st.session_state.max_emails)

    st.subheader("🤖 Auto-Reply Toggle")
    st.session_state.auto_reply_enabled = st.checkbox("Enable Auto Reply", value=st.session_state.auto_reply_enabled)

    st.subheader("💬 Custom Greeting for Auto Replies")
    st.session_state.custom_greeting = st.text_input("Greeting Text", value=st.session_state.custom_greeting)

    st.subheader("⏱️ Default Meeting Duration (mins)")
    st.session_state.meeting_duration = st.selectbox("Duration", [15, 30, 45, 60], index=[15, 30, 45, 60].index(st.session_state.meeting_duration))

    st.subheader("🌍 Timezone")
    st.session_state.timezone = st.selectbox("Timezone", ["Asia/Kolkata", "UTC", "US/Eastern", "Europe/London"],
                                             index=["Asia/Kolkata", "UTC", "US/Eastern", "Europe/London"].index(st.session_state.timezone))

    st.subheader("🔔 Slack Notification")
    st.session_state.slack_enabled = st.toggle("Send Slack Alerts", value=st.session_state.slack_enabled)

    st.subheader("🧠 AI Model Temperature")
    st.session_state.ai_temperature = st.slider("AI Temperature (creativity)", 0.0, 1.0, st.session_state.ai_temperature, step=0.05)

# -------------------- Footer --------------------
session.close()
st.markdown("---")
st.caption("Built with 💡 using Streamlit + Google APIs + Gemini AI")
