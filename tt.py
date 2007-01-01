#!/usr/bin/env python
# -*- coding: utf-8 -*-

# برنامه آموزش تایپ. نوشته جادی
# این برنامه فعلا نسخه ۰.۰۱ است. اصولا هنوز تمام نشده
# ولی به هرحال چون مدتی است روی آن کار نکرده‌ام تحت لیسانس GPL منتشرش می کنم
# در انجام هر تغیری آزاد هستید تا وقتی که این نوشته ها رو تکرار کنید
# www.Freekeyboard.net



import pygtk
pygtk.require('2.0')
import gtk, gobject
import time
import random

class MainWindow:
	def ReadLessons(self, mainwindow, area, inputFile):
		f = open(inputFile, 'r')
		i =1
		while f:
			if len(f.readline())==0: #bypass the first empty line in each lesson
				break;			# stop reading the file in case of EOF
			i+=1
			self.lessonButton.append(gtk.Button(f.readline().strip())) #name of the button
			self.intro = f.readline().strip().replace ('|', '\n')
			possibleTxts=[] #ممکنه چند درس پیشنهادی باشه . همه رو می خونیم و یکی رو شانسی انتخاب می کنیم. 
			while f:
				possibleTxts.append(f.readline().strip().replace ('|', '\n')) #علامت پایپ برابر سر خط رفتن است
				if  (possibleTxts[-1] ==  "."):
					possibleTxts.pop()  # آخری رو حذف می کنیم. آخر حرف ها با یک خط که فقط یک نقطه دارد مشخص شده
					break

			self.lessonButton[-1].connect ("clicked", self.DoOneLesson, mainwindow, area, self.intro, possibleTxts, f.readline().strip()) #lesson intro and lesson text
			self.table.attach(self.lessonButton[-1], 2, 3, i+2, i+3)
			self.lessonButton[-1].show()
	
	

	def ReadWordStat (self, filename):
		fstat = open (filename+'.stat', 'r')
		lines = fstat.readlines()
		fstat.close ()
		charstat = []
		for thisLine in lines:
			try: #چون بعضی کاراکترها اتوماتیک قابل اسپلیت نیستند. مثلا اسپیس یا انتر و ما هم آنها را نمی خواهیم
				letter, num = thisLine.strip().split()
				if letter != 'backspace':
					charstat.append ((letter, int(num)))
			except:
				pass
	
		return charstat
		

	def DoOneLesson(self, widget, mainwindow, area, lessonIntro, lessonTxt, image):  #طرف یک درس را انتخاب کرده. مقدمه و متن درس را می فرستد و همینطور عکسش را

		dialog = gtk.Dialog(title='تمرین', parent=mainwindow, flags=
						(gtk.DIALOG_MODAL), buttons=None)
		table = gtk.Table (40, 50, False)
		dialog.vbox.add (table)
		table.show()

		TeachOneLesson (table, area, lessonIntro, lessonTxt, image)
		dialog.show()	




	def area_expose_cb(self, area, event):
		lowline = 270
		rightmargin = 20
		xstep = 18

		stats = self.ReadWordStat ( 'user')
		gc_b = area.get_style().fg_gc[gtk.STATE_NORMAL]
		#gc_b.foreground = blue

		x = rightmargin
		for letter, num in stats:
			#area.window.draw_line (gc_b, x, lowline, x, 270-num)
			area.window.draw_rectangle (gc_b, False, x-1, 270-num, 2, num)
			pangoTxt= area.create_pango_layout(letter)
			area.window.draw_layout (gc_b, x-3, lowline+4, pangoTxt)
			x += xstep



		
	def __init__(self):
		self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)  #پنجره اصلی برنامه. فهرست درس ها و مقدمه اصلی پنجره
		self.window.connect("delete_event", lambda w,e: gtk.main_quit())
		self.window.show()
		self.window.set_title('آموزش تایپ')
		
		self.table = gtk.Table(50, 50, homogeneous=False)
		self.window.add (self.table)

		self.wintitle = gtk.Label('به برنامه آموزش تایپ خوش آمده اید. نگران نباشید. با تمرین همه یاد گرفته اند. شما هم می توانید... درس ها را قدم به قدم شروع کنید\n\nبرنامه عملا کامل است. فقط جینگول بازی ها مانده که آن ها هم قدم به قدم جلو می روند')
		self.wintitle.set_line_wrap(True)
		self.table.attach (self.wintitle, 0, 4, 0, 1)
		self.wintitle.show()

		area = gtk.DrawingArea()
		area.set_size_request(450, 300)
		self.table.attach(area, 5, 6, 0, 10)
		colormap = area.get_colormap()
		blue = colormap.alloc_color(0, 0, 65535)
		area.connect("expose-event", self.area_expose_cb)
		area.show()

		self.lessonButton = []
		self.ReadLessons(self.window, area, 'normal.jtt')

		charstat = self.ReadWordStat ('user')
		newstat = charstat
		#DrawGraph(charstat, newstat)

		self.table.show()
		self.window.show()


