
import sys
import requests
import datetime
from datetime import timedelta
import time
import traceback
from threading import Thread

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import urllib
import re
import base64

from .selenium_yes24 import Selenium_yes24

class PerfDate(object):
	def __init__(self, date):
		mydatetime = datetime.datetime.strptime(date, "%Y-%m-%d")
		self.weekday = mydatetime.weekday()
		self.date = mydatetime.strftime("%Y%m%d")
		self.perftimes = None

	def setPerfTimes(self, perftimes):
		self.perftimes = perftimes

	def getPerfTimes(self):
		return self.perftimes

	def isPrefered(self, arr):
		if arr is None:
			return True

		for datestr in arr:
			d = datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M")
			if self.date == d.strftime("%Y%m%d"):
				return True
		return False

	def __repr__(self):
		whatday = ['MON','TUE','WED','THU','FRI','SAT','SUN'][self.weekday]
		return "---{}({})---".format(self.date, whatday)

class PerfTime(object):
	def __init__(self):
		#self.timeid = timeid
		#self.date = date
		#self.timeinfo = mydatetime.strftime("%H%M")
		#self.idhall = idhall
		self.seatdata = None
		self.layoutseats = None

	def dataSet(self, timeid, date, timeinfo, idhall):
		self.timeid = timeid
		self.date = date
		mydatetime = datetime.datetime.strptime(timeinfo, "%H시 %M분")
		self.timeinfo = mydatetime.strftime("%H%M")
		self.idhall = idhall

	#[{"perftimeid":"160","perfid":"36142","perfdesc":"\uc9c0\ucc3d\uc6b1","date1":"20200215","date1filter":"2020-02-15 18:00","date2":"2020-02-15","idtime":"1078036","idhall":"9596","status":"\uc2e0\uccad\uac00\ub2a5"}]
	def dataSet2(self, timeid, date, timeinfo, idhall):
		self.timeid = timeid
		self.date = date
		self.timeinfo = timeinfo
		self.idhall = idhall

	def __repr__(self):
		return "[{}] {} {}".format(self.timeid, self.date, self.timeinfo)

	def isPrefered(self, date, filter_time):
		if filter_time is None:
			return False

		if self.date == date and self.timeinfo == filter_time:
			return True

		return False

	def setSeatData(self, seatdata, layoutseats):
		self.seatdata = seatdata
		self.layoutset = {}
		for s in layoutseats:
			row = int(s)//100000
			col = int(s)%100000
			if row not in self.layoutset:
				self.layoutset[row] = [col]
			else:
				self.layoutset[row].append(col)

	def getPreferedSeat(self, count=2, prefer=None, serial=True, strict=True, sort='left'):
		myseatdata = self.seatdata
		#myseatdata = self.seatdata[::-1]
		#seatcount = len(self.seatdata)
		#myseatdata = self.seatdata[seatcount//2:]

		"""
		#print start
		seatlen = min(len(myseatdata), 5)
		for seat in myseatdata[:seatlen]:
			print(seat)
		extralen = len(myseatdata) - seatlen
		if extralen > 0:
			print('......({} more)'.format(extralen))
		#print end
		"""
		print("Totally...{} seats...".format(len(myseatdata)))

		if prefer is not None:
			print("prefer is not None")
			myseatdata = [seat for seat in myseatdata if seat.isSeatPrefered(prefer, self.layoutset)]

		if serial and len(myseatdata) > 1:
			first_seat = myseatdata[0]
			#serial check
			while len(myseatdata) > 1:
				seat1 = myseatdata[0]
				seat2 = myseatdata[1]
				if not seat1.isSeatSerial(seat2):
					myseatdata.remove(seat1)
				else:
					break

			if len(myseatdata) == 1:
				myseatdata = [first_seat]

		if len(myseatdata) == 0:
			print(self.timeid, ":seatdata is 0")
			return []
		elif len(myseatdata) < count:
			if strict:
				print(self.timeid, ":seatdata is less than", count, "(abort buying)")
				return []
			else:
				print(self.timeid, ":seatdata is less than", count, "(but buying)")
		else:
			if count == 1 and (sort == 'center' or sort == 'right'):
				print("You changed sort as {}..".format(sort))
				first = myseatdata[0]
				firstrow = []
				for s in myseatdata:
					if s.seat_row != first.seat_row:
						break
					firstrow.append(s)
				print(firstrow)
				if sort == 'center':
					myseatdata = [firstrow[len(firstrow)//2]]
				else:
					myseatdata = [firstrow[-1]]
			else: # left or invalid param
				myseatdata = myseatdata[0:count]

		return myseatdata

class Yes24(object):
	def __init__(self, idperf, idtime, idhall):
		self.session = requests.Session()
		self.idperf = idperf
		self.idtime = idtime
		self.idhall = idhall
		self.triedSeats = []
		#self.customerid = None
		#self.ipmanager = IPManager()

	def login(self, loginid, loginpw):
		self.loginid = loginid
		self.loginpw = loginpw
		URL = "http://ticket.yes24.com/Pages/Login/Ajax/AxLoginEnt.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'PLoginID':loginid, 'PPassword':loginpw}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[login]", r.status_code, r.reason, r.headers['Date'])
		print(r.text)
		#age = self.session.cookies['Mallinmall_CKMAG']
		#print('age:', age)
		#self.customerid = self.session.cookies['Mallinmall_CKMN']
		#print('customerid:',self.customerid)

	def login2(self, loginid, loginpw):
		self.loginid = loginid
		self.loginpw = loginpw

		URL = "https://www.yes24.com/Templates/FTLogin.aspx"
		r = self.session.get(URL)

		#Captcha check first
		if "FBLoginSub_panLoginCaptcha" in r.text:
			print("Captcha required...")
			return False

		soup = BeautifulSoup(r.text, "html.parser")
		fbtoken = soup.find('input', {'id':'FBLoginSub_hdfLoginToken'})
		fbtokenvalue = fbtoken['value']
		print('fbtokenvalue:',fbtokenvalue)

		now = datetime.datetime.now()
		nowtimestamp = int(now.timestamp()*1000)
		tobase64 = "{}|{}".format(nowtimestamp, fbtokenvalue)
		print(tobase64)
		fbloginhash = base64.b64encode(tobase64.encode('utf-8')).decode('utf-8')
		print('fbloginhash:',fbloginhash)

		#URL = "http://ticket.yes24.com/Pages/Login/Ajax/AxLoginEnt.aspx"
		#URL = "https://www.yes24.com/Templates/FTLogin.aspx?ReturnURL=http://ticket.yes24.com/"
		URL = "https://www.yes24.com/Templates/FTLogin.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		headers['origin'] = 'https://www.yes24.com'
		headers['referer'] = 'https://www.yes24.com/Templates/FTLogin.aspx'

		payload = {'SMemberID':loginid, 'SMemberPassword':loginpw}
		payload['FBLoginSub$hdfLoginToken'] = fbtokenvalue
		payload['FBLoginSub$hdfLoginHash'] = fbloginhash
		payload['LoginType'] = ''
		payload['RefererUrl'] = 'http://ticket.yes24.com'
		payload['AutoLogin'] = 1
		payload['LoginIDSave'] = 'Y'
		r = self.session.post(URL, headers=headers, data=payload, verify=False)
		print("[login]", r.status_code, r.reason, r.headers['Date'])

		if "yesPop('loginFailPop'" in r.text:
			msg = "Wrong id or password..({})".format(loginid)
			print(msg)
			self.notifyTelegram(message=msg)
			raise Exception("WRONG ID OR PASSWORD EXCEPTION...")
		elif "FBLoginSub_panLoginCaptcha" in r.text:
			print("Captcha required...")
			return False

		return True

	def login2_loop(self, loginid, loginpw):
		while True:
			ret = self.login2(loginid, loginpw)
			if ret:
				break
			else:
				print("Waiting 10seconds for next login try")
				time.sleep(10)
				continue

	def getUserInfo(self):
		## servicecookies
		self.servicecookies = ''
		for cookie in self.session.cookies:	
			if cookie.name == 'ServiceCookies':
				self.servicecookies = cookie.value
				print("ServiceCookies :", cookie.value)
				break

		## decode servicecookies
		print(self.servicecookies)
		print(base64.b64decode(self.servicecookies))
		decodedcookies = base64.b64decode(self.servicecookies).decode('euc-kr')

		infos = decodedcookies.split('`')
		self.customerid = infos[0]
		self.userid = infos[1]
		self.userage = infos[8]
		print('[{}][{}][{}]'.format(self.customerid, self.userid, self.userage))


	def checkRealname(self):
		URL = "http://ticket.yes24.com/Pages/Perf/Detail/Detail.aspx?IdPerf=30000"
		r = self.session.get(URL)

		soup = BeautifulSoup(r.text, "html.parser")
		i = soup.find('input', {'id':'HidlsNameCheck'})
		if i is None:
			print("[checkRealname] page load failed")
			return
		HidlsNameCheck = i['value']
		print('HidlsNameCheck:', HidlsNameCheck)
		if HidlsNameCheck == '1':
			print("REAL NAME NOT AUTH")
			msg = "[{}] REAL NAME NOT AUTH;;;".format(self.loginid)
			self.notifyTelegram(message=msg)
		else:
			print("REAL NAME OK")

	# To parse IdCustomer
	def getPerfSaleHtmlSeat(self, idtime, idhall):
		#1029754 6538
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/PerfSaleHtmlSeat.aspx?idTime={}&idHall={}&block=0&stMax=10&pHCardAppOpt=0".format(idtime, idhall)
		r = self.session.get(URL)
		print('[PerfSaleHtmlSeat]',r.status_code, r.reason, r.headers['Date'])
		#print(r.text)
		regex = re.compile("var IdCustomer = '([0-9]+)'")
		mo = regex.search(r.text)
		if mo != None:
			self.customerid = mo.group(1)
			print('customerid:',self.customerid)
		else:
			print("no customerid... abort")
			raise Exception("NO CUSTOMERID EXCEPTION...")

	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSaleState.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSeatRemain.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeNoSeatClass.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfSaleInfo.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfGuideView.aspx"

	def getGuideView(self):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfGuideView.aspx"
		payload = {'pIdPerf':self.idperf}
		r = self.session.post(URL, data=payload)
		print('[GuideView]',r.status_code, r.reason, r.headers['Date'])
		print(r.text)

	def getPerfTimeFromWang(self, date, filter_time=None):
		self.showcaptcha = True

		URL = "http://wangticket.com/yes24/read_perfs.php?perfid={}".format(self.idperf)
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = requests.get(URL, headers=headers)
		print('[Time Wang]',r.status_code, r.reason, r.headers['Date'])
		print(r.text)

		if r.text == "" or r.text == "[]":
			print("getPerfTimeFromWang not found")
			return []

		perftimes = []
		result = r.json()
		for perftime in result:
			self.showcaptcha = True if perftime['captcha'] == '1' else False
			timeid = perftime['idtime']
			if timeid == "0":
				continue
			date1 = perftime['date1']
			time1 = perftime['time1']
			idhall = perftime['idhall']
			myPerfTime = PerfTime()
			myPerfTime.dataSet2(timeid, date1, time1, idhall)
			if myPerfTime.isPrefered(date, filter_time):
				perftimes.append(myPerfTime)
				print(myPerfTime, "(filter found)")
				return [myPerfTime]

		if len(perftimes) > 0:
			print(perftimes[0])
		else:
			print("no available performance(wang)")
			
		return perftimes


	def _getPerfTime(self, date, filter_time=None):
		self.sel.playdate = date
		self.sel.playtime = filter_time

		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfTime.aspx"
		#URL = "http://m.ticket.yes24.com/Perf/Sale/Ajax/Perf/AxPerfTime.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		headers['Referer'] = 'http://ticket.yes24.com/Pages/Perf/Sale/PerfSaleProcess.aspx?IdPerf={}'.format(self.idperf)
		payload = {'pDay':date,'pIdPerf':self.idperf,'pIdCode':0,'pIsMania':0}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[Time All]", r.status_code, r.reason, r.headers['Date'])
		print(r.text)

		perftimes = []
		soup = BeautifulSoup(r.text, "html.parser")
		for li in soup.findAll('li'):
			timeid = li['value']
			timeinfo = li['timeinfo']
			idhall = li['idhall']
			myPerfTime = PerfTime()
			myPerfTime.dataSet(timeid, date, timeinfo, idhall)
			perftimes.append(myPerfTime)
			if myPerfTime.isPrefered(date, filter_time):
				print(myPerfTime, "(filter found)")
				return [myPerfTime]

		if len(perftimes) > 0:
			print(perftimes[0])
		return perftimes


	def getPerfTime(self, date, filter_time=None):
		EXCEPT_COUNT = 0
		while True:
			if EXCEPT_COUNT > 100:
				raise Exception("TOO MUCH EXCEPTION...")

			try:
				result = self._getPerfTime(date, filter_time)
			except:
				print(traceback.format_exc())
				print("failed to getPerfTime because of server problem")
				time.sleep(0.5)
				EXCEPT_COUNT = EXCEPT_COUNT + 1
				continue

			return result

	def _get442Page(self):
		URL = "https://m.ticket.yes24.com:442/Perf/Sale/PerfSaleProcess.aspx?IdPerf={}".format(self.idperf)
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}

		s = datetime.datetime.now() ## for DEBUG
		r = self.session.get(URL, headers=headers)
		e = datetime.datetime.now() ## for DEBUG
		print("[get442Page]", r.status_code, r.reason, r.headers['Date'], r.headers['content-length'], (e-s))
		#print(r.text)

		if '날짜/시간 선택' in r.text:
			print("Ok to access 442 !")
		else:
			print("Fail to access 442 !")
			print(r.text)
		return

	def get442Page(self):
		while True:
			try:
				self._get442Page()
				return
			except:
				print(traceback.format_exc())
				print("failed to get442Page because of server problem")
				time.sleep(0.5)
				continue

	def _getHallMapRemain(self, idhall, idtime):
		URL = "http://ticket.yes24.com/OSIF/Book.asmx/GetHallMapRemain"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'idHall':idhall, 'idTime':idtime}
		r = self.session.post(URL, headers=headers, data=payload)
		print('[HallMap]', r.status_code, r.reason, r.headers['Date'])
		print(r.text)

		root = ET.fromstring(r.text)
		ns = "{http://tempuri.org/}"

		blockremain = root.findtext('{}BlockRemain'.format(ns))
		for block in blockremain.split('^'):
			if block == '':
				continue
			(block_num,remain) = block.split('@')
			if int(remain) > 0:
				print(block_num, remain)
				return block_num
		return -1


	def getHallMapRemain(self, idhall, idtime):
		EXCEPT_COUNT = 0
		while True:
			if EXCEPT_COUNT > 100:
				raise Exception("TOO MUCH EXCEPTION...")

			try:
				result = self._getHallMapRemain(idhall, idtime)
			except:
				print(traceback.format_exc())
				print("failed to getHallMapRemain because of server problem")
				time.sleep(0.5)
				EXCEPT_COUNT = EXCEPT_COUNT + 1
				continue

			return result


	def getSaleState(self):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSaleState.aspx"
		payload = {'pIdTime':self.idtime}
		r = self.session.post(URL, data=payload)
		print('[HallMap]', r.status_code, r.reason, r.headers['Date'])
		#print(r.text)



	def _getSeatData(self, block, idhall, idtime, idcustomer):
		URL = "http://ticket.yes24.com/OSIF/Book.asmx/GetBookWhole"
		#URL = "http://m.ticket.yes24.com/OSIF/Book.asmx/GetBookWhole"
		payload = {'idHall':idhall,'idTime':idtime,'block':block,'channel':1,'idCustomer':idcustomer,'idOrg':1}
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		#headers['Host'] = 'ticket.yes24.com'
		#headers['Origin'] = 'http://ticket.yes24.com'
		#headers['X-Requested-With'] = 'XMLHttpRequest'
		headers['Pragma'] = 'no-cache'
		r = self.session.post(URL, headers=headers, data=payload)
		print("[Seat]", r.status_code, r.reason, r.headers['Date'], end='\r')
		#print(r.text)

		root = ET.fromstring(r.text)
		ns = "{http://tempuri.org/}"
		#print(root.findtext('{}IdTime'.format(ns)))
		#print(root.findtext('{}Block'.format(ns)))
		layout = root.findtext('{}Layout'.format(ns))
		self.layoutseats = re.findall(r'<DIV.*? value=\"([0-9]+)\"></DIV>', layout)
		#print(layoutseats)
		blockseat = root.findtext('{}BlockSeat'.format(ns))
		seatdata = []
		for seat in blockseat.split('^'):
			if seat == '':
				continue
			mySeat = Seat(seat)
			if mySeat.idlock != '0': #if already bought
				continue
			if mySeat in self.triedSeats: #if already tried
				print("already tried...", mySeat)
				continue
			seatdata.append(mySeat)

		seatdata.sort()

		return seatdata


	def getSeatData(self, block, idhall, idtime, idcustomer):
		EXCEPT_COUNT = 0
		while True:
			if EXCEPT_COUNT > 100:
				raise Exception("TOO MUCH EXCEPTION...")

			try:
				result = self._getSeatData(block, idhall, idtime, idcustomer)
			except:
				print(traceback.format_exc())
				print("failed to getSeatData because of server problem")
				time.sleep(0.5)
				EXCEPT_COUNT = EXCEPT_COUNT + 1
				continue

			return result


	def _lockSeat(self, block, date, idtime, seats):
		if len(seats) == 0:
			return False

		self.triedSeats.extend(seats)

		mytoken = ",".join([seat.seatid for seat in seats])
		print(date, idtime, mytoken)
		[print(seat) for seat in seats]
		#myptags = "".join([seat.getPTag() for seat in seats])
		#print(myptags)

		URL = "http://ticket.yes24.com/OSIF/Book.asmx/Lock"
		payload = {'name':self.customerid,'idTime':idtime,'token':mytoken,'Block':block}
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[Lock]", r.status_code, r.reason, r.headers['Date'])
		print(r.text)

		root = ET.fromstring(r.text)
		ns = "{http://tempuri.org/}"
		responsecode = root.findtext('{}Code'.format(ns))
		if responsecode != 'None':
			print("Lock failed")
			return False

		print("Lock succeed.....Expires in 5min(NOW:{})".format(datetime.datetime.now()))

		params = urllib.parse.urlencode(payload)
		getURL = URL + "?" + params
		print(getURL)
		print("")
		return True


	def lockSeat(self, block, date, idtime, seats):
		EXCEPT_COUNT = 0
		while True:
			if EXCEPT_COUNT > 100:
				raise Exception("TOO MUCH EXCEPTION...")

			try:
				result = self._lockSeat(block, date, idtime, seats)
			except:
				print(traceback.format_exc())
				print("failed to lockSeat because of server problem")
				time.sleep(0.5)
				EXCEPT_COUNT = EXCEPT_COUNT + 1
				continue

			return result


	def setLastPage(self, date, idtime, seats):
		self.classes = "-".join([seat.grade for seat in seats])
		seatend = self.seatEnd(idtime, self.classes)
		self.sel.change_element_html_by_id('ulSeatSpace', seatend)

		self.idseats = "-".join([seat.seatid for seat in seats])
		etcfee = self.getEtcFee(idtime, len(seats))
		self.sel.change_element_html_by_id('divBookingFee', etcfee)

		method = self.getDeliveryMethod(idtime, date, self.idperf, "")
		self.sel.change_element_html_by_id('deliveryPos', method)
		self.sel.driver.execute_script("var rdos = document.getElementsByName('rdoDelivery');if(rdos.length>0)rdos[0].click();")

		seats_desc = "".join(["<span>{}</span>".format(seat.desc) for seat in seats])
		self.sel.change_element_html_by_id('tk_seat', seats_desc)

		self.sel.change_value_by_id(self.idperf)
		self.sel.change_element_value_by_id('IdTime', idtime)
		self.sel.change_element_value_by_id('IdSeatClassPrice', self.idseatclassprice)
		self.sel.change_element_value_by_id('IdSeatClass', self.idseatclass)
		self.sel.change_element_value_by_id('IdSeat', self.idseats)
		print("READY!!!!!!!!!!!!!!!!!!! BOOK FAST!!!!!")


	"""
	#<tr deliveryno idpromotion='15962337'><td class='l' >금토일공휴일-장애인할인(4-6급/1인1매)50% <font color='red'>[배송불가]</font><br /></td><td>75,000</td><td><select Id=selPromotion15962337 amount='75000' onchange=fdc_PreCheckPromotion('15962337','34562','84','T','F',1,1,this);><option value=0>0매</option><option value=1>1매</option></select></td><td><img id='TimgAlertPro15962337' alt='할인 설명툴팁 보기' src='http://tkfile.yes24.com/img/perfsale/btn_q.gif' notice='복지 4-6급(1인 1매) / 티켓 수령 시 관람자 
&lt;br /&gt;본인의 복지카드 확인 / 본인 미관람 또는 
&lt;br /&gt;미지참시 차액지불' style='cursor:hand;cursor:pointer;' onclick='fdc_ShowPromotionTooltip(this);' /></td></tr>
fdc_PreCheckPromotion('15962389','34556','84','T','F',1,1,this);
function fdc_PreCheckPromotionBase(jpIdPromotion, jpIdCode, jpIdAuth, jpIsOverlap, jpIsLimit, jpLimitNo, jpGroupIndex, jpSelObj)
	"""
	def _getPromotion(self, seldate, idtime, promo, count):
		#if promo == "":
		#	return

		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PromotionByClass.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
		payload = {'pIdTime': idtime, 'pSelDt': seldate, 'pSeat':self.idseatclass, 'pIdCode': '', 'pHCardAppOpt': 0}
		print("payload:", payload)
		r = self.session.post(URL, headers=headers, data=payload)
		print("[Promotion]", r.status_code, r.reason, r.headers['Date'])

		p = re.compile(r'<img.*?/>') # some char ruin the text so...
		mytext = p.sub('', r.text)
		mytext = mytext.replace('display:none','display: block')
		print(mytext)

		soup = BeautifulSoup(mytext, "html.parser")
		trs = soup.findAll('tr')
		for tr in trs:
			if 'idpromotion' in tr.attrs:
				idpromotion = tr.attrs['idpromotion']
				promotionstr = tr.text
				if (promo != "" and promo in promotionstr) or (tr.find('option', {'selected': True})):

					print(idpromotion)
					print(promotionstr)
					select = tr.find('select')
					onchange = select.attrs['onchange']
					print(onchange)
					splits = onchange.split(',')
					idcode = splits[1].replace("'", "")
					idauth = splits[2].replace("'", "")
					overlap = splits[3].replace("'", "")
					limit = splits[4].replace("'", "")
					limitno = int(splits[5])

					## SelPromotionStorage
					promotion = "<input type='hidden' id='chkPro{}' value='{}' addinfo='{}-{}'>".format(idpromotion, idcode, overlap, limitno)
					print(promotion)
					self.sel.change_element_html_by_id('SelPromotionStorage', promotion)

					## divPromotionList
					self.sel.change_element_html_by_id('divPromotionList', mytext)
					selpromoid = "selPromotion{}".format(idpromotion)
					self.sel.change_element_int_value_by_id(selpromoid, count)
					break


	def getPromotion(self, seldate, idtime, promo, count):
		EXCEPT_COUNT = 0
		while True:
			if EXCEPT_COUNT > 100:
				raise Exception("TOO MUCH EXCEPTION...")

			try:
				result = self._getPromotion(seldate, idtime, promo, count)
			except:
				print(traceback.format_exc())
				print("failed to getPromotion because of server problem")
				time.sleep(0.5)
				EXCEPT_COUNT = EXCEPT_COUNT + 1
				continue

			return result


	def getYesPays(self, money):
		if money == 0:
			return

		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/YesPays.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pPayType': 0}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[YesPays]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)

		soup = BeautifulSoup(r.text, "html.parser")

		self.rcvYesDepositv = 0
		rcvYesDeposit = soup.find('input', {'id':'rcvYesDeposit'})
		if rcvYesDeposit is not None:
			self.rcvYesDepositv = int(rcvYesDeposit['value'])
			#idcode ??

		#self.rcvYesPointv = 0
		#rcvYesPoint = soup.find('input', {'id':'rcvYesPoint'})
		#if rcvYesPoint is not None:
		#	self.rcvYesPointv = int(rcvYesPoint['value'])
		#	#idcode ??

		self.rcvYesGiftv = 0
		self.rcvYesGiftc = 0
		rcvYesGift = soup.find('input', {'id':'rcvYesGift'})
		if rcvYesGift is not None:
			self.rcvYesGiftv = int(rcvYesGift['value'])
			self.rcvYesGiftc = int(rcvYesGift['totalcount'])

		print("YesDeposit:",self.rcvYesDepositv)
		#print("YesPoint:", self.rcvYesPointv)
		print("YesGift:", self.rcvYesGiftv, self.rcvYesGiftc)
		if (self.rcvYesDepositv < money) and (self.rcvYesGiftv < money):
			print("YesPays not enough for checkout\n"*10)
			print("(BUT THIS API can be wrong when server is busy)")
			#raise Exception("YESPAYS NOT ENOUGH EXCEPTION...")

	def getYesGift(self, money, giftuse):
		if money == 0:
			return

		#if self.rcvYesDepositv >= money:
		#	self.sel.change_element_int_value_by_id('txtYesDeposit', money)
		#	return

		#if self.rcvYesPointv >= money:
		#	## not implemented
		#	return


		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Popup/Ajax/YesGiftUse.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = self.session.post(URL, headers=headers)
		print("[YesGift]", r.status_code, r.reason, r.headers['Date'])
		print(r.text)
		self.sel.yesgift = r.text
		self.sel.giftuse = giftuse

		total_money = money
		usedgiftinfo = ""

		soup = BeautifulSoup(r.text, "html.parser")
		trs = soup.findAll('tr')
		if trs is not None:
			for tr in trs:
				giftkey = tr['giftkey']
				if giftuse != '' and giftkey.split('#')[1] not in giftuse:
					print("skip using gift:", giftkey)
					continue
				amount = int(tr['limitamount'])
				if total_money > amount:
					using_money = amount
				else:
					using_money = total_money

				usedgiftinfo = usedgiftinfo + "{}#{}^".format(giftkey, using_money)
				#print(giftkey, amount, using_money)
				total_money = total_money - using_money
				if total_money == 0:
					break
				
		print(usedgiftinfo)
		script = "fdc_PopupYesGiftUseEnd({},'{}');".format(money-total_money, usedgiftinfo)
		print(script)
		self.sel.driver.execute_script(script)

	def setDefaultDeliveryMethod(self, date, idtime, seats, rows):
		WillCallOK = False
		for seat in seats:
			if seat.seat_row in rows:
				WillCallOK = True

		if not WillCallOK:
			print("no need to change delivery method by default")
			return
		else:
			print("need to change delivery method by default")

		method = "<input type='radio' name='rdoDelivery' id='rdoDeliveryBase' value='-1' price='0' datedifference='' onclick='fdc_DeliveryMethodChange(this);' /><label for='rdoDeliveryBase'>현장수령</label>"
		self.sel.change_element_html_by_id('deliveryPos', method)
		self.sel.driver.execute_script("var rdos = document.getElementsByName('rdoDelivery');if(rdos.length>0)rdos[0].click();")

	def checkout(self):
		ret = self.sel.checkout()
		if ret:
			self.sel.handleBookSuccess()
			msg = "[{}][{}] {}".format(self.userid, self.sel.bookno, self.sel.tkseat)
			self.notifyTelegram(message=msg)
			self.myOrderList()
			return True
		else:
			print("Finding another seat!!!!!!!!")
			return False

	def myOrderList(self):
		for i in range(0,100):
			try:
				isfound = self.myOrderList_ex()
				if isfound:
					break
				time.sleep(1)
				continue
			except KeyboardInterrupt:
				raise
			except Exception as e:
				#print(traceback.format_exc())
				print("Exception happen in myOrderList...", str(e))
				time.sleep(1)
				continue

	def myOrderList_ex(self):
		URL = "http://ticket.yes24.com/Pages/MyPage/Ajax/MyOrder/MyOrderList.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}

		now = datetime.datetime.now()
		today = now.strftime("%Y-%m-%d")
		m3_ago = (now - timedelta(days=90)).strftime("%Y-%m-%d")

		payload = {'pDispGubun': '1', 'pStartDT':m3_ago, 'pEndDT':today, 'pCurPage':1, 'pPageSize':10}
		print(payload)
		r = self.session.post(URL, headers=headers, data=payload)
		print("[myOrderList]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)

		try:
			findingbookno = self.sel.bookno
			isfound = False
		except AttributeError: # if not declared
			print("bookno is empty. must be testing!")
			findingbookno = "TESTING"
			isfound = True

		soup = BeautifulSoup(r.text, "html.parser")
		trs = soup.find_all('tr')
		for tr in trs[1:]:
			ainfo = tr.find('a')
			idorder = ainfo.attrs['idorder']

			tds = tr.find_all('td')
			bookno = tds[1].text
			perfname = tds[2].text
			perfdate = tds[3].text
			count = tds[4].text
			status = tds[5].text
			print("[{}({})][{}][{}][{}][{}]".format(bookno, idorder, perfname, perfdate, count, status))
			if findingbookno in bookno:
				print("Found Booking you just booked")
				isfound = True
			self.myOrderView(idorder=idorder)

		return isfound

	def myOrderView(self, idorder):
		for i in range(0,10):
			try:
				isfound = self.myOrderView_ex(idorder)
				if isfound:
					break
				time.sleep(1)
				continue
			except KeyboardInterrupt:
				raise
			except Exception as e:
				print(traceback.format_exc())
				print("Exception happen in myOrderView...", str(e))
				time.sleep(1)
				continue

	def myOrderView_ex(self, idorder):
		self.idorder = idorder
		URL = "http://ticket.yes24.com/Pages/MyPage/MyOrderTicketView.aspx?IdOrder={}".format(self.idorder)
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = self.session.get(URL, headers=headers)
		print("[myOrderView]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)

		soup = BeautifulSoup(r.text, "html.parser")

		#### BANK OR NONE??
		cancelbtn0 = soup.find('a', {'id':'imgCancelPayNone'})
		cancelbtn1 = soup.find('a', {'id':'imgCancelPayBank'})
		cancelbtn2 = soup.find('a', {'id':'imgCancelPayCard'})
		if cancelbtn0 is not None:
			print("Not paid yet!")
			self.canceltype = "NONE"
			self.isallcancel = "TRUE"
		elif cancelbtn1 is not None:
			print("Already paid by bank")
			self.canceltype = "BANK"
			self.isallcancel = "TRUE"
		elif cancelbtn2 is not None:
			print("Already paid by card")
			self.canceltype = "CARD"
			self.isallcancel = "TRUE"
		else:
			print(r.text)
			print("Booking is not cancelable anymore!!")
			return True

		print("canceltype", self.canceltype)
		print("isallcancel", self.isallcancel)

		### 
		table = soup.find('table', {'id':'tblBookingSeatInfo'})
		whattd = {'style':'display:none;'}
		if self.canceltype == "BANK" or self.canceltype == "CARD":
			whattd = {'class':'ri'}
		tds = table.findAll('td', whattd)
		if tds is None or len(tds) == 0:
			print("Cannot find order")
			print(r.text)
			return False

		TKinfo = ''
		for idx, td in enumerate(tds):
			infos = ['Seat_Option', 'Seat_Pay', 'Seat_IdTrans', 'Seat_IdTime', 'Seat_IdSeat', 'Seat_PerfDate', 'Seat_Price', 'Seat_PrintNo', 'Seat_SeatFormat']
			for info in infos:
				colname = info + str(idx+1)
				seatinfo = td.find('input', {'id':colname})
				TKinfo = TKinfo + seatinfo['value'] + '#'
			TKinfo = TKinfo + 'true^'

		print("ticketinfo:", TKinfo)
		self.ticketinfo = TKinfo

		## PAY YET
		## mCancelType : NONE
		## mIsAllCancel : TRUE
		return True


	def browser_login(self, x=0, y=0, headless=False):
		self.sel = Selenium_yes24(idperf=self.idperf)
		try:
			self.sel.startChrome(headless=headless)
		except:
			print("chrome issue!!!")
			msg = "Chrome start ISSUE!(retry)"
			self.notifyTelegram(message=msg)
			raise Exception("chrome issue")
		#self.sel.login(userid=self.loginid, userpw=self.loginpw)
		self.sel.login2(userid=self.loginid, userpw=self.loginpw, cookies=self.session.cookies)

	def browser_openSample(self, idperf, idtime):
		self.sel.openBlank()
		self.sel.openPerf(idperf, idtime)

	def browser_wait_last_page(self, payment_method=1, deposit=0, giftuse='', captcha_self=False):
		self.sel.goLastPage()
		self.sel.prepare_lastpage(payment_method=payment_method, showcaptcha=self.showcaptcha)
		self.getYesGift(money=deposit, giftuse=giftuse)
		self.sel.handleCaptcha(captcha_self=captcha_self)

	def _seatEnd(self, idtime, classes):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSeatFlashEnd.aspx"
		#URL = "http://m.ticket.yes24.com/Perf/Sale/Ajax/Perf/AxTimeSeatFlashEnd.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime': idtime, 'PCntClass':classes}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[seatEnd]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)
		#<li class='grade'><div classbyte='T82$188$174'><strong class='c_name'>R석</strong> <span class='c_price'>130,000원</span><select id='selSeatClass' price='130000'><option selected value='2'>2매</option></select></div></li>

		soup = BeautifulSoup(r.text, "html.parser")
		self.classbyte = soup.find('div')['classbyte']
		self.price = int(soup.find('select', {"id":"selSeatClass"})['price'] )
		self.ticketcnt = soup.find('option')['value']
		self.idseatclassprice = "{}-{}-{},".format(self.classbyte, self.ticketcnt, self.price)
		self.idseatclass = "{}-{},".format(self.classbyte, self.ticketcnt)
		#print('IdSeatClassPrice:', self.idseatclassprice)
		#print('IdSeatClass:', self.idseatclass)
		return r.text

	def seatEnd(self, idtime, classes):
		EXCEPT_COUNT = 0
		while True:
			if EXCEPT_COUNT > 100:
				raise Exception("TOO MUCH EXCEPTION...")

			try:
				result = self._seatEnd(idtime, classes)
			except:
				print(traceback.format_exc())
				print("failed to seatEnd because of server problem")
				time.sleep(0.5)
				EXCEPT_COUNT = EXCEPT_COUNT + 1
				continue

			return result


	def _getEtcFee(self, idtime, count):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/EtcFee.aspx"
		#URL = "http://m.ticket.yes24.com/Perf/Sale/Ajax/Perf/AxEtcFee.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime': idtime, 'pSeatCnt': count, 'pFreeCountOfCoupon': 0, 'pFreeCountOfGiftTicket': 0}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[EtcFee]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)
		#<input type=hidden id=EtcFees value='69#2000^' /><input type=hidden id=EtcFeeAmount value='2000' /><input type=hidden id=EtcValidTicketCnt value='2' />

		soup = BeautifulSoup(r.text, "html.parser")
		self.feetype = soup.find('input', {"id": "EtcFees"})['value']
		self.feeamount = soup.find('input', {"id": "EtcFeeAmount"})['value']
		#print(self.feetype)
		#print(self.feeamount)
		return r.text

	def getEtcFee(self, idtime, count):
		EXCEPT_COUNT = 0
		while True:
			if EXCEPT_COUNT > 100:
				raise Exception("TOO MUCH EXCEPTION...")

			try:
				result = self._getEtcFee(idtime, count)
			except:
				print(traceback.format_exc())
				print("failed to getEtcFee because of server problem")
				time.sleep(0.5)
				EXCEPT_COUNT = EXCEPT_COUNT + 1
				continue

			return result


	## http://ticket.yes24.com/Pages/Perf/Sale/Scripts/ps_divControls.js?v3=75
	## fdc_CheckWillCall()
	def _getDeliveryMethod(self, idtime, date, idperf, idclass):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/DeliveryMethod.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime':idtime, 'pBaseDate':date, 'pIdPerf':idperf, 'pIdClass':idclass}
		r = self.session.post(URL, headers=headers, data=payload)
		print('[DeliveryMethod]',r.status_code, r.reason, r.headers['Date'])
		print(r.text)
		return r.text


	def getDeliveryMethod(self, idtime, date, idperf, idclass):
		EXCEPT_COUNT = 0
		while True:
			if EXCEPT_COUNT > 100:
				raise Exception("TOO MUCH EXCEPTION...")

			try:
				result = self._getDeliveryMethod(idtime, date, idperf, idclass)
			except:
				print(traceback.format_exc())
				print("failed to getDeliveryMethod because of server problem")
				time.sleep(0.5)
				EXCEPT_COUNT = EXCEPT_COUNT + 1
				continue

			return result


	def getDeliveryInfo(self):
		try:
			URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/DeliveryUserInfo.aspx"
			headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
			r = self.session.post(URL, headers=headers)
			print('[Delivery]',r.status_code, r.reason, r.headers['Date'])
			#print(r.text)

			soup = BeautifulSoup(r.text, "html.parser")
			username = soup.find('input', {'id':'LUAddr_UserName'})['value']
			mobile1 = soup.find('input', {'id':'LUAddr_Mobile1'})['value']
			mobile2 = soup.find('input', {'id':'LUAddr_Mobile2'})['value']
			mobile3 = soup.find('input', {'id':'LUAddr_Mobile3'})['value']
			mailh = soup.find('input', {'id':'LUAddr_MailH'})['value']
			maild = soup.find('input', {'id':'LUAddr_MailD'})['value']
			zipcode = soup.find('input', {'id':'LUAddr_ZipCode1'})['value']
			address1 = soup.find('input', {'id':'LUAddr_Address1'})['value']
			address2 = soup.find('input', {'id':'LUAddr_Address2'})['value']

			mobile = "{}-{}-{}".format(mobile1, mobile2, mobile3)
			email = "{}@{}".format(mailh, maild)
			print("[{}] [{}] [{}]".format(username, mobile, email))
			print("[{}] [{}] [{}]".format(zipcode, address1, address2))

			if mobile1 == '' or mobile2 == '' or mobile3 == '':
				print("no mobile number... \n"*10)
				msg = "[{}] no mobile number...".format(self.loginid)
				self.notifyTelegram(message=msg)

			if mailh == '' or maild == '':
				print("no email... \n"*10)
				msg = "[{}] no email...".format(self.loginid)
				self.notifyTelegram(message=msg)

			if zipcode == '' or address1 == '' or address2 == '':
				print("no address... \n"*10)
				msg = "[{}] no address...".format(self.loginid)
				self.notifyTelegram(message=msg)

		except:
			print(traceback.format_exc())
			print("failed to getDeliveryInfo...but not critical..\n"*10)

	def getPayMethod(self, idtime, date):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PayMethod.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime':idtime, 'pBaseDate':date, 'pIsMPoint':0}
		r = self.session.post(URL, headers=headers, data=payload)
		print('[PayMethod]',r.status_code, r.reason, r.headers['Date'])
		print(r.text)

	def getMyOrders(self, date=None):
		URL = "http://ticket.yes24.com/Pages/MyPage/Ajax/MyOrder/MyOrderList.aspx"
		payload = {'pDispGubun': 1, 'pStartDT':'2018-10-14', 'pEndDT':'2018-11-14', 'pCurPage':1, 'pPageSize':20}
		r = self.session.post(URL, data=payload)
		print("[MyOrders]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)

		orderlist = []
		soup = BeautifulSoup(r.text, "html.parser")
		for a in soup.findAll('a', {"class": "orderticketview"}):
			idorder = a['idorder']
			if idorder not in orderlist:
				orderlist.append(idorder)

		for order in orderlist:
			print(order)
			self.getMyOrderTicket(orderid=order)

	def getMyOrderTicket(self, orderid):
		URL = "http://ticket.yes24.com/Pages/MyPage/MyOrderTicketPrint.aspx?IdOrder={}&IdPackOrd=".format(orderid)
		r = self.session.post(URL)
		print("[Ticket]", r.status_code, r.reason, r.headers['Date'])
		#print(r.text)
		soup = BeautifulSoup(r.text, "html.parser")
		info = str( soup.find('div', {"class": "blu_list"}) )
		print(info)

	def notifyTelegram(self, message):
		try:
			message = "[y][{}]".format(self.pcid) + message
			URL = "http://wangticket.com/melon/send_message.php?to={}&message={}".format(self.to, message)
			headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"}
			r = requests.get(URL, headers=headers)
			print("[notifyTelegram]", r.status_code, r.reason, r.headers['Date'])
			#print(r.text)
		except Exception as err:
			print("Exception happen in notifyTelegram...", str(err))

	def upload_log(self, filename, userid, pcname):
		URL = "https://wangticket.com/yes24/log_uploader.php"
		headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"}
		files = {'myfile': open('logs/'+filename, 'rb')}
		(filename0, filename1) = filename.split('.')
		payload = {}
		payload['filename'] = "{}({})({}).{}".format(filename0, userid, pcname, filename1)
		r = requests.post(URL, files=files, data=payload, headers=headers)
		print("[upload_log]", r.status_code, r.reason, r.headers['Date'])
		print(r.text)

class Seat(object):
	def __init__(self, seat):
		ticket = seat.split('@')
		self.seatid = ticket[0]
		self.seat_row = int(self.seatid)//100000
		self.seat_col = int(self.seatid)%100000
		self.idlock = ticket[2]
		self.desc = ticket[3]
		self.price = ticket[4]
		self.grade = ticket[5]

	def __repr__(self):
		return "{} / lock:{} / {} / {} / {}".format(self.seatid, self.idlock, self.desc, self.price, self.grade)

	def getPTag(self):
		return '<p id="C{}" class="txt2" name="cseat" grade="{}">{}</p>'.format(self.seatid, self.grade, self.desc)

	def __eq__(self, other):
		return self.seatid == other.seatid

	def __lt__(self, other):
		return int(self.seatid) < int(other.seatid)

	def isSeatPrefered(self, prefer, layoutset):
		(row1, col1, row2, col2) = prefer
		# relative prefer check
		if type(col1)==float and type(col2)==float:
			# ROW
			preferrows = list(layoutset)[row1-1:row2]
			if self.seat_row not in preferrows:
				return False
			rowarr = layoutset[self.seat_row]

			# COL
			leftidx = int(len(rowarr)*col1)
			left = rowarr[leftidx]
			rightidx = int(len(rowarr)*col2)
			rightidx = len(rowarr)-1 if rightidx >= len(rowarr) else rightidx
			right = rowarr[rightidx]
			if left <= self.seat_col and self.seat_col <= right:
				return True
			return False

		# t600030 : 4row, 9th seat
		# t1200037 : 10row, 16th seat
		#if self.seat_row >= 6 and self.seat_row <= 20 and self.seat_col >= 30 and self.seat_col <= 53: # TEST
		if self.seat_row >= row1 and self.seat_row <= row2 and self.seat_col >= col1 and self.seat_col <= col2: # REAL
			return True
		return False

	def isSeatSerial(self, other):
		if self.seat_row != other.seat_row:
			return False
		elif abs(self.seat_col-other.seat_col) == 1:
			return True
		else:
			return False



