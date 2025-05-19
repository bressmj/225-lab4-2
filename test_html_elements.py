from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import unittest

class TestContacts(unittest.TestCase):
    def setUp(self):
        # Setup Firefox options for headless operation
        firefox_options = Options()
        firefox_options.add_argument("--headless")  # Ensures the browser window does not open
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Firefox(options=firefox_options)

    def test_contacts(self):
        driver = self.driver
        driver.get("http://10.48.10.146")  # Replace with your target website
        
        # Wait for the contact list section to load (adjust selector to your app)
        wait = WebDriverWait(driver, 10)  # Wait for up to 10 seconds
        try:
            # Replace the below selector with the appropriate one for your app
            contact_section = wait.until(EC.presence_of_element_located((By.ID, "contact-list")))  # Example selector
            
            # Check for the presence of all 10 test contacts
            for i in range(10):
                test_name = f'Test Name {i}'
                # Assert if the contact name is found in the page source
                assert test_name in driver.page_source, f"Test contact {test_name} not found in page source"
            
            print("Test completed successfully. All 10 test contacts were verified.")
        
        except Exception as e:
            print(f"An error occurred: {e}")
            driver.save_screenshot("error_screenshot.png")  # Save a screenshot for debugging

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