class TeachOneLesson:
	def WriteWordStat (self, filename, charStat):

		fstat = open (filename+'.stat', 'w')
		for letter in charStat:
			total = 0.0
			for thistime in charStat[letter]:
				total += thistime

			speed = total / len(charStat[letter]) * 100 
			if speed > 240: 
				speed = 240
			if (letter):
				fstat.write ("%s\t%s\n" % (letter, int(270-speed)))
		fstat.close ()

	def CheckEachLetter (self, widget, teacher, student, status, keyboardbuf, keyboardimage, area): #هر چند لحظه یکبار متن تایپ شده شاگرد را بررسی می کند و نمره می دهد
	
							#اگر تایپ تمام شده باشد و درست باشد، زمان سنج را متوقف می کند و نمره را نمایش می دهد
		tbuffer = teacher.get_buffer()
		sbuffer = student.get_buffer()

		global prewaitingForChar
		global thisCharTime
		global charStat
		try:
			charStat
		except:
			charStat={}
		try:
			prewaitingForChar
		except:
			prewaitingForChar = tbuffer.get_text(tbuffer.get_iter_at_offset(0), tbuffer.get_iter_at_offset(1))

		wordsNum=1

		redtag=sbuffer.create_tag(None, foreground='white', background='red')
		errorNum = 0
		for i in range(0, sbuffer.get_char_count()):
			tc = tbuffer.get_text(tbuffer.get_iter_at_offset(i), tbuffer.get_iter_at_offset(i+1))
			sc = sbuffer.get_text(sbuffer.get_iter_at_offset(i), sbuffer.get_iter_at_offset(i+1))
			if tc==' ' or tc=='\n': 
				wordsNum+=1
			if (tc != sc):
				errorNum += 1
				sbuffer.apply_tag (redtag, sbuffer.get_iter_at_offset(i), sbuffer.get_iter_at_offset(i+1))
			
		if (sbuffer.get_char_count()==0):
			self.startTime = time.time()
			thisCharTime = time.time()

		timeTxt = ' زمان ' + str(int (time.time() - self.startTime)) + ' ثانیه '

		#فهرستی از هر کلید و اینکه برای هر کاراکتر 
		keyboard_layout = {"پ":((0,0),(375, 22), ),"ض":((40,23), ),"ص":((69,23), ),"ث":((95,23), ),"ﻕ":((122,23), ),"ف":((149,23), ),"ﻍ":((176,23), ),"ع":((203,23), ),"ه":((230,23), ),"خ":((257,23), ),"ح":((285,23), ),"ج":((311,23), ),"چ":((339,23), ),"ش":((54,46), ),"س":((80,46), ),"ی":((107,46), ),"ب":((134,46), ),"ل":((161,46), ),"ا":((187,46), ),"ت":((215,46), ),"ن":((242,46), ),"م":((269,46), ),"ک":((296,46), ),"گ":((323,46), ),"ظ":((65,68), ),"ط":((92,68), ),"ز":((119,68), ),"ر":((146,68), ),"ذ":((173,68), ),"د":((200,68), ),"و":((253,68), ),".":((281,68), ),"ژ":((119,68),(14,68),(353,68), ),"!":((25,1),(14,68),(353,68), ),"(":((268,0),(14,68),(353,68), ),")":((242,0),(14,68),(353,68), ),"-":((296,0), ),"،":((188,0),(14,68),(353,68), ),"؟":((308,68),(14,68),(353,68), )," ":((134,90), (154, 90), (174,90), (194,90),(214,90)), "\n" : ((354, 45),(374,45)), "backspace": ((354, 0),(374,0))}
		

		if errorNum == 0:
			waitingForChar = tbuffer.get_text (tbuffer.get_iter_at_offset(sbuffer.get_char_count()), tbuffer.get_iter_at_offset(sbuffer.get_char_count()+1))
		else:
			waitingForChar = "backspace"

		if waitingForChar != prewaitingForChar:
			thistime = time.time() - thisCharTime
			thisCharTime = time.time()
			try:
				charStat[prewaitingForChar].append(thistime)
			except:
				charStat[prewaitingForChar]=[]
				charStat[prewaitingForChar].append(thistime)
			prewaitingForChar = waitingForChar


		if (keyboard_layout.has_key(waitingForChar)):
			pixbuf2 = gtk.gdk.pixbuf_new_from_file('push.png')
			keyboardbuf = gtk.gdk.pixbuf_new_from_file('keyboard.png')	
			
			for (x, y) in keyboard_layout[waitingForChar]:
				pixbuf2.composite(keyboardbuf, x, y, 20, 20, 1, 1, 1, 1, gtk.gdk.INTERP_BILINEAR, 255)
			keyboardimage.set_from_pixbuf (keyboardbuf)
			keyboardimage.hide()
			keyboardimage.show()

		#چک می کنیم که طرف تایپ را تمام کرده یا نه
		if errorNum == 0 and sbuffer.get_char_count() > 0 and tbuffer.get_char_count() == sbuffer.get_char_count(): #all typed correctly
			status.set_text ('آفرین! تمرین تمام شد\n' + timeTxt + '(یعنی %i کلمه در دقیقه)' % int(wordsNum*60/int(time.time() - self.startTime)))
			student.set_editable(False)
			student.set_cursor_visible(False)
			self.WriteWordStat ('user', charStat)
			area.queue_draw()
			del charStat
			return 0  #زمان سنج متوقف می شود
		else:
			remaining = tbuffer.get_char_count()-sbuffer.get_char_count()
			if remaining > 0 :
				remstr = str(remaining) + ' باقی مانده '
			else:
				remstr = str(-remaining) + ' اضافه تایپ کرده اید '
			status.set_text (str(errorNum)+' خطا \n' + remstr + '\n' + timeTxt)
			return 1   #زمان سنج ادامه می دهد


	def __init__(self, table, area, lessonIntro, lessonTxt, image=''):
	#create window	

		lessonTxt = random.choice(lessonTxt)

		if image: # اگر فایل تصویری برای این درس مشخص شده بود نمایش اش می دهیم
			headimage = gtk.Image()
			headimage.set_from_file(image)
			table.attach (headimage, 0, 3, 1, 2)
			headimage.show()

		#حالا عکس یک کیبرد که بعدا بافرش رو می فرستیم برای برنامه چک کننده درست تایپ کردن شاگرد و اون برنامه روی این یک مربع قرمز می ندازه که نشون می ده کدوم کلید باید فشرده بشه. 
		keyboardbuf = gtk.gdk.pixbuf_new_from_file('keyboard.png')	
		keyboardimage = gtk.Image()
		keyboardimage.set_from_pixbuf (keyboardbuf)
		table.attach (keyboardimage, 0, 3, 2, 3)


		intro = gtk.Label(lessonIntro)  # نوشته بالای هر درس. ممکنه آموزش درس یا تشویق باشه
		intro.set_line_wrap(True)
		table.attach (intro, 0, 3, 0, 1)
		intro.show()

		teacher=gtk.TextView()
		teacher.set_editable(False)  #متن معلم. قرار نیست ویرایش بشه 
		teacher.set_cursor_visible(False)
		tbuffer=teacher.get_buffer()
		tbuffer.set_text (lessonTxt) #محتوای درس را در بخش معلمی نشان بده
		teacher.set_wrap_mode(gtk.WRAP_WORD)
		table.attach (teacher, 0, 3, 3, 4, ypadding=12)

		student=gtk.TextView()  #متنی که شاگرد تایپ کرده
		student.set_wrap_mode(gtk.WRAP_WORD)
		table.attach (student, 0, 3, 4, 5)

		status = gtk.Label('در حال شروع')
		table.attach (status, 0, 3, 5, 6)

		status.show()
		teacher.show()
		student.show()

		student.grab_focus()
		
		startTime = time.time() # مشخص می کنه که در چه لحظه ای تایپ شروع شده که بعدا بتونیم زمان تایپ رو بگیم
		self.timer = gobject.timeout_add (20, self.CheckEachLetter, self, teacher, student, status, keyboardbuf, keyboardimage, area) # هر چندوقت یکبار روتینی رو صدا می زنه که متن تایپ شده رو نمره می ده



def main():

	gtk.main()
	return 0

if __name__ == "__main__":
	random.seed()
	MainWindow()
	main()
