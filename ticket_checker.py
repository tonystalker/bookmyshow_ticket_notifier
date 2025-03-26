import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv
import schedule
import time
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('ticket_checker.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()

def check_url_exists(url):
    """
    Comprehensively check URL accessibility with detailed error reporting.
    
    Args:
        url (str): The URL to check
    
    Returns:
        dict: A dictionary containing check results
    """
    try:
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        accessible_codes = [200, 201, 203, 204, 403]
        
        return {
            'exists': response.status_code in accessible_codes,
            'status_code': response.status_code,
            'reason': response.reason,
            'is_accessible': response.status_code in accessible_codes
        }
    
    except requests.exceptions.ConnectionError:
        logging.error("Connection Error: Unable to connect to the server.")
        return {
            'exists': False,
            'error': 'Connection Error',
            'details': 'Unable to connect to the server. Check network or URL.',
            'is_accessible': False
        }
    
    except requests.exceptions.Timeout:
        logging.error("Timeout Error: The request timed out.")
        return {
            'exists': False,
            'error': 'Timeout Error',
            'details': 'The request timed out. The server might be slow or unreachable.',
            'is_accessible': False
        }
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Request Exception: {str(e)}")
        return {
            'exists': False,
            'error': 'Request Exception',
            'details': str(e),
            'is_accessible': False
        }

def send_whatsapp_message(url):
    """
    Send a WhatsApp message using Twilio when the URL is found.
    
    Args:
        url (str): The URL of the ticket
    """
    try:
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        recipient_number = os.getenv('RECIPIENT_WHATSAPP_NUMBER')
        
        if not all([account_sid, auth_token, recipient_number]):
            logging.error("Missing Twilio credentials. Check your .env file.")
            return
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=f"🎉 Ticket Available! Quick, book now at: {url}",
            from_=twilio_whatsapp_number,
            to=recipient_number
        )
        
        logging.info(f"WhatsApp message sent. SID: {message.sid}")
    
    except Exception as e:
        logging.error(f"Failed to send WhatsApp message: {str(e)}")

def check_and_notify():
    """
    Main function to check URL and send notification if available.
    """
    url = os.getenv('TARGET_URL', 'https://in.bookmyshow.com/sports/lucknow-super-giants-vs-chennai-super-kings/ET00434751')
    
    logging.info(f"Checking URL: {url}")
    
    check_result = check_url_exists(url)
    logging.info("URL Check Results:")
    for key, value in check_result.items():
        logging.info(f"{key.replace('_', ' ').title()}: {value}")
    
    if check_result['is_accessible']:
        send_whatsapp_message(url)

def main():
    schedule.every(10).minutes.do(check_and_notify)
    
    logging.info("Ticket Checker started. Checking every 10 minutes.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()