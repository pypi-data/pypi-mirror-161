
import sys
import requests
import datetime
import time
import traceback
from threading import Thread

from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import urllib
import re

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
	def __init__(self, timeid, date, timeinfo, idhall):
		self.timeid = timeid
		self.date = date
		mydatetime = datetime.datetime.strptime(timeinfo, "%H시 %M분")
		self.timeinfo = mydatetime.strftime("%H:%M")
		self.idhall = idhall
		self.seatdata = None

	def __repr__(self):
		return "[{}] {} {}".format(self.timeid, self.date, self.timeinfo)

	def isPrefered(self, arr):
		if arr is None:
			return True

		for datestr in arr:
			d = datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M")
			if self.date == d.strftime("%Y%m%d") and self.timeinfo == d.strftime("%H:%M"):
				return True
		return False

	def setSeatData(self, seatdata):
		self.seatdata = seatdata

	def getPreferedSeat(self, count=2, prefer=True, serial=True, strict=True):
		myseatdata = self.seatdata
		#myseatdata = self.seatdata[::-1]
		#seatcount = len(self.seatdata)
		#myseatdata = self.seatdata[seatcount//2:]

		#print start
		seatlen = min(len(myseatdata), 5)
		for seat in myseatdata[:seatlen]:
			print(seat)
		extralen = len(myseatdata) - seatlen
		if extralen > 0:
			print('......({} more)'.format(extralen))
		#print end

		if prefer:
			myseatdata = [seat for seat in myseatdata if seat.isSeatPrefered()]

		if serial:
			#serial check
			while len(myseatdata) > 1:
				seat1 = myseatdata[0]
				seat2 = myseatdata[1]
				if not seat1.isSeatSerial(seat2):
					myseatdata.remove(seat1)
				else:
					break

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
			myseatdata = myseatdata[0:count]

		return myseatdata

