from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Telegram Bot Token (replace with your actual token)
TOKEN = "7805737766:AAEAOEQAHNLNqrT0D7BAeAN_x8a-RDVnnlk"

# Blogger Credentials (replace with your actual credentials)
BLOGGER_EMAIL = "your_blogger_email@example.com"
BLOGGER_PASSWORD = "your_blogger_password"

def update_code(update, context):
    try:
        # Get command arguments (post_url, new_code)
        post_url = context.args[0]
        new_code = " ".join(context.args[1:])  # Join remaining args for code

        # Start the web driver (use appropriate driver for your browser)
        driver = webdriver.Chrome()
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
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "postingIframe")))
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

def start(update, context):
    update.message.reply_text("Hello! I'm your Blogger code editor bot. "
                              "Use /update_code [post_url] [new_code] to update code.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("update_code", update_code))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
            
