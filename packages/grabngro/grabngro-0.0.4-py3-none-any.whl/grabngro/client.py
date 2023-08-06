import requests

class ApiClient:
	"""
	`ApiClient` is a wrapper for the pyarrow API.

	Example:

	```
	client = ApiClient()

	# lists available datasets
	datasets = client.get_datasets()
	print(datasets) # ex: ['ndvi_8day', 'gdi_daily', 'lst_daily']

	# query ndvi data for a region in 2019
	client.get_by_region(region_id=140360, dataset='ndvi_8day', year=2019)

	# query gdi data for Illinois in December 2017
	client.get_by_province(province_id=13064, dataset='gdi_daily', year=2017, month=12)

	# query lst data for France from January 2017 to March 2020, inclusive
	x = client.get_by_country(country_id=1070, dataset='lst_daily', year=2017, month=1, year_until=2020, month_until=3)

	# load the result into a pandas DataFrame
	df = pd.DataFrame(x).T
	```
	"""

	def __init__(self):
		self.API_ENDPOINT = 'http://10.20.25.249:8000/' # internal private ip
		self.CONNECT_ERROR = 'Unable to connect to the API.\nThe IP may have changed, try updating grabngro with `pip install --upgrade grabngro`'

	def get_datasets(self):
		try:
			res = requests.get(self.API_ENDPOINT + 'datasets')
		except requests.exceptions.ConnectionError:
			raise Exception(self.CONNECT_ERROR)
		res.raise_for_status()
		return res.json()

	def get_by_region(self, region_id, **kwargs):
		return self.query('&region=%s' % region_id, **kwargs)

	def get_by_province(self, province_id, **kwargs):
		return self.query('&province=%s' % province_id, **kwargs)

	def get_by_country(self, country_id, **kwargs):
		return self.query('&country=%s' % country_id, **kwargs)

	def query(self, area_selector, dataset, year, month=None, year_until=None, month_until=None):
		year = int(year)
		end_mo = 12
		start_mo = int(month or 1)
		end_yr = int(year_until or year)
		querystring = '?file=%s%s' % (dataset, area_selector)
		for yr in range(year, end_yr + 1):
			if yr == end_yr:
				end_mo = int(month_until or month or 12)
			for mo in range(start_mo, end_mo + 1):
				if start_mo == 1 and end_mo == 12:
					querystring += '&months=%s' % yr
					break
				querystring += '&months=%s-%s' % (yr, mo)
			start_mo = 1

		try:
			res = requests.get(self.API_ENDPOINT + querystring)
		except requests.exceptions.ConnectionError:
			raise Exception(self.CONNECT_ERROR)
		res.raise_for_status()
		json = res.json()
		if 'error' in json.keys():
			raise Exception(json['error'])
		return json
