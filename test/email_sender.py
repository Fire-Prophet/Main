# email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_email(sender_email, sender_password, receiver_email, subject, body, smtp_server, smtp_port=587):
    """
    SMTP 서버를 통해 이메일을 보냅니다.
    보안상의 이유로 실제 비밀번호 대신 환경 변수나 보안 저장소를 사용하는 것이 좋습니다.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # TLS 보안 시작
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
        logging.info(f"Email successfully sent from {sender_email} to {receiver_email}.")
        return True
    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP Authentication Error: The username or password you entered is not correct.")
        return False
    except smtplib.SMTPConnectError:
        logging.error(f"SMTP Connection Error: Could not connect to {smtp_server}:{smtp_port}. Check server address and port.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending email: {e}")
        return False

# 예시 사용 (실제 계정 정보로 대체 필요)
if __name__ == "__main__":
    # 실제 사용 시 환경 변수나 보안 설정에서 불러오세요.
    # 예:
    # SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
    # SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
    SENDER_EMAIL = "your_email@example.com" # 실제 발신자 이메일로 변경
    SENDER_PASSWORD = "your_email_password" # 실제 발신자 비밀번호로 변경 (주의: 실제 코드에서는 직접 노출 금지)
    RECEIVER_EMAIL = "recipient@example.com" # 실제 수신자 이메일로 변경
    SMTP_SERVER = "smtp.example.com" # 실제 SMTP 서버 주소로 변경 (예: smtp.gmail.com)
    SMTP_PORT = 587 # 대부분의 경우 587

    email_subject = "Test Email from Python"
    email_body = "This is a test email sent from a Python script using smtplib."

    if SENDER_EMAIL == "your_email@example.com":
        logging.warning("Please update SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, and SMTP_SERVER with actual values to run the example.")
        print("\nSkipping email sending example. Please configure 'SENDER_EMAIL', 'SENDER_PASSWORD', etc., in email_sender.py.")
    else:
        print(f"Attempting to send email from {SENDER_EMAIL} to {RECEIVER_EMAIL}...")
        if send_email(SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, email_subject, email_body, SMTP_SERVER, SMTP_PORT):
            print("Email sent successfully!")
        else:
            print("Failed to send email. Check logs for details.")
