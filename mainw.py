#!/usr/bin/env python

import Tkinter as tk
import tkFileDialog
import ttk

import tklib.console as tkcon
import tklib.symbol as tksym

import yahoo

import pdb

VERSION="0.0.2"

class Application():

	
	def __init__(self, root):
		
		self.root = root
		self.source = None
		
		self.root.title("pymta tkInterface {0}".format(VERSION))

		# menu bar
		menubar = tk.Menu(self.root)
		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label="New", command=self.database_new)
		filemenu.add_command(label="Open", command=self.database_open)
		filemenu.add_command(label="Exit", command=self.quit)
		menubar.add_cascade(label="File", menu=filemenu)
		symbolmenu = tk.Menu(menubar, tearoff=0)
		symbolmenu.add_command(label="Add", command=self.symbol_add)
		symbolmenu.add_command(label="Load from file", command=self.symbol_load_from_file)
		menubar.add_cascade(label="Symbol", menu=symbolmenu)
		self.root.config(menu=menubar)
		
		# create the main frame
		self.mainFrame = tk.Frame(self.root)
		self.mainFrame.pack(fill=tk.BOTH, expand=1)
		
		# show console window
		self.con = tkcon.Window(self.root)
		
		# symbols list
		listFrame = tk.Frame(self.mainFrame)
		listFrame.pack(fill=tk.BOTH, expand=1)
		
		scrollbar = tk.Scrollbar(listFrame)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.symbolsList = ttk.Treeview(listFrame, columns=["descr", "last_updated"])
		self.symbolsList.pack(fill=tk.BOTH, expand=1)
		
		self.symbolsList.config(yscrollcommand=scrollbar.set)
		scrollbar.config(command=self.symbolsList.yview)

		# symbols list context menu
		# self.popup = tk.Menu(self.symbolsList, tearoff=0)
		# self.popup.add_command(label="Refresh EoD", command=self.symbol_refreshEoD)
		# self.popup.add_command(label="Plot", command=self.symbol_plot)
		# self.symbolsList.bind("<Button-3>", self.do_popup)
		
		# button bar
		btnFrame = tk.Frame(self.mainFrame)
		btnFrame.pack(fill=tk.BOTH, expand=0)
		btnAdd = tk.Button(btnFrame, text="Add new", command=self.symbol_add)
		btnRefresh = tk.Button(btnFrame, text="Refresh selected", command=self.symbol_refreshEoD)
		btnAdd.pack(side=tk.RIGHT)
		btnRefresh.pack(side=tk.RIGHT)
		
		# FIXME: delete following rows
		# self.source = yahoo.LocalSource("/home/marco/lab/pymta/yahoo.db3")
		self.source = yahoo.LocalSource("C:/mg/lab/pymta/yahoo.db3")
		self.symbolsList_refresh()

	# def do_popup(self, event):
		
		# try:
			# self.popup.tk_popup(event.x_root, event.y_root, 0)
		# finally:
			# self.popup.grab_release()
			

	def database_new(self):
		"""Create a new database file"""

		filename = tkFileDialog.asksaveasfilename()
		
		if filename:
			self.con.info("User asked to create a new database named {0}".format(filename))
			self.source = yahoo.LocalSource(filename)
		

	def database_open(self):
		"""Open an existing database"""
	
		filename = tkFileDialog.askopenfilename(multiple=False)

		if filename:
		
			try:
				self.con.info("Trying to load file {0}".format(filename))
				self.source = yahoo.LocalSource(filename)
			except Exception, ex:
				self.con.critical("Cannot open file {0} as local database".format(filename))
				self.con.error(ex.message)
			
			self.symbolsList_refresh()
	
	def symbol_load_from_file(self):
		"""Add a group of symbols starting from one CSV index file"""
		
		if self.source == None:
			self.con.info("You need to open a database first")
			return
			
		w = tksym.WindowAddFromFile(self.root, self.source)
			

	def symbol_add(self):
		"""Add new symbol to database"""
		
		if self.source == None:
			self.con.info("You need to open a database first")
			return
			
	def symbol_refreshEoD(self):
	
		selectedIndexes = self.symbolsList.selection()
		
		for idx in selectedIndexes:
		
			symbol = self.symbolsList.item(idx)["text"]
			
			try:
				self.con.info("Refreshing symbol {0}".format(symbol))
				self.source.symbol_refresh_eod(symbol)
				
			except Exception, ex:
				self.con.error("Cannot refresh symbol {0}".format(symbol))
				self.con.error(ex.message)
				continue
				
			self.con.info("Done")

		
	def symbolsList_refresh(self):
		"""Rescan database to retrieve all the stored symbols"""
		
		symbols = self.source.symbol_get_all()
		for symbol in symbols:
			self.symbolsList.insert('', 'end', text=symbol[0], values=[symbol[1], symbol[2]])
		
			
	def quit(self):
	
		self.root.quit()
		self.root.destroy()
	
		

if __name__ == '__main__':

	root = tk.Tk()
	app = Application(root)
	root.mainloop()
