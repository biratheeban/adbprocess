from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import json
import time
from appium.options.android import UiAutomator2Options

# Setup desired capabilities
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "emulator-5554"
options.app_package = "lk.bi007.testapp"
options.automation_name = "UiAutomator2"
options.no_reset = True

driver = webdriver.Remote("http://localhost:4723", options=options)

recorded_events = []
previous_ui_state = {}
previous_activity = None

def get_ui_state():
    """Fetches current UI state (elements and their attributes)."""
    ui_state = {}
    try:
        elements = driver.find_elements(by=AppiumBy.XPATH, value="//*")  # Get all UI elements
        for element in elements:
            try:
                resource_id = element.get_attribute("resource-id") or "unknown"
                text = element.get_attribute("text") or ""
                bounds = element.get_attribute("bounds") or ""
                class_name = element.get_attribute("class") or ""
                checked = element.get_attribute("checked") if "CheckBox" in class_name else None
                clickable = element.get_attribute("clickable") == "true"
                
                ui_state[resource_id] = {
                    "text": text,
                    "bounds": bounds,
                    "class": class_name,
                    "checked": checked,
                    "clickable": clickable,
                    "last_tap": previous_ui_state.get(resource_id, {}).get("last_tap", 0)
                }
            except Exception:
                pass  # Ignore elements that cannot be accessed
    except Exception as e:
        print(f"Error getting UI state: {e}")
    return ui_state

def detect_changes():
    """Detects actual button clicks and records relevant events."""
    global previous_ui_state, previous_activity
    current_ui_state = get_ui_state()
    current_activity = driver.current_activity

    # Record activity change
    if previous_activity is not None and current_activity != previous_activity:
        recorded_events.append({
            "type": "activity_change",
            "timestamp": time.time(),
            "from_activity": previous_activity,
            "to_activity": current_activity
        })
        print(f"[LOG] Activity changed: {previous_activity} -> {current_activity}")

    previous_activity = current_activity

    # Detect actual clicks only on buttons
    for element_id, new_attrs in current_ui_state.items():
        old_attrs = previous_ui_state.get(element_id, {})

        # Ensure it's a button and was clicked (state changed)
        if new_attrs.get("clickable") == "true" and "Button" in new_attrs.get("class", ""):
            if new_attrs != old_attrs:  # Ensure state change happened
                recorded_events.append({
                    "type": "button_click",
                    "timestamp": time.time(),
                    "activity": current_activity,
                    "element": element_id,
                    "value": new_attrs.get("text", "unknown")
                })
                print(f"[LOG] Click detected: {element_id} -> {new_attrs.get('text', 'Button')}")

    previous_ui_state = current_ui_state  # Update previous state

def save_events():
    """Save recorded events to a JSON file."""
    try:
        with open("recorded_events.json", "w") as f:
            json.dump(recorded_events, f, indent=4)
        print(f"Saved {len(recorded_events)} events to recorded_events.json")
    except Exception as e:
        print(f"Error saving events: {e}")
        # Create a backup file in case of error
        with open(f"recorded_events_backup_{int(time.time())}.json", "w") as f:
            json.dump(recorded_events, f, indent=4)

def monitor_ui():
    """Continuously monitors for user interactions."""
    global previous_activity
    print("Recording started. Interact with the app.")
    try:
        previous_activity = driver.current_activity
        while True:
            detect_changes()
            time.sleep(0.5)  # Poll every half second for more responsive detection
    except KeyboardInterrupt:
        print("Recording stopped by user.")
    except Exception as e:
        print(f"Error during monitoring: {e}")
    finally:
        save_events()
        driver.quit()

# Start monitoring
monitor_ui()
