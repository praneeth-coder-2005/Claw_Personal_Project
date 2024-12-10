from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import logging
from queue import Queue

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = "7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk"

# Blogger Credentials
BLOGGER_EMAIL = "natureloverz2025@gmail.com"
BLOGGER_PASSWORD = "#5213680099Ac"  # Make sure to handle special characters if any

def update_code(update: telegram.Update, context: CallbackContext) -> None:
    try:
        # Get command arguments (post_url, new_code)
        post_url = context.args[0]
        new_code = " ".join(context.args[1:])  # Join remaining args for code

        # Start the web driver (use appropriate driver for your browser)
        driver = webdriver.Chrome()  # Or webdriver.Firefox(), etc.
        driver.get(post_url)  # Go directly to the post URL

        # Google Authentication (it should redirect to login if needed)
        try:  # Try to find the email field (in case already logged in)
            email_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
        except:  # If not found, assume already logged in
            pass  
        else:
            email_field.send_keys(BLOGGER_EMAIL)
            driver.find_element(By.ID, "identifierNext").click()

            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(BLOGGER_PASSWORD)
            driver.find_element(By.ID, "passwordNext").click()

            # (If you have 2FA, handle it here)
            # ... 

        # Switch to the iframe (if the editor is in an iframe)
        try:
            WebDriverWait(driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "postingIframe"))
            )
        except:
            pass  # If no iframe, continue

        # Locate the code block (adjust the selector if needed)
        code_block = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "pre code")) 
        )

        # Clear existing code and enter new code
        code_block.send_keys(Keys.CONTROL + "a")
        code_block.send_keys(Keys.DELETE)
        code_block.send_keys(new_code)

        # Switch back to the main content (if you switched to an iframe)
        try:
            driver.switch_to.default_content()
        except:
            pass

        # Save changes (if needed - inspect and find the "Update" button)
        # update_button = driver.find_element(...)
        # update_button.click()

        driver.quit()
        update.message.reply_text("Code updated successfully!")

    except Exception as e:
        update.message.reply_text(f"Error updating code: {e}")

def start(update: telegram.Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! I'm your Blogger code editor bot. "
                              "Use /update_code [post_url] [new_code] to update code.")

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token and update queue.
    update_queue = Queue()
    updater = Updater(TOKEN, update_queue=update_queue)  # Added update_queue

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("update_code", update_code))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
        
