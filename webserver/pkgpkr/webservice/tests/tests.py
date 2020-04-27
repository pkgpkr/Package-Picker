"""
Functional tests for the web service using Selenium
"""

from sys import platform
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.test import LiveServerTestCase
from pyvirtualdisplay import Display


class LoginTest(LiveServerTestCase):
    """
    Selenium tests for the web service
    """

    # Needed to overwrite LiveServerTestCase default port (i.e. 8001)
    port = 8000

    def setUp(self):

        # Create chrome sessions depending on OS
        if platform == "win32":
            path = "C:\\DRIVERS\\chromedriver_win32\\chromedriver.exe"
            self.driver = webdriver.Chrome(executable_path=path)
        elif platform == "darwin":
            path = "/usr/local/bin/chromedriver"
            self.driver = webdriver.Chrome(executable_path=path)
        else:

            # Assure no visibility display for Ubuntu CLI to render without UI
            # Assure large enough screen to preven responsive look which hides some buttons
            display = Display(visible=0, size=(1920, 1080))
            display.start()

            path = "/usr/bin/chromedriver"
            self.driver = webdriver.Chrome(executable_path=path)

        self.driver.implicitly_wait(3)

        self.driver.maximize_window()
        self.driver.get(self.live_server_url)
        super(LoginTest, self).setUp()

    def tearDown(self):
        self.driver.quit()
        super(LoginTest, self).tearDown()

    def test_work_process(self):
        """
        End to end test of the recommendation workflow
        """

        """
          ___ _        _   _      ___
         / __| |_ __ _| |_(_)__  | _ \__ _ __ _ ___ ___
         \__ \  _/ _` |  _| / _| |  _/ _` / _` / -_|_-<
         |___/\__\__,_|\__|_\__| |_| \__,_\__, \___/__/
                                          |___/
        """
        # get the login buttons
        login_button = self.driver.find_element_by_xpath(
            "//*[@id='navbarBasicExample']/div[2]/div/div")

        login_button.click()

        # Check if the user redirected back to the main page
        self.assertEqual(f'http://localhost:{LoginTest.port}/', self.driver.current_url)

        # About button
        about_ele = self.driver.find_element_by_xpath(
            "//*[@id='navbarBasicExample']/div[1]/a[2]")
        about_ele.click()

        # Check if the user at about page
        self.assertEqual(f'http://localhost:{LoginTest.port}/about', self.driver.current_url)

        """
             _ ___   ___                  _ _
          _ | / __| | _ \___ _ __  ___ __(_) |_ ___ _ _ _  _
         | || \__ \ |   / -_) '_ \/ _ (_-< |  _/ _ \ '_| || |
          \__/|___/ |_|_\___| .__/\___/__/_|\__\___/_|  \_, |
                            |_|                         |__/
        """
        # My repositories button
        reps_ele_path = "//*[@id='navbarBasicExample']/div[1]/a[4]"
        reps_ele = self.driver.find_element_by_xpath(reps_ele_path)
        reps_ele.click()

        # Check if the user at my repositories page
        self.assertEqual(f'http://localhost:{LoginTest.port}/repositories', self.driver.current_url)

        # The first element from the repos list
        first_repo_ele = self.driver.find_element_by_xpath(
            "//tbody/tr[1]/td[1]/a")
        first_repo_ele.click()

        # Wait until the loading animation is disappeared
        loading_state = self.driver.find_element_by_xpath("//*[@class='pageloader']")
        WebDriverWait(self.driver, 30).until(EC.invisibility_of_element(loading_state))

        # Check if the user at recommendations page
        self.assertEqual("Recommendations", self.driver.title)
        showing_text = self.driver.find_element_by_xpath("//*[@id='recommend-table_info']")
        self.assertIn('Showing 1', showing_text.get_attribute('textContent'))

        # Check if text in branch selector is `master`
        branch_span = self.driver.find_element_by_xpath("//*[@class='dropdown-trigger']/button/span")
        self.assertEqual("master", branch_span.get_attribute('textContent'))

        # Click on dropdown and another branch in the Dropdown
        branch_to_click = self.driver.find_element_by_xpath("//*[@class='dropdown-menu']/div/a[@href='?branch=test']")
        branch_dropdown = self.driver.find_element_by_xpath("//*[@class='dropdown-trigger']/button")
        branch_dropdown.click()
        branch_to_click.click()

        # Wait until the loading animation is disappeared
        loading_state = self.driver.find_element_by_xpath("//*[@class='pageloader']")
        WebDriverWait(self.driver, 30).until(EC.invisibility_of_element(loading_state))

        # Check if the user at recommendations page with different branch
        self.assertEqual("Recommendations", self.driver.title)
        showing_text = self.driver.find_element_by_xpath("//*[@id='recommend-table_info']")
        self.assertIn('Showing 1', showing_text.get_attribute('textContent'))

        # Assure that we are looking at another branch
        branch_span = self.driver.find_element_by_xpath("//*[@class='dropdown-trigger']/button/span")
        self.assertEqual("test", branch_span.get_attribute('textContent'))

        # Category border
        category_order_ele = self.driver.find_element_by_xpath(
            "//*[@id='recommend-table']/thead/tr/th[4]")

        # Click it twice to make sure the first recommendation has at least one category
        category_order_ele.click()
        category_order_ele.click()

        # The first category
        first_category_ele = self.driver.find_element_by_xpath(
            "//*[@id='recommend-table']/tbody/tr[1]/td[3]/div[1]/button")
        first_category_ele.click()

        # Clear button
        clear_ele = self.driver.find_element_by_xpath("//*[@id='category-clear']")
        clear_ele.click()

        # Filter text inputs
        search_ele_path = "//*[@id='recommendationFilter']"
        search_ele = self.driver.find_element_by_xpath(search_ele_path)
        search_ele.send_keys("te")
        search_ele.clear()

        # The first element from the recommendation list
        first_recommendation_ele = self.driver.find_element_by_xpath(
            "//*[@id='recommend-table']/tbody/tr[1]/td[1]/div")
        first_recommendation_ele.click()

        # Ensure that the package detail window opens as expected
        self.driver.switch_to_window("package_details")
        self.driver.find_element_by_xpath("//*[@id='app']")

        # Close the npm page
        self.driver.close()
        window_before = self.driver.window_handles[0]
        self.driver.switch_to_window(window_before)

        """  _ ___   ___
          _ | / __| |   \ ___ _ __  ___
         | || \__ \ | |) / -_) '  \/ _ \
          \__/|___/ |___/\___|_|_|_\___/

        """
        # Go back to the home page
        home_ele = self.driver.find_element_by_xpath(
            "//*[@id='navbarBasicExample']/div[1]/a[1]")
        home_ele.click()

        # Check if the user is on the home page
        self.assertEqual(f'http://localhost:{LoginTest.port}/', self.driver.current_url)

        # Try the recommendations demo
        demo_ele = self.driver.find_element_by_xpath(
            "//*[@id='recommendation-button']")
        demo_ele.click()

        # Wait until the loading animation is disappeared
        loading_state = self.driver.find_element_by_xpath("//*[@class='pageloader']")
        WebDriverWait(self.driver, 30).until(EC.invisibility_of_element(loading_state))

        # Check if the user at recommendations page
        self.assertEqual("Recommendations", self.driver.title)
        showing_text = self.driver.find_element_by_xpath("//*[@id='recommend-table_info']")
        self.assertIn('Showing 1', showing_text.get_attribute('textContent'))

        # Click the PkgPkr Score button
        score_ele = self.driver.find_element_by_xpath("//*[@id='recommend-table']/tbody/tr[1]/td[2]/img")
        score_ele.click()

        # Make sure the modal opens
        close_ele = self.driver.find_element_by_xpath("//*[@id='modal-close']")
        close_ele.click()


        """
          ___      _   _               ___
         | _ \_  _| |_| |_  ___ _ _   |   \ ___ _ __  ___
         |  _/ || |  _| ' \/ _ \ ' \  | |) / -_) '  \/ _ \
         |_|  \_, |\__|_||_\___/_||_| |___/\___|_|_|_\___/
              |__/
        """
        # Go back to the home page
        home_ele = self.driver.find_element_by_xpath(
            "//*[@id='navbarBasicExample']/div[1]/a[1]")
        home_ele.click()

        # Check if the user is on the home page
        self.assertEqual(f'http://localhost:{LoginTest.port}/', self.driver.current_url)


        # Choose the Python from demo dropdown and click recommendation
        select = self.driver.find_element_by_xpath('//*[@id="lang-select"]')
        select.click()

        python_option = self.driver.find_element_by_xpath('//*[@id="lang-select"]/option[text()="Python"]')
        python_option.click()


        text_area = self.driver.find_element_by_xpath('//*[@id="manual-input"]')
        self.assertIn('Django', text_area.get_attribute('value'))

        recommend_btn = self.driver.find_element_by_xpath('//*[@id="recommendation-button"]')
        recommend_btn.click()

        # # Wait until the loading animation is disappeared
        loading_state = self.driver.find_element_by_xpath("//*[@class='pageloader']")
        WebDriverWait(self.driver, 30).until(EC.invisibility_of_element(loading_state))

        # Assure it is showing Python on recommendation page and have results
        title = self.driver.find_element_by_xpath('/html/body/section[2]//h2')
        self.assertIn('Python package', title.get_attribute('textContent'))
        #showing_text = self.driver.find_element_by_xpath("//*[@id='recommend-table_info']")
        #self.assertIn('Showing 1', showing_text.get_attribute('textContent'))


        # Logout button
        logout_ele = self.driver.find_element_by_xpath(
            "//*[@id='navbarBasicExample']/div[2]/div/div")
        logout_ele.click()

        # Check if the user redirected back to the main page
        self.assertEqual("Package Picker", self.driver.title)
