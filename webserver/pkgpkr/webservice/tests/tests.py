from selenium import webdriver
from sys import platform
from django.test import LiveServerTestCase
from pyvirtualdisplay import Display


class LoginTest(LiveServerTestCase):
    # Needed to overwrite LiveServerTestCase default port (i.e. 8001)
    port = 8000

    def setUp(self):


        # Create chrome sessions depending on OS
        if platform == "win32":
            self.driver = webdriver.Chrome(executable_path="C:\DRIVERS\chromedriver_win32\chromedriver.exe")
        elif platform == "darwin":
            self.driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver")
        else:
            self.driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver")

            # Assure no visibility display for Ubuntu CLI to render without UI
            # Assure large enough screen to preven responsive look which hides some buttons
            display = Display(visible=0, size=(1920, 1080))
            display.start()

        self.driver.implicitly_wait(3)


        self.driver.maximize_window()
        self.driver.get(self.live_server_url)
        super(LoginTest, self).setUp()

    def tearDown(self):
        self.driver.quit()
        super(LoginTest, self).tearDown()

    def test_work_process(self):
        # get the login buttons
        login_button = self.driver.find_element_by_xpath("//*[@id='navbarBasicExample']/div[2]/div/div")

        login_button.click()

        # Check if the user redirected back to the main page
        self.assertEqual('http://localhost:8000/', self.driver.current_url)

        # About button
        about_ele = self.driver.find_element_by_xpath("//*[@id='navbarBasicExample']/div[1]/a[2]")
        about_ele.click()

        # Check if the user at about page
        self.assertEqual('http://localhost:8000/about', self.driver.current_url)

        # My repositories button
        reps_ele = self.driver.find_element_by_xpath("//*[@id='navbarBasicExample']/div[1]/a[3]")
        reps_ele.click()

        # Check if the user at my repositories page
        self.assertEqual('http://localhost:8000/repositories', self.driver.current_url)

        # The first element from the repos list
        first_repo_ele = self.driver.find_element_by_xpath("//*[@id='DataTables_Table_0']/tbody/tr/td[1]/a")
        first_repo_ele.click()

        # Check if the user at recommendations page
        self.assertEqual("Recommendations", self.driver.title)

        # Category border
        category_order_ele = self.driver.find_element_by_xpath("//*[@id='DataTables_Table_0']/thead/tr/th[2]")

        # Click it twice to make sure the first recommendation has at least one category
        category_order_ele.click()
        category_order_ele.click()

        # The first category
        first_category_ele = self.driver.find_element_by_xpath("//*[@id='DataTables_Table_0']/tbody/tr[1]/td[2]/div[1]/button")
        first_category_ele.click()

        # Clear button
        clear_ele = self.driver.find_element_by_xpath("//*[@id='categoryClear']")
        clear_ele.click()

        # Filter text inputs
        search_ele = self.driver.find_element_by_xpath("//*[@id='recommendationFilter']")
        search_ele.send_keys("te")
        search_ele.clear()

        # The first element from the recommendation list
        first_recommendation_ele = self.driver.find_element_by_xpath("//*[@id='DataTables_Table_0']/tbody/tr/td[1]/a")
        first_recommendation_ele.click()

        # Logout button
        logout_ele = self.driver.find_element_by_xpath("//*[@id='navbarBasicExample']/div[2]/div/div")
        logout_ele.click()

        # Check if the user redirected back to the main page
        self.assertEqual("Package Picker", self.driver.title)
