
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

class Stage(object):
	START = 0
	LOGINED = 1
	PERF_OPENED = 2


class Selenium_yes24(object):
	def __init__(self, idperf, x=100, y=100, w=1024, h=700):
		self.idperf = idperf
		self.stage = Stage.START
		self.using = False

		options = Options()
		options.add_argument('--disable-infobars')
		options.add_argument('--window-position={},{}'.format(x,y));
		options.add_argument('--window-size={},{}'.format(w,h))
		self.driver = webdriver.Chrome('./chromedriver', chrome_options=options)  # Optional argument, if not specified will search path.
		#self.driver.set_window_position(x, y)
		#self.driver.set_window_size(w, h)
		self.driver.implicitly_wait(5)

	def login(self, userid, userpw):
		URL = 'https://ticket.yes24.com/Pages/Login/LoginEnt.aspx?ReturnURL=http://ticket.yes24.com/Home/Perf/PerfDetailInfo.aspx&&ReturnParams=IdPerf={}'.format(self.idperf)
		self.driver.get(URL);

		## LOGIN FIRST
		self.driver.find_element_by_name('txtLoginID').send_keys(userid)
		self.driver.find_element_by_name('txtPassword').send_keys(userpw)
		self.driver.find_element_by_name('imgLogin').click()

		## save stage
		self.stage = Stage.LOGINED

		"""
		executor_url = driver.command_executor._url
		session_id = driver.session_id

		print(session_id)
		print(executor_url)
		"""

	def isUsing(self):
		return self.using

	def setUsing(self, flag):
		self.using = flag

	def logout(self):
		# it is for removing command_executor
		time.sleep(1)
		self.driver.quit()

	def openBlank(self, count=1):
		self.driver.find_element_by_xpath("//a[contains(@href,'LogOutUrl')]")
		self.driver.execute_script("window.open()")

		## handling popup
		main_window_handle = self.driver.current_window_handle

		popup_window_handle = None
		for handle in self.driver.window_handles:
		    if handle != main_window_handle:
		        popup_window_handle = handle
		        #break

		self.driver.switch_to.window(popup_window_handle)

	def openPerf(self, idperf, idtime):
		URL = 'http://ticket.yes24.com/Pages/Perf/Sale/PerfSaleProcess.aspx?IdPerf={}&IdTime={}'.format(idperf, idtime)
		#URL = 'http://ticket.yes24.com/Pages/Perf/Sale/PerfSaleProcess.aspx?IdPerf={}'.format(idperf)
		self.driver.get(URL)
		self.stage = Stage.PERF_OPENED

	def waitLastPage(self):
		print("Waiting last page")
		while True:
			es = self.driver.find_element_by_xpath("//img[@id='captchaImg']")
			if es is not None and es.is_displayed():
				break
			time.sleep(1)
		print("Found last page")

	def findTime(self, date, idtime):
		"""
		while True:
			print("> find month before")
			es = self.driver.find_elements_by_xpath("//a[@id='{}']".format(date))
			print("> find month after")
			if len(es) == 0:
				print("move next month")
				self.driver.find_element_by_css_selector('.next.dcursor').click()
			else:
				print("found month")
				break

		## click date
		self.driver.find_element_by_xpath("//a[@id='{}']".format(date)).click()
		## click time
		self.driver.find_element_by_xpath("//li[@value='{}']".format(idtime)).click()
		"""
		## click select seat
		#self.driver.find_element_by_xpath("//img[@id='btnSeatSelect']").click()
		retry_click_element_by_xpath(self.driver, "//img[@id='btnSeatSelect']")

		time.sleep(1)

	def findTime_m(self, date, idtime):
		pass

	def selectSeat(self, idhall, token, ptags):
		## switch frame
		#iframe = self.driver.find_element_by_xpath("//iframe[@id='ifrmSeatFrame']")	
		iframe = self.driver.find_elements_by_tag_name("iframe")	
		self.driver.switch_to.frame(iframe[0])

		# WAIT UNTIL PAGE LOADED
		retry_xpath_empty(self.driver, "//div[@id='divSeatArray']")

		## li liSelSeat
		# id and grade is must
		#seats_str = "<p id=\"C600031\" class=\"txt2\" name=\"cseat\" grade=\"VIP석\">1층B구역 04열 024번</p>"
		seats_str = ptags

		try:
			liselseat = self.driver.find_element_by_xpath("//*[@id='liSelSeat']")
			self.driver.execute_script("arguments[0].innerHTML = '{}'".format(seats_str), liselseat)
		except NoSuchElementException as e:
			print(str(e))

		time.sleep(1)

		## complete select seat
		try:
			self.driver.find_element_by_xpath("//*[@class='booking']").click()
		except NoSuchElementException as e:
			print(str(e))
		# MOBILE
		#self.driver.find_element_by_xpath("//a[contains(@onclick, 'fdc_SeatChoiceEnd')]").click()


		#driver.switch_to.window(main_window_handle) #or driver.switch_to_default_content()
		#print("switched to main")

		"""
		while True:
			print("waiting 5seconds... to avoid selenium quit")
			time.sleep(5)
		"""

	def nextStep(self):
		self.driver.switch_to.default_content()
		#self.driver.find_element_by_xpath("//a[contains(@onclick,'fdc_PromotionEnd')]").click()
		#self.driver.find_element_by_xpath("//a[contains(@onclick,'fdc_DeliveryEnd')]").click()
		retry_find_element_by_xpath(self.driver, "//a[contains(@onclick,'fdc_PromotionEnd')]").click()
		#retry_find_element_by_xpath(self.driver, "//div[@id='step04_OrdererInfo']")
		retry_find_element_by_xpath(self.driver, "//span[@id='deliveryPos']")
		retry_input_empty(self.driver, 'ordererUserName')
		retry_find_element_by_xpath(self.driver, "//a[contains(@onclick,'fdc_DeliveryEnd')]").click()

	def prepare_lastpage(self):
		payment_method = 1

		# 2 credit card / 222 kakao bank / 22 bank
		if payment_method == 1:
			self.driver.find_element_by_xpath("//input[@idgroup='2']").click()
		elif payment_method == 2:
			self.driver.find_element_by_xpath("//input[@idgroup='222']").click()
		elif payment_method == 3:
			self.driver.find_element_by_xpath("//input[@idgroup='22']").click()
			select = Select(self.driver.find_element_by_id("selBank"))
			# 50 KB / 11631 KEB / 57 NH / 11629 SH / 49 WOORI
			# 11634 POST / 11630 HANA / 11633 SC
			select.select_by_value("50")

		self.driver.find_element_by_id("cbxCancelFeeAgree").click()
		self.driver.find_element_by_id("chkinfoAgree").click()

	def change_value_by_id(self, vid):
		self.driver.execute_script("jgIdPerf={}".format(vid))

	def change_element_value_by_id(self, eid, v):
		self.driver.execute_script("document.getElementById('{}').value = '{}';".format(eid,v))

	def change_element_html_by_id(self, eid, html):
		self.driver.execute_script("document.getElementById('{}').innerHTML = \"{}\";".format(eid,html))

def retry_click_element_by_xpath(driver, xpath):
	while True:
		try:
			element = driver.find_element_by_xpath(xpath)
			element.click()
			break
		except:
			print("failed to click.", xpath)
			time.sleep(0.2)
	return element


def retry_find_element_by_xpath(driver, xpath):
	while True:
		element = driver.find_element_by_xpath(xpath)
		if element.is_displayed():
			break
		else:
			print("element is not displayed yet.", xpath)
			time.sleep(0.2)
	return element

def retry_input_empty(driver, inputid):
	while True:
		element = driver.find_element_by_id(inputid)
		if element.get_attribute('value') == '':
			print("input is empty yet.", inputid)
			time.sleep(0.2)
		else:
			break
	return

def retry_xpath_empty(driver, xpath):
	while True:
		element = driver.find_element_by_xpath(xpath)
		if element.get_attribute('innerHTML') == '':
			print("xpath is empty yet.", xpath)
			time.sleep(0.2)
		else:
			break
	return

