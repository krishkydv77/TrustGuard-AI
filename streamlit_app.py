import os
import requests
import streamlit as st

st.set_page_config(page_title="TrustGuard AI", page_icon="🛡️", layout="wide")
api_url = os.getenv("SAFEASSIST_API_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")
st.title("TrustGuard AI— Intelligent Customer Support Automation & Trust Safety Platform")
st.caption("Secure Conversations. Intelligent Decisions. Trusted Automation.")

# Browser-session auth state. The token is kept only in Streamlit's session state.
if "access_token" not in st.session_state:
    st.session_state.access_token = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""


def auth_headers():
    token = st.session_state.get("access_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def show_api_error(response):
    try:
        detail = response.json().get("detail", response.text)
    except (ValueError, AttributeError):
        detail = response.text
    st.error(f"Request failed ({response.status_code}): {detail}")

with st.sidebar:
    st.header("Account")
    if st.session_state.access_token:
        st.success(f"Signed in as {st.session_state.user_email}")
        if st.button("Sign out", use_container_width=True):
            st.session_state.access_token = ""
            st.session_state.user_email = ""
            st.rerun()
    else:
        login_tab, register_tab = st.tabs(["Sign in", "Register"])
        with login_tab:
            with st.form("login_form"):
                login_email = st.text_input("Email", key="login_email", placeholder="you@example.com")
                login_password = st.text_input("Password", type="password", key="login_password")
                login_submit = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if login_submit:
                try:
                    response = requests.post(
                        f"{api_url}/auth/login",
                        json={"email": login_email.strip(), "password": login_password}, timeout=20,
                    )
                    if response.ok:
                        data = response.json()
                        st.session_state.access_token = data["access_token"]
                        st.session_state.user_email = data["user"]["email"]
                        st.success("Signed in successfully.")
                        st.rerun()
                    else:
                        show_api_error(response)
                except requests.RequestException as exc:
                    st.error(f"Could not connect to API: {exc}")
        with register_tab:
            with st.form("register_form"):
                register_email = st.text_input("Email address", key="register_email", placeholder="you@example.com")
                register_password = st.text_input("Password (at least 8 characters)", type="password", key="register_password")
                register_confirm = st.text_input("Confirm password", type="password", key="register_confirm")
                register_submit = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if register_submit:
                if register_password != register_confirm:
                    st.error("Passwords do not match.")
                elif len(register_password) < 8:
                    st.error("Password must contain at least 8 characters.")
                else:
                    try:
                        response = requests.post(
                            f"{api_url}/auth/register",
                            json={"email": register_email.strip(), "password": register_password}, timeout=20,
                        )
                        if response.ok:
                            data = response.json()
                            st.session_state.access_token = data["access_token"]
                            st.session_state.user_email = data["user"]["email"]
                            st.success("Account created and signed in.")
                            st.rerun()
                        else:
                            show_api_error(response)
                    except requests.RequestException as exc:
                        st.error(f"Could not connect to API: {exc}")
        st.caption("Demo account: demo@safeassist.com / Demo@12345")
        st.caption("Use a unique password for personal accounts.")

chat_tab, moderation_tab, analytics_tab = st.tabs(["Support Chat", "Moderation Playground", "Analytics"])

with chat_tab:
    st.subheader("Customer support assistant")
    if st.session_state.access_token:
        st.caption("Signed-in order and refund requests use your authenticated account.")
    else:
        st.info("You can ask general questions without signing in. Sign in to look up your orders or submit refund requests.")
    message = st.text_area("Message", placeholder="Where is my order?", key="chat_message")
    if st.button("Send message", type="primary"):
        if not message.strip():
            st.warning("Enter a message first.")
        else:
            try:
                r = requests.post(f"{api_url}/chat", json={"message": message.strip()}, headers=auth_headers(), timeout=30)
                if r.ok:
                    data = r.json()
                    st.success(data["response"])
                    st.write({"intent": data["intent"], "moderation": data["moderation_action"], "source": data["source"], "request_id": data["request_id"]})
                else:
                    show_api_error(r)
            except requests.RequestException as exc:
                st.error(f"Could not connect to API: {exc}")

with moderation_tab:
    st.subheader("Trust & safety test")
    text = st.text_area("Text to evaluate", key="moderation_text", placeholder="Paste a message to check")
    if st.button("Check moderation"):
        if not text.strip():
            st.warning("Enter some text first.")
        else:
            try:
                r = requests.post(f"{api_url}/moderation/check", json={"text": text.strip()}, timeout=30)
                if r.ok:
                    result = r.json()
                    st.metric("Action", result["action"])
                    st.json(result)
                else:
                    show_api_error(r)
            except requests.RequestException as exc:
                st.error(f"Could not connect to API: {exc}")

with analytics_tab:
    st.subheader("Operational overview")
    if st.button("Refresh analytics"):
        try:
            r = requests.get(f"{api_url}/analytics/overview", timeout=15)
            r.raise_for_status()
            stats = r.json()
            c1, c2, c3 = st.columns(3)
            c1.metric("Chat requests", stats["total_chats"])
            c2.metric("Moderation checks", stats["moderation_checks"])
            c3.metric("Avg latency (ms)", stats["average_chat_latency_ms"])
            st.json(stats)
        except requests.RequestException as exc:
            st.error(f"Could not load analytics: {exc}")
