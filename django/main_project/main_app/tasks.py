from celery import shared_task

@shared_task
def send_user_created_email(email, username):
    subject = "Welcome to the Platform!"
    message = f"Hello {username}, thanks for signing up!"
    from_email = "welcome@example.com"
    recipient_list = [email]
    print(f"Sending welcome email - Subject: {subject}, Message: {message}, From_Email: {from_email}, Recipient_List: {recipient_list}")
