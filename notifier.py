"""Sends daily job alert email via Gmail SMTP."""

import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _job_row(job: dict) -> str:
    return (
        f'<tr>'
        f'<td style="padding:6px 12px;border-bottom:1px solid #eee">'
        f'<a href="{job["url"]}" style="color:#36f;text-decoration:none">{job["title"]}</a>'
        f'</td>'
        f'<td style="padding:6px 12px;border-bottom:1px solid #eee;color:#555">{job["company"]}</td>'
        f'<td style="padding:6px 12px;border-bottom:1px solid #eee;color:#555">{job["location"]}</td>'
        f'</tr>'
    )


def _build_html(diff: dict, today: date) -> str:
    added = diff["added"]
    removed = diff["removed"]
    total = diff["total_today"]

    added_rows = "".join(_job_row(j) for j in added) if added else (
        '<tr><td colspan="3" style="padding:8px 12px;color:#999">없음</td></tr>'
    )
    removed_rows = "".join(_job_row(j) for j in removed) if removed else (
        '<tr><td colspan="3" style="padding:8px 12px;color:#999">없음</td></tr>'
    )

    table_style = 'style="width:100%;border-collapse:collapse;font-size:14px"'
    header_style = 'style="background:#f5f5f5;text-align:left;padding:8px 12px;font-weight:bold;color:#333"'

    return f"""
<html><body style="font-family:sans-serif;max-width:720px;margin:0 auto;padding:24px">
  <h2 style="color:#333">원티드 QA 채용 알림 — {today.strftime('%Y년 %m월 %d일')}</h2>
  <p style="color:#555">검색 조건: QA · 경력 3~7년 · 서울/인천/경기 · 현재 공고 <strong>{total}개</strong></p>

  <h3 style="color:#2a9d2a">🆕 새로운 공고 ({len(added)}개)</h3>
  <table {table_style}>
    <tr>
      <th {header_style}>포지션</th>
      <th {header_style}>회사</th>
      <th {header_style}>지역</th>
    </tr>
    {added_rows}
  </table>

  <h3 style="color:#e06060;margin-top:32px">❌ 마감된 공고 ({len(removed)}개)</h3>
  <table {table_style}>
    <tr>
      <th {header_style}>포지션</th>
      <th {header_style}>회사</th>
      <th {header_style}>지역</th>
    </tr>
    {removed_rows}
  </table>

  <p style="margin-top:32px;font-size:12px;color:#aaa">
    원티드 QA 채용 알리미 · 매일 오전 10시 발송
  </p>
</body></html>
"""


def send_email(diff: dict, to_addr: str | None = None) -> None:
    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    recipient = to_addr or os.environ.get("ALERT_TO", smtp_user)

    today = date.today()
    subject = (
        f"[원티드 QA] {today.strftime('%m/%d')} "
        f"새공고 {len(diff['added'])}개 · 마감 {len(diff['removed'])}개"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg.attach(MIMEText(_build_html(diff, today), "html", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.ehlo()
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.sendmail(smtp_user, recipient, msg.as_string())

    print(f"이메일 발송 완료 → {recipient}")
