from models import *
import datetime
import time

class Counter:
	
	def __init__(self):
		self.TIME_PERIODS = {
			'five_minutes': datetime.timedelta(minutes = 5), 
			'one_hour': datetime.timedelta(hours = 1),
			'one_day': datetime.timedelta(days = 1)
		}
		self.USER_LIMITS = {
			'five_minutes': 5000,
			'one_hour': 10000,
			'one_day': 50000
		}
		self.GLOBAL_LIMITS = {
			'five_minutes': 50000,
			'one_hour': 100000,
			'one_day': 1000000
		}
		self.client = None
		self.host = None
		self.access = None
		self.user_count = {}
		self.global_count = {}
		
	def exceeded(self, request, slow_down = False):

		return False
		
		now = datetime.datetime.now()
		try:
			client, dummy = AccessClient.objects.get_or_create(string = request.META['HTTP_USER_AGENT'])
		except:
			client, dummy = AccessClient.objects.get_or_create(string = "None")
		host, dummy = AccessHost.objects.get_or_create(string = request.META['REMOTE_ADDR'])
		access, dummy = Access.objects.get_or_create(host = host, client = client, timestamp = now)
		
		if host.force_block:
			return True
		
		for period, timedelta in self.TIME_PERIODS.items():
			self.user_count[period] = Access.objects.filter(host = host, timestamp__gte = (now - timedelta)).count()
			if self.user_count[period] > self.USER_LIMITS[period]:
				if slow_down:
					host = AccessHost.objects.get(string = request.META['REMOTE_ADDR'])
					sleep_period = min(max(1,(self.user_count[period] / 100)), 3)
					if host.force_sleep_period:
						sleep_period = host.force_sleep_period
					host.current_sleep_period = sleep_period
					host.save()
					if host.blocked:
						time.sleep(15)
						continue
					d = datetime.datetime.now() - host.lock_timestamp  
					# days is negative if the lock time stamp is in the future compared to datetime.now()
					if d.days >= 0 and d.seconds >= 0:
						host.lock_timestamp = datetime.datetime.now() + datetime.timedelta(seconds = sleep_period)
						host.blocked = 1
						host.save()
						time.sleep(sleep_period)
						host.lock_timestamp = datetime.datetime.now()
						host.blocked = 0
						host.save()
					else:
						time.sleep(15)
					#host.blocked = 0
					#host.save()
				#return True
		
			self.global_count[period] = Access.objects.filter(timestamp__gte = (now - timedelta)).count()
			if self.global_count[period] > self.GLOBAL_LIMITS[period]:
				time.sleep(10)
				#return True
		
		return False
		
		
		
