
import yahoo
import unittest
import datetime
import sqlite3
import os

import pdb


DB3_FILE = "tests/test.db3"
CSV_FILE = "tests/test.csv"
CSV_INDEX_FILE = "tests/index_test.csv"
TEST_SYMBOL = "TEST"
ONLINE_TEST_SYMBOL = "ENI.MI" # for testing yahoo online database
TEST_INDEX_SYMBOL = "^DJI"
COMPONENTS_NUM = 30 # total number of components for the DJ index
URL_INDEX_COMPONENTS = "http://finance.yahoo.com/q/cp?"


def silentremove(filename):
	"""Remove given filename if exists. Fails silently.
	"""
	try:
		os.remove(filename)
	except OSError:
		pass


class OnlineSource(unittest.TestCase):
	
	def setUp(self):
		
		self.source = yahoo.OnlineSource()
		
	def tearDown(self):
		
		pass
		
	def test_parsedatestring(self):
		
		datetime_obj = datetime.datetime.strptime('1974-09-03', '%Y-%m-%d')
		unixtime = int(datetime_obj.strftime('%s'))
		self.assertEqual(self.source._parsedatestring('1974-09-03'), unixtime)
		
	def test_symbol_get_closings(self):
		
		rows = self.source.symbol_get_closings(ONLINE_TEST_SYMBOL)
		self.assertGreater(len(rows), 0)
		self.assertEqual(len(rows[0]), 2)
		
	def test_symbol_get_volumes(self):
		
		rows = self.source.symbol_get_volumes(ONLINE_TEST_SYMBOL)
		self.assertGreater(len(rows), 0)
		self.assertEqual(len(rows[0]), 2)
		
	def test_symbol_get_ochlv(self):
		
		rows = self.source.symbol_get_ochlv(ONLINE_TEST_SYMBOL)
		self.assertGreater(len(rows), 0)
		self.assertEqual(len(rows[0]), 6)
		
	def test_symbol_exists(self):
		
		self.assertTrue(self.source.symbol_exists(ONLINE_TEST_SYMBOL))

	def test_symbol_not_exists(self):
		
		self.assertFalse(self.source.symbol_exists('YARGLA.MI'))

	def test_download2csv(self):
		
		filename = self.source.download2csv(ONLINE_TEST_SYMBOL)
		self.assertTrue(os.path.isfile(filename))
		silentremove(filename)

	def test_get_maxdate(self):
		
		maxdate = self.source.symbol_get_maxdate(ONLINE_TEST_SYMBOL)
		self.assertIsInstance(maxdate, datetime.datetime)


