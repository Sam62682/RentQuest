import random
import smtplib
from email.message import EmailMessage
def otp_gen_sender():
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    print(otp) 
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    from_email = 'samkurre62682@gmail.com'
    server.login(from_email, 'mony nnfa nahn pdxn')
    to_mail = input("Enter your email : ")

    msg = EmailMessage()
    msg['Subject'] = "OTP Verfication"
    msg['From'] = from_email
    msg['To'] = to_mail
    msg.set_content("Your OTP is : " + otp)

    server.send_message(msg)
    return otp
a = otp_gen_sender()
input_otp = input("Enter OTP : ")
if input_otp == a:
    print("OTP Verified")
else:
    print("Invalid OTP")
