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
        f'<td style="padding:6px 12px;border-bottom:1px solid #eee;color:#555">{job.get("location", "")}</td>'
        f'</tr>'
    )


def _section_html(label: str, diff: dict, search_desc: str, table_style: str, header_style: str) -> str:
    added = diff["added"]
    removed = diff["removed"]
    total = diff["total_today"]

    empty = f'<tr><td colspan="3" style="padding:8px 12px;color:#999">없음</td></tr>'
    added_rows = "".join(_job_row(j) for j in added) if added else empty
    removed_rows = "".join(_job_row(j) for j in removed) if removed else empty

    return f"""
  <h2 style="color:#333;margin-top:40px;border-left:4px solid #36f;padding-left:12px">{label}</h2>
  <p style="color:#555;margin-top:4px">{search_desc} · 현재 공고 <strong>{total}개</strong> 추적 중</p>

  <h3 style="color:#2a9d2a">새로운 공고 ({len(added)}개)</h3>
  <table {table_style}>
    <tr>
      <th {header_style}>포지션</th>
      <th {header_style}>회사</th>
      <th {header_style}>지역</th>
    </tr>
    {added_rows}
  </table>

  <h3 style="color:#e06060;margin-top:24px">마감된 공고 ({len(removed)}개)</h3>
  <table {table_style}>
    <tr>
      <th {header_style}>포지션</th>
      <th {header_style}>회사</th>
      <th {header_style}>지역</th>
    </tr>
    {removed_rows}
  </table>
"""


def _build_html(wanted_diff: dict, remember_diff: dict, today: date) -> str:
    table_style = 'style="width:100%;border-collapse:collapse;font-size:14px"'
    header_style = 'style="background:#f5f5f5;text-align:left;padding:8px 12px;font-weight:bold;color:#333"'

    wanted_section = _section_html(
        "원티드 (Wanted)",
        wanted_diff,
        "QA · 경력 3~7년 · 서울/인천/경기",
        table_style,
        header_style,
    )
    remember_section = _section_html(
        "리멤버 (Remember)",
        remember_diff,
        "QA · 필터 없음 · 최신 1,000개 기준",
        table_style,
        header_style,
    )

    return f"""
<html><body style="font-family:sans-serif;max-width:760px;margin:0 auto;padding:24px">
  <h1 style="color:#222;font-size:20px">QA 채용 알림 — {today.strftime('%Y년 %m월 %d일')}</h1>
  {wanted_section}
  {remember_section}
  <p style="margin-top:40px;font-size:12px;color:#aaa">
    원티드 + 리멤버 QA 채용 알리미 · 매일 오전 9시 발송
  </p>
</body></html>
"""


def send_email(wanted_diff: dict, remember_diff: dict, to_addr: str | None = None) -> None:
    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ["SMTP_USER"]
    smtp_pass = os.environ["SMTP_PASS"]
    recipient = to_addr or os.environ.get("ALERT_TO", smtp_user)

    today = date.today()
    total_added = len(wanted_diff["added"]) + len(remember_diff["added"])
    total_removed = len(wanted_diff["removed"]) + len(remember_diff["removed"])
    subject = (
        f"[QA 채용] {today.strftime('%m/%d')} "
        f"새공고 {total_added}개 · 마감 {total_removed}개"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg.attach(MIMEText(_build_html(wanted_diff, remember_diff, today), "html", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.ehlo()
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.sendmail(smtp_user, recipient, msg.as_string())

    print(f"이메일 발송 완료 → {recipient}")
