import keyboard
import threading
import requests
from PIL import ImageGrab
from win10toast import ToastNotifier
import base64
from io import BytesIO
import tkinter as tk

# Configuration
API_KEY = "Add you Gemini API" # Replace with your actual API key
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

toaster = ToastNotifier()

def capture_screen():
    screenshot = ImageGrab.grab()
    width, height = screenshot.size

    # Estimate taskbar and header sizes
    header_height = 40   # top bar
    footer_height = 40   # bottom taskbar

    cropped = screenshot.crop((0, header_height, width, height - footer_height))
    return cropped

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def ask_ai_with_image(base64_image):
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": base64_image
                        }
                    },
                    {
                        "text": "Solve the question in the image and provide only the final answer."
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    try:
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except (KeyError, IndexError):
        return "No valid response received from Gemini AI."

def process_flow():
    try:
        image = capture_screen()
        base64_img = image_to_base64(image)
        answer = ask_ai_with_image(base64_img)
        print("Gemini:", answer)
        show_custom_overlay(answer)
    except Exception as e:
        print("Error:", e)

def show_custom_overlay(message):
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(background='black')

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    width, height = 400, 100
    x = (screen_width // 2) - (width // 2)
    y = 50  # top center

    root.geometry(f"{width}x{height}+{x}+{y}")
    label = tk.Label(root, text=message, bg="black", fg="white", font=("Segoe UI", 14), wraplength=380)
    label.pack(expand=True, fill='both')

    def close_overlay():
        root.destroy()

    root.after(8000, close_overlay)  # Auto-close after 8 seconds
    root.mainloop()

def listen_shortcut():
    keyboard.add_hotkey("ctrl+shift+q", lambda: threading.Thread(target=process_flow).start())
    print("Listening for Ctrl+Shift+Q...")
    keyboard.wait()

if __name__ == "__main__":
    listen_shortcut()