class Yes24(object):
	def __init__(self, idperf, idtime, idhall):
		self.session = requests.Session()
		self.idperf = idperf
		self.idtime = idtime
		self.idhall = idhall
		#self.customerid = None
		#self.ipmanager = IPManager()

	def login(self, loginid, loginpw):
		self.loginid = loginid
		self.loginpw = loginpw
		URL = "https://ticket.yes24.com/Pages/Login/Ajax/AxLoginEnt.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'PLoginID':loginid, 'PPassword':loginpw}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[login]", r.status_code, r.reason)
		print(r.text)
		#age = self.session.cookies['Mallinmall_CKMAG']
		#print('age:', age)
		self.customerid = self.session.cookies['Mallinmall_CKMN']
		print('customerid:',self.customerid)

	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSaleState.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSeatRemain.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeNoSeatClass.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfSaleInfo.aspx"
	#URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfGuideView.aspx"

	
	def getGuideView(self):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfGuideView.aspx"
		payload = {'pIdPerf':self.idperf}
		r = self.session.post(URL, data=payload)
		print('[GuideView]',r.status_code, r.reason)
		print(r.text)

	def getPerfTime(self, date, filter_array=None):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/PerfTime.aspx"
		#URL = "http://m.ticket.yes24.com/Perf/Sale/Ajax/Perf/AxPerfTime.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pDay':date,'pIdPerf':self.idperf,'pIdCode':0,'pIsMania':0}
		r = self.session.post(URL, headers=headers, data=payload)
		#print("[Time All]", r.status_code, r.reason)
		#print(r.text)

		perftimes = []
		soup = BeautifulSoup(r.text, "html.parser")
		for li in soup.findAll('li'):
			timeid = li['value']
			timeinfo = li['timeinfo']
			idhall = li['idhall']
			myPerfTime = PerfTime(timeid, date, timeinfo, idhall)
			if myPerfTime.isPrefered(filter_array):
				print(myPerfTime)
				perftimes.append(myPerfTime)

		return perftimes


	def getHallMapRemain(self, idhall, idtime):
		URL = "http://ticket.yes24.com/OSIF/Book.asmx/GetHallMapRemain"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'idHall':idhall, 'idTime':idtime}
		r = self.session.post(URL, headers=headers, data=payload)
		print('[HallMap]', r.status_code, r.reason)
		print(r.text)

		root = ET.fromstring(r.text)
		ns = "{http://tempuri.org/}"

		blockremain = root.findtext('{}BlockRemain'.format(ns))
		for block in blockremain.split('^'):
			if block == '':
				continue
			(block_num,remain) = block.split('@')
			print(block_num, remain)
			if int(remain) > 0:
				return block_num
		return -1

	def getSaleState(self):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSaleState.aspx"
		payload = {'pIdTime':self.idtime}
		r = self.session.post(URL, data=payload)
		print('[HallMap]', r.status_code, r.reason)
		#print(r.text)

	def getSeatData(self, block, idhall, idtime, idcustomer):
		URL = "http://ticket.yes24.com/OSIF/Book.asmx/GetBookWhole"
		#URL = "http://m.ticket.yes24.com/OSIF/Book.asmx/GetBookWhole"
		payload = {'idHall':idhall,'idTime':idtime,'block':block,'channel':1,'idCustomer':idcustomer,'idOrg':1}
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[Seat]", r.status_code, r.reason, r.headers['Date'], end='\r')
		#print(r.text)

		root = ET.fromstring(r.text)
		ns = "{http://tempuri.org/}"
		#print(root.findtext('{}IdTime'.format(ns)))
		#print(root.findtext('{}Block'.format(ns)))
		blockseat = root.findtext('{}BlockSeat'.format(ns))
		seatdata = []
		for seat in blockseat.split('^'):
			if seat == '':
				continue
			mySeat = Seat(seat)
			if mySeat.idlock != '0': #if already bought
				continue
			seatdata.append(mySeat)

		seatdata.sort()

		return seatdata

	def lockSeat(self, block, date, idtime, seats):
		if len(seats) == 0:
			return False

		mytoken = ",".join([seat.seatid for seat in seats])
		print(date, idtime, mytoken)
		myptags = "".join([seat.getPTag() for seat in seats])
		print(myptags)

		URL = "http://ticket.yes24.com/OSIF/Book.asmx/Lock"
		payload = {'name':self.customerid,'idTime':idtime,'token':mytoken,'Block':block}
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[Lock]", r.status_code, r.reason)
		print(r.text)

		root = ET.fromstring(r.text)
		if int(root.text) != 0:
			print("Lock failed")
			return False

		print("Lock succeed.....Expires in 5min(NOW:{})".format(datetime.datetime.now()))

		params = urllib.parse.urlencode(payload)
		getURL = URL + "?" + params
		print(getURL)
		print("")
		return True

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

		"""
            if (joDvry.find("input[id^='rdoDelivery']").length > 0)
                joDvry.find("input[id^='rdoDelivery']:first").prop("checked", true).trigger("click");
		"""

		self.sel.change_value_by_id(self.idperf)
		self.sel.change_element_value_by_id('IdTime', idtime)
		self.sel.change_element_value_by_id('IdSeatClassPrice', self.idseatclassprice)
		self.sel.change_element_value_by_id('IdSeatClass', self.idseatclass)
		self.sel.change_element_value_by_id('IdSeat', self.idseats)
		print("READY!!!!!!!!!!!!!!!!!!! BOOK FAST!!!!!")
		print("Waiting for you enter!! to find another seat")
		input()

		return True

	def browser_login(self):
		self.sel = Selenium_yes24(idperf=self.idperf)
		self.sel.login(userid=self.loginid, userpw=self.loginpw)
		self.sel.openBlank()

	def browser_openSample(self, idperf, idtime):
		self.sel.openPerf(idperf, idtime)

	def browser_wait_last_page(self):
		self.sel.waitLastPage()
		self.sel.prepare_lastpage()

	def browser_openPerf(self, date, idtime, token, ptags):
		sel = self.sel
		try:
			sel.openPerf(self.idperf, idtime)
			sel.findTime(date=date, idtime=idtime)
			sel.selectSeat(idhall='', token=token, ptags=ptags)
			sel.nextStep()
		except Exception:
			print(traceback.format_exc())
			print("Exception happened but script keep going")

	def seatEnd(self, idtime, classes):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/TimeSeatFlashEnd.aspx"
		#URL = "http://m.ticket.yes24.com/Perf/Sale/Ajax/Perf/AxTimeSeatFlashEnd.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime': idtime, 'PCntClass':classes}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[seatEnd]", r.status_code, r.reason)
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

	def getEtcFee(self, idtime, count):
		#URL = "http://m.ticket.yes24.com/Perf/Sale/Ajax/Perf/AxEtcFee.aspx"
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/EtcFee.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime': idtime, 'pSeatCnt': count, 'pFreeCountOfCoupon': 0, 'pFreeCountOfGiftTicket': 0}
		r = self.session.post(URL, headers=headers, data=payload)
		print("[EtcFee]", r.status_code, r.reason)
		#print(r.text)
		#<input type=hidden id=EtcFees value='69#2000^' /><input type=hidden id=EtcFeeAmount value='2000' /><input type=hidden id=EtcValidTicketCnt value='2' />

		soup = BeautifulSoup(r.text, "html.parser")
		self.feetype = soup.find('input', {"id": "EtcFees"})['value']
		self.feeamount = soup.find('input', {"id": "EtcFeeAmount"})['value']
		#print(self.feetype)
		#print(self.feeamount)
		return r.text

	def getDeliveryMethod(self, idtime, date, idperf, idclass):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/DeliveryMethod.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		payload = {'pIdTime':idtime, 'pBaseDate':date, 'pIdPerf':idperf, 'pIdClass':idclass}
		r = self.session.post(URL, headers=headers, data=payload)
		print('[DeliveryMethod]',r.status_code, r.reason)
		#print(r.text)
		return r.text

	def getDeliveryInfo(self):
		URL = "http://ticket.yes24.com/Pages/Perf/Sale/Ajax/Perf/DeliveryUserInfo.aspx"
		headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
		r = self.session.post(URL, headers=headers)
		print('[Delivery]',r.status_code, r.reason)
		print(r.text)

	def getMyOrders(self, date=None):
		URL = "http://ticket.yes24.com/Pages/MyPage/Ajax/MyOrder/MyOrderList.aspx"
		payload = {'pDispGubun': 1, 'pStartDT':'2018-10-14', 'pEndDT':'2018-11-14', 'pCurPage':1, 'pPageSize':20}
		r = self.session.post(URL, data=payload)
		print("[MyOrders]", r.status_code, r.reason)
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
		print("[Ticket]", r.status_code, r.reason)
		#print(r.text)
		soup = BeautifulSoup(r.text, "html.parser")
		info = str( soup.find('div', {"class": "blu_list"}) )
		print(info)

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
		prefer = "O" if self.isSeatPrefered() else "X"
		return "{} / lock:{} / {} / {} / {} / Prefer?{}".format(self.seatid, self.idlock, self.desc, self.price, self.grade, prefer)

	def getPTag(self):
		return '<p id="C{}" class="txt2" name="cseat" grade="{}">{}</p>'.format(self.seatid, self.grade, self.desc)

	def __lt__(self, other):
		return int(self.seatid) < int(other.seatid)

	def isSeatPrefered(self):
		# t1300064
		# t1400082
		#if self.seat_row >= 13 and self.seat_row <= 14 and self.seat_col >= 64 and self.seat_col <= 82:
		#	return True

		# t600030 : 4row, 9th seat
		# t1200037 : 10row, 16th seat
		#if self.seat_row >= 6 and self.seat_row <= 20 and self.seat_col >= 30 and self.seat_col <= 53: # TEST
		if self.seat_row >= 6 and self.seat_row <= 12 and self.seat_col >= 30 and self.seat_col <= 37: # REAL
			return True
		return False

	def isSeatSerial(self, other):
		if self.seat_row != other.seat_row:
			return False
		elif abs(self.seat_col-other.seat_col) == 1:
			return True
		else:
			return False



