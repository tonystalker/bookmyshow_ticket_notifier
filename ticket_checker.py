import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler()  
    ]
)

load_dotenv()

def check_url_exists(url):
    """
    Comprehensively check URL accessibility with detailed error reporting.
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
    
    except Exception as e:
        logging.error(f"URL Check Error: {str(e)}")
        return {
            'exists': False,
            'error': 'Check Failed',
            'details': str(e),
            'is_accessible': False
        }

def send_whatsapp_message(url):
    """
    Send a WhatsApp message using Twilio when the URL is found.
    """
    try:
    
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        recipient_number = os.getenv('RECIPIENT_WHATSAPP_NUMBER')
        
    
        if not all([account_sid, auth_token, recipient_number]):
            logging.error("Missing Twilio credentials.")
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

def main():
    """
    Main function to continuously check URL and send notification.
    Adapted for Railway's always-on environment.
    """

    url = "https://in.bookmyshow.com/sports/lucknow-super-giants-vs-mumbai-indians/ET00434749"
    
    
    check_interval = int(os.getenv('CHECK_INTERVAL', 600))
    
    logging.info(f"Ticket Checker Started. Checking URL: {url}")
    logging.info(f"Check Interval: {check_interval} seconds")
    
    while True:
        try:
            logging.info("Performing URL check...")
            check_result = check_url_exists(url)
            
            
            logging.info("URL Check Results:")
            for key, value in check_result.items():
                logging.info(f"{key.replace('_', ' ').title()}: {value}")
            
            
            if check_result['is_accessible']:
                send_whatsapp_message(url)
            
            
            time.sleep(check_interval)
        
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {str(e)}")
            
            time.sleep(check_interval)

if __name__ == '__main__':
    main()