import subprocess
import win32gui
import time
import webbrowser as web
from re import fullmatch
import pyautogui as pg
from pywhatkit.core import core, exceptions, log

pg.FAILSAFE = False

core.check_connection()


def get_default_browser():
    command = 'powershell -Command "$defaultBrowser = (Get-ItemProperty \'HKCU:\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice\').ProgId; echo $defaultBrowser"'
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)

    if result.returncode != 0:
        print("Error executing PowerShell command:")
        print(result.stderr.strip())
        return None

    output = result.stdout.strip()
    return output


def set_frontmost_process(browser_name):
    if browser_name.lower() == 'microsoft edge':
        # For Microsoft Edge, let's try a different approach to bring it to the foreground
        subprocess.run('start microsoft-edge:', shell=True)
        return

    # Find the window handle of the application
    handle = win32gui.FindWindow(None, browser_name)

    if handle == 0:
        print(f"Error: {browser_name} window not found.")
        return

    # Bring the window to the foreground
    win32gui.SetForegroundWindow(handle)


def sendwhatmsg_instantly(
        phone_no: str,
        message: str,
        wait_time: int = 10,
        tab_close: bool = False,
        close_time: int = 1,
) -> None:
    """Send WhatsApp Message Instantly"""

    if not core.check_number(number=phone_no):
        raise exceptions.CountryCodeException("Country Code Missing in Phone Number!")

    phone_no = phone_no.replace(" ", "")
    if not fullmatch(r"^\+?[0-9]{2,4}\s?[0-9]{9,15}", phone_no):
        raise exceptions.InvalidPhoneNumber("Invalid Phone Number.")

    web.open(f"https://web.whatsapp.com/send?phone={phone_no}")
    time.sleep(wait_time)

    index = 0
    length = len(message)
    while index < length:
        letter = message[index]
        pg.write(letter)
        if letter == ":":
            index += 1
            while index < length:
                letter = message[index]
                if letter == ":":
                    pg.press("enter")
                    break
                pg.write(letter)
                index += 1
        index += 1

    default_browser = get_default_browser()
    if default_browser != "Unknown":
        # Set the frontmost process to the default browser
        set_frontmost_process(default_browser)
    else:
        print("Set your default browser to Chrome, Firefox, Microsoft Edge, or Brave to use this feature.")

    # Press enter to send the message
    pg.press('enter')

    log.log_message(_time=time.localtime(), receiver=phone_no, message=message)
    if tab_close:
        core.close_tab(wait_time=close_time)



