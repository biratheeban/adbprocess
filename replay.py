import json
import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.action_chains import ActionChains
from appium.options.android import UiAutomator2Options

# Configuration
APP_PACKAGE = "lk.bi007.testapp"

# Load recorded events
with open("recorded_events.json", "r") as f:
    recorded_events = json.load(f)

# Setup desired capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "emulator-5554"
options.app_package = APP_PACKAGE
options.automation_name = "UiAutomator2"
options.no_reset = True

# Start Appium driver
driver = webdriver.Remote("http://localhost:4723", options=options)

def is_app_running():
    """Check if the app is running."""
    return driver.current_package == APP_PACKAGE

def launch_app():
    """Launch the app if it's not running."""
    if not is_app_running():
        print(f"[INFO] {APP_PACKAGE} is not running. Launching now...")
        driver.activate_app(APP_PACKAGE)  # Ensure the app is running
        time.sleep(3)  # Wait for app to start

def switch_activity(activity_name):
    """Explicitly switch to a different activity using Appium execute_script."""
    try:
        driver.execute_script("mobile: shell", {
            "command": f"am start -n {APP_PACKAGE}/{activity_name}"
        })
        print(f"[INFO] Switched to activity: {activity_name}")
        time.sleep(2)  # Wait for activity transition
    except Exception as e:
        print(f"[ERROR] Failed to switch activity: {e}")

def replay_events():
    """Replay recorded user interactions"""
    launch_app()  # Ensure the app is open

    print(f"Replaying {len(recorded_events)} events...")

    for event in recorded_events:
        try:
            if event["type"] == "element_click":
                element_id = event["element"]
                if element_id:
                    element = driver.find_element(AppiumBy.ID, element_id)
                    actions = ActionChains(driver)
                    actions.move_to_element(element).click().perform()
                    print(f"[REPLAY] Clicked on {element_id}")

            elif event["type"] == "text_input":
                element_id = event["element"]
                text_value = event["value"]
                if element_id:
                    element = driver.find_element(AppiumBy.ID, element_id)
                    element.clear()
                    element.send_keys(text_value)
                    print(f"[REPLAY] Entered text in {element_id}: {text_value}")

            elif event["type"] == "checkbox_toggle":
                element_id = event["element"]
                if element_id:
                    element = driver.find_element(AppiumBy.ID, element_id)
                    element.click()
                    print(f"[REPLAY] Toggled checkbox {element_id}")

            elif event["type"] == "activity_change":
                from_activity = event["from_activity"]
                to_activity = event["to_activity"]
                print(f"[INFO] Activity changed from {from_activity} to {to_activity}")
                switch_activity(to_activity)  # Switch activity explicitly

            time.sleep(1)  # Small delay to mimic real user actions

        except Exception as e:
            print(f"[ERROR] Failed to replay event {event}: {e}")

    print("Replay complete.")
    driver.quit()

# Run the replay
replay_events()
