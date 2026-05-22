import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from langchain.tools import tool
import markdown


def build_html_report(markdown_content: str, subject: str) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    html_content = markdown.markdown(
        markdown_content,
        extensions=["extra", "nl2br", "sane_lists"]
    )

    html = f"""
    <html>
        <head>
            <meta charset="UTF-8" />
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f6f8;
                    margin: 0;
                    padding: 0;
                    color: #1f2937;
                }}
                .container {{
                    max-width: 800px;
                    margin: 40px auto;
                    background: #ffffff;
                    padding: 32px;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                }}
                .header {{
                    background: #0f172a;
                    color: white;
                    padding: 24px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 24px;
                }}
                .title {{
                    font-size: 22px;
                    margin: 0;
                }}
                .subtitle {{
                    font-size: 14px;
                    opacity: 0.85;
                    margin-top: 8px;
                }}
                .badge {{
                    display: inline-block;
                    background: #2563eb;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 999px;
                    font-size: 12px;
                    margin-top: 12px;
                }}
                .content {{
                    line-height: 1.7;
                    font-size: 15px;
                }}
                .content h1,
                .content h2,
                .content h3,
                .content h4 {{
                    color: #0f172a;
                    margin-top: 28px;
                    margin-bottom: 12px;
                }}
                .content p {{
                    margin: 0 0 14px 0;
                }}
                .content ul,
                .content ol {{
                    margin: 0 0 14px 22px;
                }}
                .content blockquote {{
                    border-left: 4px solid #cbd5e1;
                    margin: 16px 0;
                    padding: 10px 16px;
                    background: #f8fafc;
                    color: #334155;
                }}
                .content code {{
                    background: #f1f5f9;
                    padding: 2px 6px;
                    border-radius: 6px;
                    font-family: Consolas, monospace;
                    font-size: 13px;
                }}
                .content pre {{
                    background: #0f172a;
                    color: #e2e8f0;
                    padding: 16px;
                    border-radius: 10px;
                    overflow-x: auto;
                    font-size: 13px;
                }}
                .content pre code {{
                    background: transparent;
                    padding: 0;
                    color: inherit;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 12px;
                    color: #64748b;
                    text-align: center;
                    border-top: 1px solid #e5e7eb;
                    padding-top: 16px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="title">Relatório por Email</h1>
                    <div class="subtitle">Gerado a partir do conteúdo Markdown da IA</div>
                    <div class="badge">{subject}</div>
                </div>

                <div class="content">
                    {html_content}
                </div>

                <div class="footer">
                    Generated at {generated_at}
                </div>
            </div>
        </body>
    </html>
    """

    return html


@tool(return_direct=False)
def send_email(report: str, subject: str = "Generated Report") -> str:
    """
    Envia um relatório por email
    """

    sender = os.getenv("SMTP_SENDER")
    password = os.getenv("SMTP_APP_PASSWORD")
    recipient = os.getenv("SMTP_RECIPIENT")

    if not sender or not password or not recipient:
        return "O serviço de email está indisponível, entre em contato com a empresa pra corrigir o erro [ERR: EMAIL_CONFIG]"

    html_content = build_html_report(report, subject)

    message = MIMEMultipart("alternative")
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(html_content, "html", "utf-8"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipient, message.as_string())
    server.quit()

    return "Email sent successfully"