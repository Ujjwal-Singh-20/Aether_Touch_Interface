import customtkinter as ctk
from tkinter import StringVar, Toplevel
import pyautogui
import os
import requests  # For making API calls
import cv2
import threading
import time
import math
from Hand_Detection import HandDetection  
import webbrowser
import json
from Virtual_Cursor import VirtualCursor
from Gesture_Volume_Control import GestureVolumeControl

# Setting custom tkinter appearance and color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Defining colors
BG_COLOR = "#1E1E2F"
MENU_COLOR = "#24243e"
TEXT_COLOR = "#D1D2E5"



# Dropdown options
OPTIONS = ["None", "Show Weather", "Open Calculator", "Open Notepad", "Minimize All Windows"]

# Loading saved shortcuts from JSON on startup
def load_shortcuts():
    if os.path.exists("shortcuts.json"):
        with open("shortcuts.json", "r") as f:
            shortcuts = json.load(f)
            for name, address in shortcuts.items():
                OPTIONS.append(name)
load_shortcuts()


# OpenWeatherMap API key
API_KEY = os.getenv("OPENWEATHER_API_KEY")   #or directly update with your API key(as a string in ""), for local testing
# API_KEY = "b6f7acd547c8efbfe45433be6efe1fb1"   #for direct usage, uncomment this line, and comment out the above line

if not API_KEY:
    print("Error: API key is not set. Please visit OpenWeather and generate your own API key.")
    print("Set it as an environment variable or update the code with your key.")
    exit()


action_map = {
    "Show Weather": lambda app: app.toggle_weather_window(),
    "Open Calculator": lambda app: app.toggle_calculator(),
    "Open Notepad": lambda app: app.toggle_notepad(),
    "Minimize All Windows": lambda app: pyautogui.hotkey("win", "d") if os.name == "nt" else pyautogui.hotkey("command", "f3"),
}

# Gesture-to-action map: stores selected actions for each gesture
gesture_to_action = {
    "Point Up": "None",
    "Point Left": "None",
    "Point Right": "None",
    "Fist": "Minimize All Windows",
}

