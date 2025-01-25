from django.core.mail import EmailMessage, send_mail, send_mass_mail


def mail_sender(subject, message, recipient):
            message = message
            recipient = recipient
            sender = 'shakibulalamj@gmail.com'

            if not recipient:
                pass

            try:
                send_mail(subject, message, sender, [recipient], fail_silently=True)
                return True
            except Exception as e:
                pass

def mass_mail_sender(subject, message, recipient_list):
    sender = 'shakibulalamj@gmail.com'
    
    # Ensure subject, message, and recipient_list are valid
    if not (recipient_list and subject and message):
        print("Invalid inputs: subject, message, and recipient_list are required.")
        return
    
    try:
        # Prepare the email message tuple
        mail_message = (subject, message, sender, recipient_list)
        
        # send_mass_mail expects a sequence of such tuples
        send_mass_mail((mail_message,), fail_silently=False)
        print("Emails sent successfully!")
    except Exception as e:
        print(f"Error sending emails: {str(e)}")
