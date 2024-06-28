import subprocess
import time
import os
from re import fullmatch
import pyautogui as pg
from pywhatkit.core import core, exceptions, log

pg.FAILSAFE = False

core.check_connection()

def open_whatsapp_microsoft_store():
    """Open WhatsApp installed from the Microsoft Store using PowerShell."""
    command = 'Start-Process "ms-windows-store://pdp/?productid=9nksqgp7f2nh"'
    subprocess.run(["powershell", "-Command", command])
    time.sleep(10)

    # After waiting for the page to load, we simulate clicking the 'Open' button
    # Adjust the coordinates according to your screen resolution
    pg.click(x=700, y=500)  # Example coordinates, adjust as needed

    # Return the path to WhatsApp
    return "WhatsApp"

def send_whatsapp_message(phone_no: str, message: str, wait_time: int = 20, tab_close: bool = False,
                          close_time: int = 1) -> None:
    """Send WhatsApp Message Instantly"""

    if not core.check_number(number=phone_no):
        raise exceptions.CountryCodeException("Country Code Missing in Phone Number!")

    phone_no = phone_no.replace(" ", "")
    if not fullmatch(r"^\+?[0-9]{2,4}\s?[0-9]{9,15}", phone_no):
        raise exceptions.InvalidPhoneNumber("Invalid Phone Number.")

    whatsapp_path = open_whatsapp_microsoft_store()
    if not whatsapp_path:
        print("WhatsApp not found in default paths.")
        return

    subprocess.Popen([whatsapp_path])  # Open WhatsApp desktop application
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

    log.log_message(_time=time.localtime(), receiver=phone_no, message=message)
    if tab_close:
        core.close_tab(wait_time=close_time)
