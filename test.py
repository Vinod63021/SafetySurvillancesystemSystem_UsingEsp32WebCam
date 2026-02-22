from twilio.rest import Client

# 🔐 Replace with your real credentials
account_sid = ""
auth_token = ""

# Your Twilio number (from dashboard)
twilio_number = ""

# Parent number (must include country code)
to_number = ""

try:
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body="✅ Twilio Test Successful! Your Child Safety System SMS is working.",
        from_=twilio_number,
        to=to_number
    )

    print("✅ SMS Sent Successfully!")
    print("Message SID:", message.sid)

except Exception as e:
    print("❌ Error Sending SMS:")
    print(e)
