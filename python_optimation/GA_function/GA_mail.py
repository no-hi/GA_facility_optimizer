import smtplib
from email.mime.text import MIMEText

smtp_host = 'smtp.gmail.com'             # SMTPサーバのホスト名
smtp_port = 587                          # SMTPサーバのポート番号安全接続＝587
to_email = 'hyo15.3318@gmail.com'        # 送信先のEmailアドレス

def send_error_email(error_message,output_directory_name):
    from_email = 'errorman15.3318@gmail.com' # 送信元のEmailアドレス
    username = 'errorman15.3318@gmail.com'   # SMTPサーバのユーザ名
    password = 'yurq vewc ezvo uarq'         # SMTPサーバのパスワード

    error_message = '\n'.join(error_message) if isinstance(error_message, list) else error_message
    msg = MIMEText(error_message)
    msg['Subject'] = f'エラーマンだよ{output_directory_name}'
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()                    # TLSセキュリティを開始
        server.login(username, password)     # SMTPサーバにログイン
        server.send_message(msg)             # メールを送信

def send_end_email(end_message,output_directory_name):
    from_email = 'enderman15.3318@gmail.com' # 送信元のEmailアドレス
    username = 'enderman15.3318@gmail.com'   # SMTPサーバのユーザ名
    password = 'chdw cspd yjbj avmy'         # SMTPサーバのパスワード

    end_message = '\n'.join(end_message) if isinstance(end_message, list) else end_message
    msg = MIMEText(end_message)
    msg['Subject'] = f'えんだーまんより{output_directory_name}'
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()                    # TLSセキュリティを開始
        server.login(username, password)     # SMTPサーバにログイン
        server.send_message(msg)             # メールを送信