class AetherTouchInterface:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")
        self.root.title("Smart Hand-Tracking Mirror")
        self.root.configure(bg=BG_COLOR)

        # Initialize selected functions for each gesture
        self.selected_functions = {
            "Point Up": StringVar(value="None"),
            "Point Left": StringVar(value="None"),
            "Point Right": StringVar(value="None"),
            "Fist": StringVar(value="Minimize All Windows"),
        }

        # Initialize flags to track if Notepad and Calculator are open
        self.notepad_open = False
        self.calculator_open = False

        # Create the sidebar and main content frame
        self.create_left_sidebar()
        self.create_right_sidebar()

        # Video capture setup
        self.video_capture = cv2.VideoCapture(0)
        self.weather_window = None

        # Initialize hand detector
        self.hand_detector = HandDetection()

        # Start gesture detection in a separate thread
        threading.Thread(target=self.detect_gestures, daemon=True).start()


    def toggle_virtual_cursor(self):
        if hasattr(self, "cursor_window") and self.cursor_window.winfo_exists():
            self.cursor_window.destroy()
            self.cursor_active = False
            self.video_capture = cv2.VideoCapture(0)  # Re-initialize video capture for gesture detection
            threading.Thread(target=self.detect_gestures, daemon=True).start()   #restart gesture detection feed

        else:
            self.cursor_active = True
            self.video_capture.release()  # Release video capture to avoid conflict with virtual cursor feed
            self.video_capture = cv2.VideoCapture(0)  # Re-initialize video capture for virtual cursor
            self.show_virtual_cursor_window()

    def show_virtual_cursor_window(self):
        
        self.cursor_window = Toplevel(self.root)
        self.cursor_window.title("Virtual Cursor")
        self.cursor_window.geometry("640x480")

        #starting virtual cursor feed in new thread
        threading.Thread(target=self.run_virtual_cursor_feed, daemon=True).start()

    def run_virtual_cursor_feed(self):
        virtual_cursor = VirtualCursor()
        cap = cv2.VideoCapture(0)

        while self.cursor_active:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame, _ = virtual_cursor.find_hand_landmarks(frame)
            frame = cv2.flip(frame, 1)  # Invert the frame horizontally

            cv2.imshow("Virtual Cursor Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


    def toggle_gesture_volume_control(self):
        if hasattr(self, "volume_control_window") and self.volume_control_window.winfo_exists():
            self.video_capture.release()
            self.video_capture = cv2.VideoCapture(0)
            self.volume_control_active = False
            threading.Thread(target=self.detect_gestures, daemon=True).start()
        else:
            self.volume_control_active = True
            self.video_capture.release()
            self.video_capture = cv2.VideoCapture(0)
            self.show_volume_control_window()
            volume_control = GestureVolumeControl()
            volume_control.start_control( self.volume_control_window, cap=self.video_capture)

    def show_volume_control_window(self):
        self.volume_control_window = Toplevel(self.root)
        self.volume_control_window.title("Gesture Volume Control")
        self.volume_control_window.geometry("300x100")
        self.volume_control_window.configure(bg=BG_COLOR)
        self.volume_control_window.attributes("-topmost", True)  # Keep window on top

        label = ctk.CTkLabel(self.volume_control_window, text="Gesture Volume Control Active", text_color=TEXT_COLOR, font=("Arial Rounded MT Bold", 16))
        label.pack(pady=20)

    
        
    def add_shortcut(self):
        """Open a two-step window to add a new shortcut name and address."""
        # First window for the shortcut name
        name_window = Toplevel(self.root)
        name_window.title("Enter Shortcut Name")
        name_window.geometry("400x100")
        name_var = StringVar()
        
        name_label = ctk.CTkLabel(name_window, text="Shortcut Name:", text_color="black", font=("Arial Rounded MT Bold", 14))
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(name_window, textvariable=name_var)
        name_entry.pack(pady=5)

        name_entry.bind("<Return>", lambda event: proceed_to_address())
        
        def proceed_to_address():
            name = name_var.get().strip()
            if name:
                name_window.destroy()  # Close name window
                
                # Second window for the shortcut address
                address_window = Toplevel(self.root)
                address_window.title("Enter Shortcut Address")
                address_window.geometry("300x100")
                address_var = StringVar()
                
                address_label = ctk.CTkLabel(address_window, text="Shortcut Address:", text_color="black", font=("Arial Rounded MT Bold", 14))
                address_label.pack(pady=5)
                address_entry = ctk.CTkEntry(address_window, textvariable=address_var)
                address_entry.pack(pady=5)

                address_entry.bind("<Return>", lambda event: save_shortcut())

                
                def save_shortcut():
                    address = address_var.get().strip()
                    if address:
                        OPTIONS.append(name)  # Add to OPTIONS
                        gesture_to_action[name] = "None"  # Add to action map
                        
                        # Save to JSON
                        if os.path.exists("shortcuts.json"):
                            with open("shortcuts.json", "r") as f:
                                shortcuts = json.load(f)
                        else:
                            shortcuts = {}
                        
                        shortcuts[name] = address
                        with open("shortcuts.json", "w") as f:
                            json.dump(shortcuts, f)


                        # Update dropdown options and reset dropdowns
                        for var in self.selected_functions.values():
                            var.set("None")
                        for widget in self.menu_frame.winfo_children():
                            if isinstance(widget, ctk.CTkOptionMenu):
                                widget.configure(values=OPTIONS)
                        

                        address_window.destroy()

                save_button = ctk.CTkButton(address_window, text="Save", command=save_shortcut)
                save_button.pack(pady=10)

        proceed_button = ctk.CTkButton(name_window, text="Proceed", command=proceed_to_address)
        proceed_button.pack(pady=10)


    def create_left_sidebar(self):
        """Create the left sidebar with gesture options and dropdowns."""
        self.menu_frame = ctk.CTkFrame(self.root, width=int(self.root.winfo_width() * 0.25), height=int(self.root.winfo_height() * 1), fg_color=MENU_COLOR)
        self.menu_frame.pack(side="left", fill="y")

        menu_title = ctk.CTkLabel(self.menu_frame, text="Gesture Control", text_color=TEXT_COLOR, font=("OCR A Extended", 16, "bold"))
        menu_title.pack(pady=20)

        add_shortcut_button = ctk.CTkButton(self.menu_frame, text="Add Shortcut", command=self.add_shortcut, font=("Arial Black", 14, "bold"))
        add_shortcut_button.pack(pady=10)

        cursor_button = ctk.CTkButton(self.menu_frame, text="Toggle Virtual Cursor", command = self.toggle_virtual_cursor, font=("Arial Black", 14, "bold"))
        cursor_button.pack(pady=10)


        # Create dropdowns for each gesture
        for gesture, var in self.selected_functions.items():
            label = ctk.CTkLabel(self.menu_frame, text=gesture, text_color=TEXT_COLOR, font=("Copperplate Gothic Bold", 16, "bold"))
            label.pack(pady=(10, 5))
            dropdown = ctk.CTkOptionMenu(self.menu_frame, variable=var, values=OPTIONS, fg_color=MENU_COLOR, font=("Consolas", 12), button_hover_color="#1F1F3F")
            dropdown.pack(pady=(0, 10))
            var.trace("w", lambda *args, gesture=gesture, var=var: self.update_action(gesture, var.get()))

    def create_right_sidebar(self):
        """Right sidebar with usage instructions."""
        self.info_frame = ctk.CTkFrame(self.root, width=int(self.root.winfo_width() * 0.75), height=int(self.root.winfo_width() * 1), fg_color=MENU_COLOR, border_color=MENU_COLOR)
        self.info_frame.pack(side="right", expand=True, fill="both")


        # Heading Label
        content_label = ctk.CTkLabel(
            self.info_frame,
            text="Aether Touch Interface",
            font=("Bauhaus 93", 44, "bold", "underline"),
            text_color=TEXT_COLOR,
        )
        content_label.place(relx=0.5, rely=0, anchor="n")

        # Title for the instructions
        info_title = ctk.CTkLabel(self.info_frame, text="How to Use", text_color=TEXT_COLOR, font=("Arial Rounded MT Bold", 36, "bold"))
        info_title.pack(pady=(60, 20))


        # Usage instructions text
        instructions = (
            "Gestures:\n"
            "  - Point Up: Select the associated action from the dropdown.\n"
            "  - Point Left: Select the associated action from the dropdown.\n"
            "  - Point Right: Select the associated action from the dropdown.\n"
            "  - Fist: Defaults to minimizing all windows.\n\n"
            "Adding Shortcuts:\n"
            "  - Click 'Add Shortcut' in the left sidebar.\n"
            "  - Provide a name and address (URL or file path).\n\n"
            "Virtual Cursor:\n"
            "  - Toggle the Virtual Cursor for mouse control.\n"
            "  - Use hand gestures to control the cursor:\n"
            "    - Move Cursor: Point with your index finger.\n"
            "    - Left Click: Touch the middle finger tip and thumb tip together briefly.\n"
            "    - Right Click: Touch the ring finger tip and thumb tip together briefly.\n"
            "    - Scroll: Touch the index finger tip and thumb tip, hold and move up/down.\n\n"
            "Weather Information:\n"
            "  - Select 'Show Weather' in the dropdown.\n"
            "  - A popup with your local weather will appear, when the associated gesture is performed.\n\n"
            "Applications:\n"
            "  - Choose 'Open Calculator' or 'Open Notepad' from dropdowns."
            "  - A popup with the application will appear, when the associated gesture is performed.\n\n"
        )

        # Adding the instructions text to a CTkTextbox
        info_textbox = ctk.CTkTextbox(self.info_frame, fg_color=BG_COLOR, text_color=TEXT_COLOR, border_color=MENU_COLOR, font=("Courier New", 18, "bold"), wrap="word")
        info_textbox.insert("1.0", instructions)
        info_textbox.configure(state="disabled")
        info_textbox.pack(padx=10, pady=10, expand=True, fill="both")


    def create_dropdown(self, parent, label_text, var):
        """Create a dropdown menu for a gesture selection."""
        label = ctk.CTkLabel(parent, text=label_text, text_color=TEXT_COLOR)
        label.pack(pady=(20, 5))
        
        dropdown = ctk.CTkOptionMenu(parent, variable=var, values=OPTIONS, fg_color=MENU_COLOR)
        dropdown.pack()

        # Update the gesture_to_action map when a dropdown option is changed
        var.trace("w", lambda *args, gesture=label_text, var=var: self.update_action(gesture, var.get()))

    def show_notification(self, message):
        """Show a notification message."""
        notification = Toplevel(self.root)
        notification.title("Notification")
        notification.geometry("500x100")
        notification.configure(bg=BG_COLOR)
        notification.attributes("-topmost", True)

        label = ctk.CTkLabel(notification, text=message, text_color=TEXT_COLOR, font=("Arial Rounded MT Bold", 16))
        label.pack(pady=20)

        # Automatically close the notification after 3 seconds
        notification.after(3000, notification.destroy)

    def update_action(self, gesture, action):
        """Update the gesture-to-action mapping when a dropdown option is changed."""
        gesture_to_action[gesture] = action

        

    def toggle_weather_window(self):
        """Toggle the weather display window."""
        if self.weather_window is None or not self.weather_window.winfo_exists():
            self.show_weather_window()  # Show the weather window
        else:
            self.weather_window.destroy()  # Close the weather window
            self.weather_window = None
            time.sleep(1)  # Delay to prevent immediate re-detection

    def show_weather_window(self):
        """Create and display the weather window."""
        # Fetch weather data
        weather_info = self.fetch_weather()

        # Create the Toplevel window (always on top)
        self.weather_window = Toplevel(self.root)
        self.weather_window.title("Weather Info")
        self.weather_window.geometry("300x200")
        self.weather_window.attributes("-topmost", True)
        self.weather_window.configure(bg=BG_COLOR)

        # Add weather information to the window
        weather_label = ctk.CTkLabel(self.weather_window, text=weather_info, text_color=TEXT_COLOR, font=("Arial", 14))
        weather_label.pack(pady=20)

    def get_user_city(self):
        """Fetch the user's city based on their IP address."""
        try:
            response = requests.get('https://ipinfo.io')
            data = response.json()
            city = data.get('city', 'Unknown City')
            return city
        except Exception as e:
            print(f"Error fetching city: {e}")
            return "Unknown City"

    def fetch_weather(self):
        """Fetch weather information from OpenWeatherMap."""
        city = self.get_user_city()
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            weather_info = f"City: {city}\nTemperature: {temp}°C\nDescription: {description.capitalize()}"
        else:
            weather_info = "Error fetching weather data"

        return weather_info



    def detect_gesture(self, lmlist):
        """Detect gestures based on the angle between the index finger tip and wrist."""

        while not getattr(self, 'cursor_active', False):  # Only run if cursor isn't active
            ret, frame = self.video_capture.read()

            gesture = None

            index_tip = lmlist[8]
            middle_tip = lmlist[12]
            ring_tip = lmlist[16]
            pinky_tip = lmlist[20]
            wrist = lmlist[0]
            thumb_tip = lmlist[4]
            
            # Calculate the length from wrist to middle finger tip
            length = math.hypot(middle_tip[0] - wrist[0], middle_tip[1] - wrist[1])
            
            # Approximate the width as half of the length
            width = length / 2
            
            # Approximate the hand area as a rectangle
            area = length * width
            

            # Calculate the angle in degrees
            x_diff = index_tip[0] - wrist[0]
            y_diff = index_tip[1] - wrist[1]
            angle = math.degrees(math.atan2(-y_diff, x_diff)) % 360  # Invert y_diff for screen coordinates

            # Detect gesture based on angle ranges
            if (330 <= angle or angle < 45) and thumb_tip[1] < index_tip[1]:
                gesture = "Point Left"
            elif 45 <= angle < 135 and not GestureVolumeControl.is_desired_shape(self, lmlist):
                gesture = "Point Up"
            elif 135 <= angle < 210 and thumb_tip[1] < index_tip[1]:
                gesture = "Point Right"
            

            # Fist detection: Check if all four fingertips are close to each other
            fist_threshold = 50  # Distance threshold for fingertips to be close
            fingertips_close = (
                math.dist(index_tip, middle_tip) < fist_threshold and
                math.dist(index_tip, ring_tip) < fist_threshold and
                math.dist(index_tip, pinky_tip) < fist_threshold and
                math.dist(middle_tip, ring_tip) < fist_threshold and
                math.dist(middle_tip, pinky_tip) < fist_threshold and
                math.dist(ring_tip, pinky_tip) < fist_threshold
            )

            # Check if the fingertips are close to the wrist to confirm a fist
            wrist_threshold = 40  # Distance threshold for fingertips to be close to the wrist
            fingertips_to_wrist_close = (
                math.dist(index_tip, wrist) < wrist_threshold and
                math.dist(middle_tip, wrist) < wrist_threshold and
                math.dist(ring_tip, wrist) < wrist_threshold and
                math.dist(pinky_tip, wrist) < wrist_threshold and
                math.dist(thumb_tip, wrist) < wrist_threshold  
            )

            if fingertips_close or fingertips_to_wrist_close:
                gesture = "Fist"

            return gesture


    def detect_gestures(self):
        """Continuously detect gestures and execute corresponding actions."""
        while True:
            ret, frame = self.video_capture.read()
            if ret:
                lmlist, bbox = self.hand_detector.detect_hands(frame)  # Get landmarks from hand detection
                if lmlist:  # If landmarks are detected
                    time.sleep(1)

                    index_tip_x, index_tip_y = lmlist[8][0], lmlist[8][1]
                    middle_tip_x, middle_tip_y = lmlist[12][0], lmlist[12][1]
                    ring_tip_x, ring_tip_y = lmlist[16][0], lmlist[16][1]
                    wrist = lmlist[0]

                    #calculate distance between index, middle and ring finger
                    distance_index_middle = math.hypot(middle_tip_x - index_tip_x, middle_tip_y - index_tip_y)
                    distance_middle_ring = math.hypot(ring_tip_x - middle_tip_x, ring_tip_y - middle_tip_y)

                    # Calculate the length from wrist to middle finger tip
                    length = math.hypot(middle_tip_x - wrist[0], middle_tip_y - wrist[1])
                    
                    # Approximate the width as half of the length
                    width = length / 2
                    
                    # Approximate the hand area as a rectangle
                    area = length * width

                    #check if distance is less than threshold
                    if GestureVolumeControl.is_desired_shape(self, lmlist):
                        self.toggle_gesture_volume_control()

                    elif GestureVolumeControl.is_desired_shape(self, lmlist):
                        self.toggle_gesture_volume_control()
                        time.sleep(1)

                    gesture = self.detect_gesture(lmlist)  # Detect the gesture

                    if gesture:
                        self.start_countdown(gesture)  # Start countdown for the detected gesture
                        time.sleep(1)  # Add a delay to prevent immediate re-detection
                else:
                    print("No hands detected.")
            else:
                print("Failed to capture frame.")
            
            time.sleep(0.1)  # Small delay to reduce CPU usage

    def start_countdown(self, gesture):
        """Start a 3-second countdown in a separate window."""
        self.countdown_window = Toplevel(self.root)
        self.countdown_window.title(f"Countdown Timer {gesture}")
        self.countdown_window.geometry("500x100")
        self.countdown_window.configure(bg="#0598ce")
        self.countdown_window.attributes("-topmost", True)

        # Create a label to show countdown
        countdown_label = ctk.CTkLabel(self.countdown_window, text=f"Countdown for {gesture}: 3", text_color=TEXT_COLOR, font=("Arial", 24))
        countdown_label.pack(pady=20)

        if gesture != "Fist":
            for i in range(3):
                self.countdown_window.after(i * 1000, lambda x=i: countdown_label.configure(text=f"Countdown for {gesture}: {3 - x}"))  # Update countdown text

            # After countdown, clear the gauge and execute the action
            self.countdown_window.after(3000, lambda: self.execute_gesture_action(gesture))  # Execute action after countdown
            self.countdown_window.after(3000, self.countdown_window.destroy)  # Destroy countdown window after 3 seconds
            
        else:
            self.countdown_window.after(500, countdown_label.configure(text=f"Quick action for {gesture}"))
            self.countdown_window.after(500, lambda: self.execute_gesture_action(gesture))  # Execute action after countdown
            self.countdown_window.after(500, self.countdown_window.destroy)


    def execute_gesture_action(self, gesture):
        action = gesture_to_action.get(gesture)
        if action:
            if action in action_map:
                print(f"Executing action for {gesture}: {action}")
                action_map[action](self)
            elif action in OPTIONS:
                with open("shortcuts.json", "r") as f:
                    shortcuts = json.load(f)
                address = shortcuts.get(action)
                if address:
                    # Check if the address is a URL or file path
                    if address.startswith("http://") or address.startswith("https://"):
                        webbrowser.open(address)  # Open URL in the browser
                    elif os.path.exists(address):
                        os.startfile(address)  # Open local file
                    else:
                        print(f"Invalid shortcut address: {address}")


    # Toggle methods for Notepad and Calculator applications
    def toggle_notepad(self):
        """Toggle the Notepad application."""
        if self.notepad_open:
            pyautogui.hotkey("alt", "f4")  # Close Notepad
            self.notepad_open = False
            print("Notepad closed.")
        else:
            time.sleep(1)  # Add a delay to prevent immediate re-opening
            os.system("notepad")  # Open Notepad
            self.notepad_open = True
            print("Notepad opened.")

    def toggle_calculator(self):
        """Toggle the Calculator application."""
        if self.calculator_open:
            pyautogui.hotkey("alt", "f4")
            print("Calculator closed.")
        else:
            time.sleep(1)  # Add a delay to prevent immediate re-opening
            os.system("calc")  # Open Calculator
            self.calculator_open = True
            print("Calculator opened.")



if __name__ == "__main__":

    root = ctk.CTk()  # Create main CTk window

    app = AetherTouchInterface(root)  # Create instance of SmartMirrorApp
    
    root.mainloop()  # Start the Tkinter event loop
