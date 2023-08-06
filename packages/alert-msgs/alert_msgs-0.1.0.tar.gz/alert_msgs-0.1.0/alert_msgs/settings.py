from pydantic import BaseSettings
from ready_logger import get_logger

logger = get_logger("alert-msgs")


class EmailSettings(BaseSettings):
    addr: str
    password: str
    receiver_addr: str
    attachment_max_size_mb: int = 20
    inline_tables_max_rows: int = 2000
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 465

    class Config:
        env_prefix = "alert_msgs_email_"


class SlackSettings(BaseSettings):
    webhook: str
    attachment_max_size_mb: int = 20
    inline_tables_max_rows: int = 200

    class Config:
        env_prefix = "alert_msgs_slack_"


class AlertMsgs(BaseSettings):
    send_email: bool
    alert_slack: bool

    class Config:
        env_prefix = "alert_msgs_"
