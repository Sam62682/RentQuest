import random
import smtplib
from email.message import EmailMessage

def otp_gen_sender():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    
    from_email = 'samkurre62682@gmail.com'
    server.login(from_email, 'mony nnfa nahn pdxn')

    print("Choose an option:\n1. OTP Verification\n2. Contact Us")
    choice = input("Enter choice (1 or 2): ")

    if choice == '1':
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        print(f"Generated OTP: {otp}")

        to_email = input("Enter your email for OTP: ")

        msg = EmailMessage()
        msg['Subject'] = "OTP Verification"
        msg['From'] = from_email
        msg['To'] = to_email
        msg.set_content(f"Your OTP is: {otp}")

        server.send_message(msg)
        print("OTP sent! Please check your email.")
        
        input_otp = input("Enter OTP: ")
        if input_otp == otp:
            print("OTP Verified")
        else:
            print("Invalid OTP")

    elif choice == '2':
        user_name = input("Enter your name: ")
        user_email = input("Enter your email: ")
        user_message = input("Enter your message: ")

        msg = EmailMessage()
        msg['Subject'] = "Contact Us Message"
        msg['From'] = from_email
        msg['To'] = from_email  # Send message to your own email
        msg.set_content(f"Message from {user_name} ({user_email}):\n\n{user_message}")

        server.send_message(msg)
        print("Your message has been sent! We will get back to you soon.")

    else:
        print("Invalid choice. Please restart and select a valid option.")

    server.quit()

otp_gen_sender()
