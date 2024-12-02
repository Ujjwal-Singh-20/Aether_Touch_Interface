# Aether Touch Interface

Welcome to **Aether Touch Interface** – an innovative and intuitive smart control system that merges technology and creativity. Aether Touch allows you to interact with your computer using gesture-based controls, powered by advanced gesture tracking and virtual cursor control, Aether Touch transforms the way you interact with your digital environment. Whether you're navigating through applications, controlling volume, or managing shortcuts, Aether Touch makes everything more efficient and intuitive. Perfect for those seeking convenience without compromising sophistication.

---

## Features

- **Gesture Control Setup**:  
   Assign specific actions to gestures before performing them. Configure actions for gestures like **Point Up**, **Point Left**, **Point Right**, and more.

- **Virtual Cursor**:  
   Navigate your screen with hand gestures:  
   - **Scroll**: Join **thumb tip** and **index tip**, and move vertically.  
   - **Left Click**: Join **middle finger tip** and **thumb tip** briefly.  
   - **Right Click**: Join **ring finger tip** and **thumb tip** briefly.  
   A seamless way to control your computer without touching the mouse.

- **Volume Control**:  
   Control your system volume with a simple and distinct gesture flow:  
   - **Activate Volume Control**: Show three fingers (**index**, **middle**, **ring**) with tips joined and hold for a second.  
   - **Adjust Volume**: Join **index** and **middle finger tips**, then move vertically to increase or decrease the volume. Ensure tips remain apart to stop adjustments.  
   - **Deactivate Volume Control**: Show the three-finger gesture again and hold for a second.

- **Add Shortcuts**:  
   Quickly create and configure custom shortcuts for apps, files, or URLs.

- **Real-Time Weather Updates**:  
   View your local weather directly from the interface.

- **JSON Storage**:  
   All settings, preferences, and shortcuts are securely saved in a JSON file for effortless management.

---

## Setup API Key

To use the weather-related features of the app, you need to set up your own OpenWeather API key. Follow the steps below to get your API key and integrate it with the project:

### Steps to Setup API Key:
1. **Create an OpenWeather account**:
   - Go to [OpenWeather](https://openweathermap.org/) and sign up for an account.

2. **Generate your API Key**:
   - After logging in, go to the [API Keys section](https://home.openweathermap.org/api_keys).
   - Click on "Create Key" to generate your personal API key.

3. **Store the API Key securely**:
   - For security reasons, it is highly recommended that you do **not** expose your API key directly in the code.
   - Instead, store the key in an environment variable or in a `.env` file.

4. **Add the API Key to Your Project**:
   - In your project directory, create a `.env` file (if not already present).
   - Add the following line to your `.env` file, replacing `your_api_key_here` with your actual OpenWeather API key:
     ```
     OPENWEATHER_API_KEY=your_api_key_here
     ```

5. **Use the API Key in the Project**:
   - The app will automatically load your API key from the `.env` file and use it to fetch weather data.
   
6. **Alternative Method (Direct Code Integration)**:
   - If you're not using `.env` files, you can directly replace the `OPENWEATHER_API_KEY` variable in the code with your API key (though this method is not recommended for security reasons).

### Important Notes:
- **Do not expose your API key publicly**: Make sure your `.env` file is listed in your `.gitignore` to avoid accidentally committing it to a public repository.
- **Monitor your API usage**: OpenWeather API has usage limits depending on your plan. Be sure to keep track of your requests to avoid exceeding your limits.

---

## Requirements

Ensure you have the following dependencies installed:

customtkinter pyautogui requests opencv-python mediapipe numpy


To install them, use:

```bash
pip install -r requirements.txt
```

---

## How to Use

1. **Launch the Application**: Run the main file to start the Aether Touch Interface.
2. **Set Up Gesture Actions**:  
   Assign desired actions to gestures from the interface before performing gestures.  
3. **Activate Virtual Cursor**:  
   Enable the cursor and control your computer effortlessly using hand gestures (as described below):  
   - **Scroll**: Join **thumb tip** and **index tip**, and move vertically.  
   - **Left Click**: Join **middle finger tip** and **thumb tip** briefly.  
   - **Right Click**: Join **ring finger tip** and **thumb tip** briefly.  
4. **Control Volume**:  
   - **Activate Volume Control**: Show three fingers (**index**, **middle**, **ring**) with tips joined and hold for a second.  
   - **Adjust Volume**: Join **index** and **middle finger tips**, then move vertically to increase or decrease the volume. Ensure tips remain apart to stop adjustments.  
   - **Deactivate Volume Control**: Show the three-finger gesture again and hold for a second.  
5. **Add and Use Shortcuts**:  
   Use the left sidebar to configure and use shortcuts for quick access to apps and files.  
6. **Enjoy**: Explore the features and embrace the future of touchless interaction.

---

## Contributions

Contributions are greatly appreciated! Fork the repository, propose new features, fix bugs, or enhance documentation. Let's innovate together.

---

## License

This project is licensed under the MIT License – see the [LICENSE](https://opensource.org/license/mit) file for details.

---
