from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from datetime import datetime
import json
import time
import logging
import traceback

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WidgetInteractionRecorder:
    def __init__(self, device_name, app_package, host, connection_timeout=30):
        self.options = UiAutomator2Options()
        self.options.platform_name = "Android"
        self.options.device_name = device_name
        self.options.app_package = app_package
        self.options.automation_name = "UiAutomator2"
        self.options.no_reset = True
        
        # Add additional capabilities for better detection
        self.options.set_capability('androidDeviceReadyTimeout', 30)
        self.options.set_capability('autoGrantPermissions', True)
        self.options.set_capability('newCommandTimeout', 120)
        
        self.host = host
        self.connection_timeout = connection_timeout
        self.driver = None
        self.actions = []
        self.last_activity = None
        self.previous_elements_state = {}  # Track previous state of elements
        
        self._connect_to_appium()
        
    def _connect_to_appium(self):
        try:
            logging.info(f"Connecting to Appium server at {self.host}")
            self.driver = webdriver.Remote(self.host, options=self.options)
            logging.info("Successfully connected to Appium server")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Appium server: {str(e)}")

    def start_recording(self):
        try:
            logging.info("Starting interaction recording...")
            while True:
                try:
                    self._check_activity_change()
                    self._scan_for_interactions()
                    time.sleep(0.1)  # Faster scanning interval
                except WebDriverException as e:
                    logging.error(f"WebDriver error: {str(e)}")
                    break
                except Exception as e:
                    logging.error(f"Error during recording: {str(e)}")
                    traceback.print_exc()
                    time.sleep(1)
        except KeyboardInterrupt:
            logging.info("\nReceived stop signal. Stopping recording gracefully...")
        finally:
            self.save_recording()

    def _check_activity_change(self):
        try:
            current_activity = self.driver.current_activity
            if current_activity != self.last_activity:
                logging.info(f"Activity changed: {current_activity}")
                self.last_activity = current_activity
                self.previous_elements_state = {}  # Reset state tracking on activity change
        except Exception as e:
            logging.debug(f"Error checking activity: {str(e)}")

    def _scan_for_interactions(self):
        """Enhanced interaction scanning with better detection"""
        try:
            # Find all potentially interactive elements
            elements = self.driver.find_elements(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector()'
                '.clickable(true)'
                '.enabled(true)'
                '.focusable(true)'
            )
            
            logging.debug(f"Found {len(elements)} potential interactive elements")
            
            current_elements_state = {}
            for element in elements:
                try:
                    if not element.is_displayed():
                        continue
                        
                    element_id = self._get_element_identifier(element)
                    if not element_id:
                        continue
                        
                    # Get current state
                    current_state = self._get_element_state(element)
                    current_elements_state[element_id] = current_state
                    
                    # Compare with previous state
                    if self._has_state_changed(element_id, current_state):
                        self._record_interaction(element, current_state)
                    
                except Exception as e:
                    logging.debug(f"Error processing element: {str(e)}")
            
            # Update previous state
            self.previous_elements_state = current_elements_state
            
        except Exception as e:
            logging.error(f"Error in scanning interactions: {str(e)}")

    def _get_element_identifier(self, element):
        """Get a unique identifier for the element"""
        try:
            resource_id = element.get_attribute('resource-id')
            if resource_id:
                return resource_id
            
            # Fallback to creating a composite ID
            bounds = element.get_attribute('bounds')
            text = element.get_attribute('text')
            class_name = element.get_attribute('class')
            return f"{class_name}_{bounds}_{text}"
        except:
            return None

    def _get_element_state(self, element):
        """Get comprehensive element state"""
        try:
            return {
                'selected': element.get_attribute('selected'),
                'checked': element.get_attribute('checked'),
                'focused': element.get_attribute('focused'),
                'text': element.get_attribute('text'),
                'content-desc': element.get_attribute('content-desc'),
                'enabled': element.get_attribute('enabled'),
                'clickable': element.get_attribute('clickable'),
                'bounds': element.get_attribute('bounds'),
                'displayed': element.is_displayed()
            }
        except Exception as e:
            logging.debug(f"Error getting element state: {str(e)}")
            return {}

    def _has_state_changed(self, element_id, current_state):
        """Check if element state has changed meaningfully"""
        if element_id not in self.previous_elements_state:
            return False
            
        prev_state = self.previous_elements_state[element_id]
        
        # Check for meaningful state changes
        important_attrs = ['selected', 'checked', 'focused', 'text']
        return any(
            current_state.get(attr) != prev_state.get(attr)
            for attr in important_attrs
            if attr in current_state and attr in prev_state
        )

    def _record_interaction(self, element, state):
        """Record detected interaction with enhanced logging"""
        try:
            action_type = self._determine_action_type(element, state)
            if action_type != "unknown":
                widget_attrs = self._get_widget_attributes(element)
                
                event = {
                    'type': action_type,
                    'timestamp': datetime.now().isoformat(),
                    'activity': self.last_activity,
                    'widget': widget_attrs,
                    'state_change': state
                }
                
                self.actions.append(event)
                logging.info(
                    f"[{event['activity']}] {action_type.upper()}: "
                    f"{widget_attrs['id']} - {widget_attrs.get('text', 'N/A')}"
                )
                
                # Debug logging
                logging.debug(f"Recorded interaction details: {json.dumps(event, indent=2)}")
                
        except Exception as e:
            logging.error(f"Error recording interaction: {str(e)}")

    def _determine_action_type(self, element, state):
        """Enhanced action type detection"""
        try:
            class_name = element.get_attribute("class").lower()
            
            if "edittext" in class_name:
                return "text_input" if state.get('focused') == "true" else "unknown"
            elif state.get('checked') == "true":
                return "checkbox"
            elif state.get('selected') == "true":
                return "selection"
            elif element.get_attribute("clickable") == "true":
                return "click"
            elif element.get_attribute("scrollable") == "true":
                return "scroll"
                
            return "unknown"
        except:
            return "unknown"

    def _get_widget_attributes(self, element):
        """Get comprehensive widget attributes"""
        try:
            return {
                'id': element.get_attribute('resource-id'),
                'text': element.get_attribute('text'),
                'class': element.get_attribute('class'),
                'content_desc': element.get_attribute('content-desc'),
                'package': element.get_attribute('package'),
                'activity': self.last_activity,
                'bounds': element.get_attribute('bounds'),
                'clickable': element.get_attribute('clickable'),
                'enabled': element.get_attribute('enabled'),
                'focusable': element.get_attribute('focusable')
            }
        except Exception as e:
            logging.debug(f"Error getting widget attributes: {str(e)}")
            return {'error': str(e)}

    def save_recording(self, filename=None):
        if not self.actions:
            logging.info("No interactions recorded. Skipping save.")
            return
            
        if filename is None:
            filename = f"interaction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        recording_data = {
            'app_package': self.options.app_package,
            'device_name': self.options.device_name,
            'recorded_at': datetime.now().isoformat(),
            'total_activities': len(set(event['activity'] for event in self.actions)),
            'total_interactions': len(self.actions),
            'events': self.actions
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(recording_data, f, indent=2)
            logging.info(f"Recording saved to {filename} ({len(self.actions)} events)")
        except Exception as e:
            logging.error(f"Error saving recording: {str(e)}")

    def cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

if __name__ == "__main__":
    recorder = WidgetInteractionRecorder(
        device_name="emulator-5554",
        app_package="lk.bi007.testapp",
        host="http://localhost:4723"
    )
    
    try:
        recorder.start_recording()
    except KeyboardInterrupt:
        logging.info("\nStopping recording...")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        traceback.print_exc()
    finally:
        recorder.cleanup()