"""
Email utility to send notifications to users.
Shared component used by getStarted.py (pipeline start) and result.py (results view).
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from assets.logo_base64 import LOGO_BASE64
from pathlib import Path
from dotenv import dotenv_values
from utils.i18n import t

# Load environment configuration
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
ENV_CONFIG = dotenv_values(_ENV_PATH)
EMAIL_USER = ENV_CONFIG.get("EMAIL_USER", "iphylogeo@gmail.com")
EMAIL_PASSWORD = ENV_CONFIG.get("EMAIL_PASSWORD", "rogo lqhi fldu mwml")


def send_email(subject, content, user_email):
    """
    Send an email using Gmail SMTP.

    Args:
        subject (str): Email subject
        content (str): Email content (HTML)
        user_email (str): Recipient email address
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = EMAIL_USER
        message["To"] = user_email
        message["Subject"] = subject

        # HTML body
        html_content = MIMEText(content, "html", "UTF-8")
        message.attach(html_content)

        # Connect to SMTP server
        email_session = smtplib.SMTP("smtp.gmail.com", 587)
        email_session.starttls()
        email_session.login(EMAIL_USER, EMAIL_PASSWORD)
        email_session.sendmail(EMAIL_USER, user_email, message.as_string())
        email_session.quit()
        print(f"[Mail] Email sent successfully to {user_email}")
        return True
    except Exception as e:
        print(f"[Mail] Error sending email: {e}")
        return False


def get_results_email_template(results_url, lang="en"):
    """
    Generate the HTML content for the results email.

    Args:
        results_url (str): The URL path to the results (e.g., "/result/123")
    """
    # Ensure full URL if it's relative
    if not results_url.startswith("http"):
        full_url = f"http://localhost:8050{results_url}"
    else:
        full_url = results_url

    title = t("result.email-template.title", lang)
    completed = t("result.email-template.completed", lang)
    view_prompt = t("result.email-template.view-prompt", lang)
    button_text = t("result.email-template.button", lang)

    html_lang = "fr" if lang == "fr" else "en"

    return f"""
<!DOCTYPE html>
<html lang="{html_lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #e3e3e3;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            background-color: #f8f8f8;
            padding: 10px;
        }}
        .header img {{
            width: 250px;
            height: auto;
        }}
        .title {{
            text-align: center;
            font-size: 24px;
            margin: 20px 0;
            color: #333333;
        }}
        .content {{
            text-align: center;
            font-size: 16px;
            line-height: 1.5;
            color: #333333;
        }}
        .button-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .button {{
            display: inline-block;
            background-color: #007c58;
            color: #ffffff !important;
            padding: 15px 30px;
            text-decoration: none;
            font-size: 16px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{LOGO_BASE64}" alt="iPhyloGeo Logo">
        </div>
        <div class="title">
            {title}
        </div>
        <div class="content">
            <p>{completed}</p>
            <p>{view_prompt}</p>
        </div>
        <div class="button-container">
            <a href="{full_url}" class="button">{button_text}</a>
        </div>
    </div>
</body>
</html>
"""


def send_results_ready_email(user_email, results_url, lang="en"):
    """
    Send the standard 'Results Ready' email to the user.

    Args:
        user_email (str): Recipient email
        results_url (str): URL to the results page
    """
    subject = t("result.email-template.subject", lang)
    content = get_results_email_template(results_url, lang)
    return send_email(subject, content, user_email)
