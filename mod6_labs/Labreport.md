Laboratory Report: Weather Application Development

Course: CCCS 106

Section: BSCS 3A

Module: 6

Student Information:

Name: Sean Xander B. Aquino


1. Project Overview

This report documents the development of a cross-platform Weather Application built using Python and the Flet framework (Flutter for Python). The application interfaces with the OpenWeatherMap API to fetch real-time meteorological data.

The primary objective was to create a responsive, modern user interface that not only displays standard weather metrics (temperature, humidity, wind speed) but also provides an immersive user experience through dynamic visual feedback and persistent state management.

2. Technical Implementation

The application was constructed using the following technologies:

Frontend/UI: Flet (Python wrapper for Flutter controls) using Material Design principles.

Backend Logic: Python for data processing and API handling.

Data Source: OpenWeatherMap API (JSON response parsing).

State Management: page.client_storage for persistent user preferences.

3. Key Features & Functional Analysis

3.1 Base Functionality

The core module of the application ensures essential utility:

City Search: Allows users to query weather data for global locations.

Current Metrics: Displays temperature, relative humidity, and wind speed.

Visual Feedback: Dynamic fetching of weather icons corresponding to API condition codes.

Error Handling: Robust try-except blocks to manage invalid city names or network timeouts.

3.2 Enhanced Features

A. Dynamic Theme Toggle (Light/Dark Mode)

Objective: To improve accessibility and visual comfort across different lighting environments.

Implementation: A toggle switch allows users to alternate between light and dark themes.

Technical Insight: The application logic required detecting the initial system state to prevent "flashbanging" the user. The state is managed carefully to ensure that text contrast and icon visibility remain high regardless of the selected theme.

B. Unit Conversion (Metric/Imperial)

Objective: To enhance usability for international users accustomed to different measurement systems (Celsius vs. Fahrenheit).

Implementation: A boolean state controls the display logic.

Technical Insight: A dedicated conversion function was implemented outside the main display loop. This solved a critical bug where auto-refreshing the data caused the conversion logic to run recursively, leading to incorrect values.

C. Search History Persistence

Objective: To reduce user friction by providing quick access to frequently queried locations.

Implementation: Utilizes browser-level local storage to save a list of the last 5 searched cities.

Technical Insight: The challenge was managing storage limitations and serialization. The solution involves a FIFO (First-In-First-Out) stack that updates client_storage without impacting app startup performance.

D. Geolocation & Preload

Objective: To provide an instant, personalized "at-a-glance" experience upon application launch.

Implementation: The app utilizes the Geolocation API to fetch coordinates on load.

Technical Insight: Handling the asynchronous nature of permission requests created race conditions. A "Loading" state UI was implemented to handle the gap between app launch and data retrieval, with a graceful fallback to a default location if permissions are denied.

E. Dynamic Environmental Backgrounds

Objective: To create an emotionally resonant UI that visually mimics the current weather conditions.

Implementation: A mapping system associates specific weather condition codes (e.g., 800 for Clear) with specific color gradients.

Technical Insight: As seen in the screenshot below, a "Clear Sky" at night triggers a deep indigo/blue background. This required fine-tuning contrast ratios to ensure white text remains readable against changing background hues (e.g., blue for rain, orange for sunset, grey for overcast).

4. Challenges and Solutions

Feature

Challenge

Solution

Theme Toggle

Default system themes vary across devices, leading to inverted colors on load.

Implemented a check for system preference on app_mount before enabling manual toggles.

Unit Conversion

Auto-refreshing data caused Celsius-to-Fahrenheit calculations to compound erroneously.

Decoupled the conversion logic from the rendering loop; conversion now happens only on display, not on the raw data.

Geolocation

Async permissions caused the UI to load empty before coordinates were returned.

Added a loading indicator and a fallback mechanism to default to manual search if the timeout is reached.

Dynamic Backgrounds

Ensuring text readability against high-saturation backgrounds (like the deep blue night sky).

Adopted a semi-transparent "glassmorphism" card style for data containers to ensure text contrast.

5. Application Screenshots

Figure 1: Main Interface demonstrating the "Dynamic Background" feature. The application detects "Clear Sky" at night (indicated by the moon icon) and adjusts the background gradient to a deep indigo to simulate a clear night sky.

6. Conclusion

The project successfully met all base and enhanced requirements. The inclusion of dynamic elements—specifically the background color adaptation and geolocation—significantly elevates the user experience from a static data tool to an interactive environment. Future iterations could include hourly forecasting graphs and severe weather alerts.