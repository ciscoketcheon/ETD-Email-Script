### This script pull top target data from ETD in JSON output and send it in an email to administrator. 
### This script are shared on as-is basis. 

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import requests
import datetime


#### Define SMTP server and admin email address
# smtp_server = 'x.x.x.x'
# smtp_port = 25  # or your SMTP port
# smtp_username = 'etd_notification@yourdomain.com'
### optional, this code doesn't need SMTP AUTH ### smtp_password = 'your_smtp_password'
# admin_email = 'admin@yourdomain.com'
### Fill in the following variables before trying the script


smtp_server = ''
smtp_port = 25  # or your SMTP port
smtp_username = ''
#smtp_password = ''
admin_email = ''


### Get these value from ETD, create API credential, and API key with example as follow
### client_id = "ac6991c4-df45-xxxx-xxxx-xxxxxxxxx"
### client_password = "PxVRzLALsETnyrZri9oLiZ_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
### api_key = "twBJkLMj8l3pmMWtxxxxxxxxxxxxxxxxxxx"
### token_url and report_top_url is pre-populated, change to your API region
###
### Fill in the following variables before trying the script


# Define ETD parameters
client_id = ""
client_password = ""
api_key = ""
token_url = "https://api.beta.etd.cisco.com/v1/oauth/token"
#message_url = "https://api.beta.etd.cisco.com/v1/messages/search"
report_top_url = "https://api.beta.etd.cisco.com/v1/messages/report/top"


# Function to send email
def send_email(subject, json_data):
    # Convert JSON string to Python dict (if needed)
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    # Build table rows dynamically
    rows = ""
    for target in data["data"]["topTargets"]:
        rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #ddd;">{target['emailAddress']}</td>
            <td style="padding:8px;border:1px solid #ddd;color:#e74c3c;font-weight:bold;">{target['malicious']}</td>
            <td style="padding:8px;border:1px solid #ddd;">{target['phishing']}</td>
            <td style="padding:8px;border:1px solid #ddd;">{target['bec']}</td>
            <td style="padding:8px;border:1px solid #ddd;">{target['scam']}</td>
        </tr>
        """

    # HTML email body
    html_body = f"""
    <html>
    <body style="font-family:Arial, sans-serif;background-color:#f4f6f8;padding:20px;">
        <div style="background-color:#ffffff;padding:20px;border-radius:8px;">
            <h2 style="color:#2c3e50;">📊 ETD Daily Top Targets - {today}</h2>

            <table style="border-collapse:collapse;width:100%;">
                <tr style="background-color:#2c3e50;color:white;">
                    <th style="padding:10px;border:1px solid #ddd;">Email Address</th>
                    <th style="padding:10px;border:1px solid #ddd;">Malicious</th>
                    <th style="padding:10px;border:1px solid #ddd;">Phishing</th>
                    <th style="padding:10px;border:1px solid #ddd;">BEC</th>
                    <th style="padding:10px;border:1px solid #ddd;">Scam</th>
                </tr>
                {rows}
            </table>
        </div>
    </body>
    </html>
    """

    # Create multipart message
    msg = MIMEMultipart("alternative")
    msg['From'] = smtp_username
    msg['To'] = admin_email
    msg['Subject'] = f"{subject} - {today}"
    # Attach HTML instead of plain
    msg.attach(MIMEText(html_body, 'html'))
    # Send
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.sendmail(smtp_username, admin_email, msg.as_string())


# Function to obtain the token
def obtain_token(client_id, client_password, token_url, api_key):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "x-api-key": api_key,
    }
    data = {
        "grant_type": "client_credentials"
    }
    auth = (client_id, client_password)

    response = requests.post(token_url, headers=headers, data=data, auth=auth)

    if response.status_code == 200:
        response_json = response.json()
        print("Token obtained successfully:", response_json)
        token = response_json.get("accessToken") 
    #   token = response.json()["access_token"]
    #    print("Token obtained successfully:", token)
        return token
    else:
        print("Error obtaining token:", response.text)
        return None

def topTarget(token, report_top_url, api_key):

    # Get the current time
    current_time = datetime.datetime.utcnow()

    # Calculate the start time one day ago
    start_time = current_time - datetime.timedelta(days=1)

    # Format the timestamps
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    current_time_str = current_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Print the timestamps
    print("Start time:", start_time_str)
    print("Current time:", current_time_str)


    # Define the data payload
    data = {
        "timestamp": [
            start_time_str,
            current_time_str
        ],
        "reportType": "targets"
    }


    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "x-api-key": api_key,
    }

    # Send the POST request with the data payload
    response = requests.post(report_top_url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
#        print("Request was successful.")
#        print("Response:", response.json())
         return response.json()  # Return the JSON response
    else:
        print("Error:", response.text)



if __name__ == "__main__":


    # Obtain the token
    token = obtain_token(client_id, client_password, token_url, api_key)

  # Use the token to make a request
    if token:
  #   topTarget(token, report_top_url)
        top_target_output = topTarget(token, report_top_url, api_key)

        # Send email with the output
    if "error" not in top_target_output:
        print("Top Target Output:", top_target_output)
    
        try: 
            send_email('Top Target Report', json.dumps(top_target_output, indent=4))
            print("Email sent successfully to", admin_email)
        except Exception as e:
            print("Failed to send email.", e)
    else:
        try:
            send_email('Top Target Report - Error', top_target_output["error"])
            print("Error email sent successfully.")
        except Exception as e:
            print("Failed to send error email.", e)