class LocalSource(unittest.TestCase):

	def setUp(self):
		
		silentremove(DB3_FILE)
		self.source = yahoo.LocalSource(DB3_FILE)
		self.source.eod_load_from_csv(TEST_SYMBOL, CSV_FILE) # load fake prices as symbol `TEST`
	
	def tearDown(self):
		
		self.source.close()
		silentremove(DB3_FILE)

	def test_symbol_delete(self):		
		
		self.source.symbol_delete(TEST_SYMBOL)
		
		conn = sqlite3.connect(DB3_FILE)
		cur = conn.cursor()
		cur.execute("select count(*) from DAT_EoD")
		rowcount = cur.fetchone()
		self.assertTrue(rowcount[0] == 0)
		conn.close()
		
	def test_symbol_load_eod(self):
		
		conn = sqlite3.connect(DB3_FILE)
		cur = conn.cursor()
		cur.execute("select count(*) from DAT_EoD where symbol = '{0}'".format(TEST_SYMBOL))
		rowcount = cur.fetchone()
		self.assertTrue(rowcount[0] > 0)
		conn.close()

	def test_query_simple(self):
		
		data = self.source._query("TEST")
		self.assertTrue(len(data) > 0)

	def test_query_wColumns(self):
		
		data = self.source._query("TEST", columns=['date', 'volume', 'close'])
		self.assertTrue(len(data) > 0)
	
	def test_symbol_get_all(self):
		
		self.source.symbol_load_from_csv(CSV_INDEX_FILE, "TEST_INDEX", None)
		symbols = self.source.symbol_get_all()
		self.assertTrue( len(symbols) > 0 )
		
	def test_symbol_get_maxdate(self):
		
		maxdate = self.source.symbol_get_maxdate(TEST_SYMBOL)
		self.assertIsInstance(maxdate, datetime.datetime)

	def test_symbol_get_closings(self):
		
		rows = self.source.symbol_get_closings(TEST_SYMBOL)
		self.assertGreater(len(rows), 0)
		self.assertEqual(len(rows[0]), 2)
		
	def test_symbol_get_volumes(self):
		
		rows = self.source.symbol_get_volumes(TEST_SYMBOL)
		self.assertGreater(len(rows), 0)
		self.assertEqual(len(rows[0]), 2)
		
	def test_symbol_get_ochlv(self):
		
		rows = self.source.symbol_get_ochlv(TEST_SYMBOL)
		self.assertGreater(len(rows), 0)
		self.assertEqual(len(rows[0]), 6)

	@unittest.skip("Temporarily disabled because too expensive")
	def test_symbol_all_load_eod(self):
		
		self.source.symbol_delete(TEST_SYMBOL)
		self.source.symbol_all_load_eod()
		symbols = self.source.symbol_get_all()
		loaded_symbols = self.source._query("select symbol from DAT_EoD group by symbol")
		self.assertEqual(len(symbols), len(loaded_symbols))

	@unittest.skip("Temporarily disabled because too expensive")
	def test_symbol_load_all_from_csv(self):
		
		self.source.symbol_delete(TEST_SYMBOL)
		symbols_start = self.source.symbol_get_all()
		self.source.symbol_load_from_csv('TEST_INDEX', CSV_INDEX_FILE) # load symbols from CSV file
		self.source.symbol_load_all() # load EoD
		symbols_end = self.source.symbol_get_all()
		self.assertEqual(len(symbols_start), 0)
		self.assertGreater(len(symbols_start), len(symbols_start))

	def test_eod_load_from_csv(self):
		
		self.source.eod_load_from_csv("LOADTEST", CSV_FILE)
		conn = sqlite3.connect(DB3_FILE)
		cur = conn.cursor()
		cur.execute("select count(*) from DAT_EoD where symbol = '{0}'".format("LOADTEST"))
		rowcount = cur.fetchone()
		conn.close()
		self.assertTrue(rowcount[0] > 0)
		
	def test_symbol_load_from_csv(self):
		
		self.source.symbol_load_from_csv(CSV_INDEX_FILE, "TEST_INDEX", None)
		
		conn = sqlite3.connect(DB3_FILE)

		cur = conn.cursor()
		cur.execute("select count(*) from DAT_index")
		count_DAT_index = cur.fetchone()[0]

		cur = conn.cursor()
		cur.execute("select count(*) from DAT_index_symbol where `index` = '{0}'".format("TEST_INDEX"))
		count_DAT_index_symbol = cur.fetchone()[0]

		cur = conn.cursor()
		cur.execute("select count(*) from DAT_symbol")
		count_DAT_symbol = cur.fetchone()[0]

		conn.close()
		
		self.assertEqual(count_DAT_index, 1)
		self.assertGreater(count_DAT_index_symbol, 0)
		self.assertGreater(count_DAT_symbol, 0)
	
	
	@unittest.skip("TODO :: proper way to test this method ?")
	def test_refresh(self):
		
		self.source.refresh(ONLINE_TEST_SYMBOL)
		
		conn = sqlite3.connect(DB3_FILE)
		cur = conn.cursor()		
		cur.execute("select date_STR from DAT_EoD where symbol = '{0}'"
			" order by date_STR desc limit 1".format(ONLINE_TEST_SYMBOL))

		maxdate_str = cur.fetchone()[0]
		conn.close()

		maxdate = datetime.datetime.strptime(str(maxdate_str), '%Y-%m-%d')
		today = datetime.datetime.today()
		delta = today - maxdate
		self.assertTrue(delta.days < 3) # 3 days, because of weekends
		



if __name__ == '__main__':
	
	unittest.main()
