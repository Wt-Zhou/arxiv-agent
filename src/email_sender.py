"""
邮件发送模块
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List


class EmailSender:
    """邮件发送器"""

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str,
                 sender_password: str, use_ssl: bool = False):
        """
        初始化邮件发送器

        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            sender_email: 发件人邮箱
            sender_password: 发件人密码或应用专用密码
            use_ssl: 是否使用SSL
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_ssl = use_ssl

    def send_report(self, receiver_emails: List[str], subject: str,
                    report_path: str, summary: str) -> bool:
        """
        发送报告邮件

        Args:
            receiver_emails: 收件人邮箱列表
            subject: 邮件主题
            report_path: 报告文件路径
            summary: 邮件正文摘要

        Returns:
            是否发送成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(receiver_emails)
            msg['Subject'] = subject

            # 邮件正文
            body = f"""
您好！

{summary}

详细报告请查看附件。

---
此邮件由 ArXiv Agent 自动发送
"""
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # 添加附件
            if os.path.exists(report_path):
                with open(report_path, 'rb') as f:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(f.read())
                    encoders.encode_base64(attachment)

                    filename = os.path.basename(report_path)
                    attachment.add_header('Content-Disposition',
                                        f'attachment; filename={filename}')
                    msg.attach(attachment)

            # 发送邮件
            if self.use_ssl:
                # 使用SSL连接
                print(f"正在连接到 {self.smtp_server}:{self.smtp_port} (SSL)...")
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.set_debuglevel(0)  # 设置为1可以看到详细的SMTP交互日志
                    print("正在登录...")
                    server.login(self.sender_email, self.sender_password)
                    print("正在发送邮件...")
                    server.send_message(msg)
            else:
                # 使用TLS连接
                print(f"正在连接到 {self.smtp_server}:{self.smtp_port} (STARTTLS)...")
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                    server.set_debuglevel(0)
                    print("正在启动TLS加密...")
                    server.starttls()
                    print("正在登录...")
                    server.login(self.sender_email, self.sender_password)
                    print("正在发送邮件...")
                    server.send_message(msg)

            print(f"✅ 邮件发送成功！收件人: {', '.join(receiver_emails)}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ 邮件发送失败: 认证错误（用户名或密码错误）")
            print(f"   请检查：1) 邮箱地址是否正确 2) 是否使用了授权码（不是登录密码）")
            print(f"   错误详情: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            print(f"❌ 邮件发送失败: 服务器连接断开")
            print(f"   可能原因：1) 端口配置错误 2) SSL设置不正确 3) 网络防火墙阻止")
            print(f"   建议：163邮箱使用 端口465+SSL 或 端口25+STARTTLS")
            print(f"   错误详情: {e}")
            return False
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            import traceback
            print(f"详细错误:\n{traceback.format_exc()}")
            return False

    def send_html_report(self, receiver_emails: List[str], subject: str,
                         html_content: str, attachments: Optional[List[str]] = None) -> bool:
        """
        发送HTML格式的报告邮件

        Args:
            receiver_emails: 收件人邮箱列表
            subject: 邮件主题
            html_content: HTML格式的邮件内容
            attachments: 附件文件路径列表

        Returns:
            是否发送成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(receiver_emails)
            msg['Subject'] = subject

            # 添加HTML内容
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 添加附件
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            attachment = MIMEBase('application', 'octet-stream')
                            attachment.set_payload(f.read())
                            encoders.encode_base64(attachment)

                            filename = os.path.basename(file_path)
                            attachment.add_header('Content-Disposition',
                                                f'attachment; filename={filename}')
                            msg.attach(attachment)

            # 发送邮件
            if self.use_ssl:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)

            print(f"✅ HTML邮件发送成功！收件人: {', '.join(receiver_emails)}")
            return True

        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            import traceback
            print(f"详细错误:\n{traceback.format_exc()}")
            return False
