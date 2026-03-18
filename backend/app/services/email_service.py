import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending verification and reminder emails"""
    
    def __init__(self):
        # SMTP Configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.smtp_username or not self.smtp_password:
            logger.error("SMTP credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            # Add text content if provided
            if text_content:
                part1 = MIMEText(text_content, "plain")
                msg.attach(part1)
            
            # Add HTML content
            part2 = MIMEText(html_content, "html")
            msg.attach(part2)
            
            # Send email
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_verification_email(self, to_email: str, verification_token: str, verification_url: str) -> bool:
        """
        Send email verification email
        
        Args:
            to_email: Recipient email address
            verification_token: Verification token
            verification_url: Full verification URL
        """
        subject = "Verify Your Email - Todo App Phase V"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9fafb;
                    border-radius: 8px;
                    padding: 30px;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background-color: #3b82f6;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
                .button:hover {{
                    background-color: #2563eb;
                }}
                .code {{
                    background-color: #f3f4f6;
                    padding: 15px;
                    border-radius: 6px;
                    font-family: monospace;
                    font-size: 18px;
                    letter-spacing: 2px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 14px;
                    color: #6b7280;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Verify Your Email Address</h2>
                <p>Thank you for registering with Todo App Phase V! To complete your registration, please verify your email address.</p>
                
                <p>Click the button below to verify:</p>
                <a href="{verification_url}" class="button">Verify Email</a>
                
                <p>Or copy and paste this verification code:</p>
                <div class="code">{verification_token}</div>
                
                <p>This verification link will expire in 24 hours.</p>
                
                <p>If you didn't create an account, you can safely ignore this email.</p>
            </div>
            
            <div class="footer">
                <p>Todo App Phase V &copy; 2026</p>
                <p>This is an automated message, please do not reply.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Verify Your Email Address
        
        Thank you for registering with Todo App Phase V!
        
        Click the link below to verify your email:
        {verification_url}
        
        Or copy and paste this verification code:
        {verification_token}
        
        This verification link will expire in 24 hours.
        
        If you didn't create an account, you can safely ignore this email.
        
        ---
        Todo App Phase V &copy; 2026
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_task_reminder_email(
        self,
        to_email: str,
        user_name: str,
        task_title: str,
        task_description: Optional[str],
        due_date: str,
        priority: str = "medium"
    ) -> bool:
        """
        Send task reminder email
        
        Args:
            to_email: Recipient email address
            user_name: User's name
            task_title: Task title
            task_description: Task description
            due_date: Due date formatted string
            priority: Task priority (low, medium, high)
        """
        priority_colors = {
            "low": "#10b981",
            "medium": "#f59e0b",
            "high": "#ef4444"
        }
        priority_color = priority_colors.get(priority, "#f59e0b")
        
        subject = f"Task Reminder: {task_title}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9fafb;
                    border-radius: 8px;
                    padding: 30px;
                    margin: 20px 0;
                }}
                .priority-badge {{
                    display: inline-block;
                    background-color: {priority_color};
                    color: white;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                .task-details {{
                    background-color: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 6px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .task-title {{
                    font-size: 20px;
                    font-weight: 600;
                    margin-bottom: 10px;
                }}
                .task-description {{
                    color: #6b7280;
                    margin: 10px 0;
                }}
                .due-date {{
                    color: #ef4444;
                    font-weight: 600;
                    margin-top: 15px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 14px;
                    color: #6b7280;
                }}
                .button {{
                    display: inline-block;
                    background-color: #3b82f6;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Hello {user_name}!</h2>
                <p>This is a reminder about your upcoming task:</p>
                
                <div class="task-details">
                    <div class="task-title">{task_title}</div>
                    <span class="priority-badge">{priority}</span>
                    {f'<p class="task-description">{task_description}</p>' if task_description else ''}
                    <p class="due-date">Due: {due_date}</p>
                </div>
                
                <a href="http://localhost:3000/dashboard" class="button">View Dashboard</a>
                
                <p>Stay on top of your tasks!</p>
            </div>
            
            <div class="footer">
                <p>Todo App Phase V &copy; 2026</p>
                <p>You're receiving this email because you enabled task reminders.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Task Reminder
        
        Hello {user_name},
        
        This is a reminder about your upcoming task:
        
        Task: {task_title}
        Priority: {priority}
        Due: {due_date}
        
        {f'Description: {task_description}' if task_description else ''}
        
        Stay on top of your tasks!
        
        ---
        Todo App Phase V &copy; 2026
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, reset_token: str, reset_url: str) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            reset_url: Full reset URL
        """
        subject = "Reset Your Password - Todo App Phase V"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9fafb;
                    border-radius: 8px;
                    padding: 30px;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background-color: #ef4444;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
                .code {{
                    background-color: #f3f4f6;
                    padding: 15px;
                    border-radius: 6px;
                    font-family: monospace;
                    font-size: 18px;
                    letter-spacing: 2px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    font-size: 14px;
                    color: #6b7280;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Password Reset Request</h2>
                <p>You requested to reset your password. Click the button below to proceed:</p>
                
                <a href="{reset_url}" class="button">Reset Password</a>
                
                <p>Or use this verification code:</p>
                <div class="code">{reset_token}</div>
                
                <p>This link will expire in 1 hour.</p>
                
                <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
            </div>
            
            <div class="footer">
                <p>Todo App Phase V &copy; 2026</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()
