import csv
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO
from typing import List, Optional, Union

import requests

from .components import AlertComponent, Table
from .core import (
    attach_tables,
    render_components_html,
    render_components_md,
    use_inline_tables,
)
from .settings import AlertMsgs, EmailSettings, SlackSettings, logger


def send_email(
    subject: str,
    components: List[AlertComponent],
    settings: Optional[EmailSettings] = None,
    n_attempts: int = 2,
    **_,
) -> bool:
    """Send an email using SMTP.

    Args:
        subject (str): The email subject.
        components (List[AlertComponent]): Components that should be included in the email, in order that they should be rendered from top to bottom.
        smtp_server (str, optional): The email server the email should be sent with. Defaults to "smtp.gmail.com".
        smtp_port (int, optional): Port of the email server. Defaults to 465.
        settings (Optional[EmailSettings], optional): Email settings. Defaults to None.
        n_attempts (int, optional): Number of attempt that should be made to send the email. Defaults to 2.

    Returns:
        bool: Whether the email was sent successfully or not.
    """
    settings = settings or EmailSettings()

    def _construct_message(body: str, tables: List[Table] = []) -> MIMEMultipart:
        message = MIMEMultipart("mixed")
        message["From"] = settings.addr
        message["To"] = settings.receiver_addr
        message["Subject"] = subject

        body = MIMEText(body, "html")
        message.attach(body)

        if not isinstance(tables, (list, tuple)):
            tables = [tables]

        # attach tables as CSV files.
        for table_no, table in enumerate(tables, start=1):
            file = StringIO()
            csv.DictWriter(file, fieldnames=table.header).writerows(table.rows)
            file.seek(0)
            p = MIMEText(file.read(), _subtype="text/csv")
            stem = table.caption[:50].replace(" ", "_") if table.caption else f"table"
            filename = f"{stem}_{table_no}.csv"
            p.add_header("Content-Disposition", f"attachment; filename={filename}")
            message.attach(p)
        return message

    def _send_message(message: MIMEMultipart):
        """Send a message using SMTP."""
        with smtplib.SMTP_SSL(
            host=settings.smtp_server,
            port=settings.smtp_port,
            context=ssl.create_default_context(),
        ) as s:
            for _ in range(n_attempts):
                try:
                    s.login(settings.addr, settings.password)
                    s.send_message(message)
                    return True
                except smtplib.SMTPSenderRefused as e:
                    logger.error(f"{type(e)} Error sending email: {e}")
        logger.error(
            f"Exceeded max number of attempts ({n_attempts}). Email can not be sent."
        )
        return False

    # generate HTML from components.
    email_body = render_components_html(
        components, inline_tables_max_rows=settings.inline_tables_max_rows
    )

    tables = [t for t in components if isinstance(t, Table)]
    # check if we should add table CSVs as attachments.
    attachment_tables = (
        [tables]
        if not use_inline_tables(tables, settings.inline_tables_max_rows)
        and attach_tables(tables, settings.attachment_max_size_mb)
        else []
    )
    if not _send_message(_construct_message(email_body, tables=attachment_tables)):
        # try sending again, but with tables as attachments.
        subject += f" ({len(attachment_tables)} Failed Attachments)"
        return _send_message(_construct_message(email_body))
    logger.info("Email sent successfully.")
    return True


def send_slack_message(
    components: List[AlertComponent],
    settings: Optional[SlackSettings] = None,
    n_attempts: int = 2,
    **_,
):
    # TODO attachments.
    settings = settings or SlackSettings()
    body = render_components_md(
        components=components,
        slack_format=True,
        inline_tables_max_rows=settings.inline_tables_max_rows,
    )
    for _ in range(n_attempts):
        resp = requests.post(settings.webhook, json={"text": body, "mrkdwn": True})
        logger.debug(f"[{resp.status_code}] {settings.webhook}")
        if resp.status_code == 200:
            logger.info("Slack alert sent successfully.")
            return True
        logger.error(f"[{resp.status_code}] {resp.text}")
    logger.error("Failed to send Slack alert.")
    return False


def send_alert(
    components: List[AlertComponent],
    methods: Optional[Union["email", "slack"]] = None,
    **kwargs,
):
    if isinstance(methods, str):
        methods = [methods]
    elif methods is None:
        methods = []
        settings = AlertMsgs()
        if settings.alert_slack:
            methods.append("slack")
        if settings.send_email:
            methods.append("email")
    funcs = []
    if "email" in methods:
        funcs.append(send_email)
    if "slack" in methods:
        funcs.append(send_slack_message)
    if not funcs:
        raise ValueError(f"Unknown method '{methods}'. Valid choices: slack, email.")
    return all([func(components=components, **kwargs) for func in funcs])
