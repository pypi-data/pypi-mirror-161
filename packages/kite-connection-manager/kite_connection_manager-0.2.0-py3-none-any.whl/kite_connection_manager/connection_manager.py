from .connect_without_apikey import KiteConnectBrowser
from .utils import get_totp
from .repeat_timer import RepeatTimer
import logging
import time
from typing import Optional
from kiteconnect import KiteConnect
from kiteconnect.exceptions import KiteException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)


class ZerodhaLoginException(Exception):
    """
    Exception raised while logging into Zerodha.
    """

    def __init__(self, config, error=None, message="Failed to login to Zerodha!"):
        super().__init__("{}\nProvided config: {}\n{}".format(message, config, "Error from client: {}".format(
            error) if error is not None else ""))


class KiteConnectionManager:
    """
    This class is responsible to login to Zerodha and return the KiteConnect handle through which we can act upon
    the particular account.

    @:param user_details dictionary containing login credentials - user_name, password, pin, google_authenticator_secret
        ,api_key, api_secret
    @:param refresh_connection: if true refresh the connection every refresh_interval_minutes
    """

    def __init__(self, user_details: dict, refresh_connection: bool = False, refresh_interval_minutes: int = 10):
        if 'user_name' not in user_details or 'password' not in user_details:
            raise ZerodhaLoginException(config=user_details, message="Must have both user_name and password set")
        if 'pin' not in user_details and 'google_authenticator_secret' not in user_details:
            raise ZerodhaLoginException(config=user_details,
                                        message="One of pin or google_authenticator_secret must be provided!")
        self.config = user_details
        self.user_name = user_details.get('user_name', None)
        self.password = user_details.get('password', None)
        self.api_key = user_details.get('api_key', None)
        self.api_secret = user_details.get('api_secret', None)
        self.pin = user_details.get('pin', None)
        self.google_authenticator_secret = user_details.get('google_authenticator_secret', None)
        self.kite = None
        if refresh_connection:
            self.background_thread = RepeatTimer(refresh_interval_minutes * 60, self.get_kite_connect)

    def is_logged_in(self) -> bool:
        """
        Since, KiteConnect doesn't provide a clean way to check if the access token is valid. We will try to fetch the
        price of an instrument and see if a valid response is return. If we see a status code of 403 , it means that
        the session is expired. Check https://kite.trade/docs/connect/v3/exceptions/#common-http-error-codes to learn
        about error codes.

        @:return True if the KiteConnect is still valid
        """
        if not self.kite:
            return False
        try:
            self.kite.ltp("NSE:INFY")
        except KiteException as ke:
            if ke.code == 403:
                return False
            raise ke
        return True

    def shutdown(self):
        if self.background_thread:
            self.background_thread.cancel()

    def get_kite_connect(self) -> Optional[KiteConnect]:
        if not self.is_logged_in():
            try:
                self.kite = self.__login()
            except ZerodhaLoginException as e:
                logger.error('Failed to login user_id %s. Error: %s', self.user_name, e)
                self.kite = None
        return self.kite

    def __login(self) -> KiteConnect:
        """
        Login a user and fetch the corresponding KiteConnect handle
        """
        logger.info('Trying to login user_id %s', self.user_name)
        if self.api_key is not None and self.api_secret is not None:
            return self.__login_with_apikey()
        return self.__login_without_apikey()

    def __login_without_apikey(self) -> KiteConnect:
        z = KiteConnectBrowser(user_id=self.user_name, password=self.password,
                               google_authenticator_secret=self.google_authenticator_secret, pin=self.pin)
        try:
            z.login()
        except Exception as e:
            raise ZerodhaLoginException(self.config, e)
        logger.info("Successfully logged in %s without API Key", self.user_name)
        return z

    def __login_with_apikey(self) -> KiteConnect:
        """
        Establishes connection to Kite by "always" generating a new session.
        """
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=op)
        try:
            kite = KiteConnect(api_key=self.api_key)
            driver.get(kite.login_url())

            WebDriverWait(driver=driver, timeout=10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='login-form']")))
            driver.find_element(By.XPATH, "//input[@type='text']").send_keys(self.user_name)
            driver.find_element(By.XPATH, "//input[@type='password']").send_keys(self.password)
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()

            time.sleep(1)
            WebDriverWait(driver=driver, timeout=10).until(
                EC.visibility_of_element_located((By.XPATH, "//div[@class='login-form']")))
            driver.find_element(By.XPATH, "//input[@type='text']").send_keys(
                get_totp(self.google_authenticator_secret) if self.pin is None else self.pin)
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()

            time.sleep(1)
            request_token = KiteConnectionManager.__extract_request_token(driver.current_url)
            kite.generate_session(request_token, api_secret=self.api_secret)
            logger.info("Successfully logged in %s using API Key %s. Request Token: %s", self.user_name, self.api_key,
                        request_token)
            return kite
        except Exception as e:
            raise ZerodhaLoginException(self.config, e)
        finally:
            driver.close()
            driver.quit()

    @staticmethod
    def __extract_request_token(redirect_url: str) -> str:
        """
        Extracts request_token from the redirect_url
        :param redirect_url: The URL to which Kite API redirects to after successful login
        """
        try:
            parsed_url = urlparse(redirect_url)
            return parse_qs(parsed_url.query)['request_token'][0]
        except Exception as e:
            logger.error('Unable to extract request token from the redirect URL %s', redirect_url)
