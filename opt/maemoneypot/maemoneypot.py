#!/usr/bin/env python
# -*- coding:Utf-8 -*-
from __future__ import with_statement
import hildon
import gtk
import dbus
import sqlite3 as sql
import time
import datetime
import calendar
import os
import sys
import hashlib
from modules.db_query import DatabaseQueries
from modules.matplotlib_query import MatplotlibQueries
from modules.clickable_pixbuf import CellRendererClickablePixbuf

'''This is fixed to exclude 'dummy user' actions as
the database content is definite'''
database = '/home/user/.maemoneypot/.maemoneypotdb'
bus = dbus.SystemBus()
iface = dbus.Interface(bus.get_object('org.freedesktop.Notifications',
                                      '/org/freedesktop/Notifications'),
                       'org.freedesktop.Notifications')

try:
    with open(database):
        db = sql.connect(database)
        cur = db.cursor()
        print '\033[92m'+'Database connected'+'\033[0m'
except:
    print '\033[91m'+'Database does not exist so we must create it'+'\033[0m'
    db = sql.connect(database)
    cur = db.cursor()
    cur.execute('CREATE TABLE Expenses(Id integer primary key, \
                Date date, Expense int, Category varchar, Tag varchar);')
    cur.execute('CREATE TABLE Incomes(Id integer primary key, \
                Date date, Income int, Category varchar);')
    cur.execute('CREATE TABLE Savings(Id integer primary key, \
                Date date, Saving int, Category varchar);')
    iface.SystemNoteInfoprint('Database created')

MonthNameList = {'01': 'Jan',
                 '02': 'Feb',
                 '03': 'Mar',
                 '04': 'Apr',
                 '05': 'May',
                 '06': 'Jun',
                 '07': 'Jul',
                 '08': 'Aug',
                 '09': 'Sep',
                 '10': 'Oct',
                 '11': 'Nov',
                 '12': 'Dec'}

DayNameList = {0: 'Mon',
               1: 'Tue',
               2: 'Wed',
               3: 'Thu',
               4: 'Fri',
               5: 'Sat',
               6: 'Sun'}

with open('/home/user/.maemoneypot/settings.ini', 'r') as settingsfile:
    settings = settingsfile.readlines()
currency = settings[0][0:len(settings[0])-1]
defaultView = settings[1][0:len(settings[1])-1]
pwdEnabled = settings[3][0:len(settings[3])-1]

matplotlibQuery = MatplotlibQueries(currency)


class MainWindow(hildon.StackableWindow):

    version = '0.2'

    def __init__(self):
        hildon.StackableWindow.__init__(self)
        self.connect('destroy', gtk.main_quit)
        Menu = hildon.AppMenu()
        self.set_app_menu(Menu)

        ButtonPreviousMonth = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                            gtk.HILDON_SIZE_AUTO_HEIGHT,
                                            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        ButtonPreviousMonth.set_title('Previous month')
        ButtonPreviousMonth.connect('clicked', self.goToPreviousMonth)
        Menu.append(ButtonPreviousMonth)
        ButtonNextMonth = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                        gtk.HILDON_SIZE_AUTO_HEIGHT,
                                        hildon.BUTTON_ARRANGEMENT_VERTICAL)
        ButtonNextMonth.set_title('Next month')
        ButtonNextMonth.connect('clicked', self.goToNextMonth)
        Menu.append(ButtonNextMonth)
        ButtonSpecificMonth = \
            hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                gtk.HILDON_SIZE_AUTO_HEIGHT,
                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        ButtonSpecificMonth.set_title('Go to specific month')
        ButtonSpecificMonth.connect('clicked', self.goToSpecificMonth)
        Menu.append(ButtonSpecificMonth)
        global ButtonCalendarView
        ButtonCalendarView = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                           gtk.HILDON_SIZE_AUTO_HEIGHT,
                                           hildon.BUTTON_ARRANGEMENT_VERTICAL)
        if defaultView == 'Main':
            ButtonCalendarView.set_title('Calendar view')
        elif defaultView == 'Calendar':
            ButtonCalendarView.set_title('Main view')
        ButtonCalendarView.connect('clicked', self.changeView)
        Menu.append(ButtonCalendarView)
        ButtonSettings = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                       gtk.HILDON_SIZE_AUTO_HEIGHT,
                                       hildon.BUTTON_ARRANGEMENT_VERTICAL)
        ButtonSettings.set_title('Settings')
        ButtonSettings.connect('clicked', self.settings)
        Menu.append(ButtonSettings)
        ButtonSearch = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                     gtk.HILDON_SIZE_AUTO_HEIGHT,
                                     hildon.BUTTON_ARRANGEMENT_VERTICAL)
        ButtonSearch.set_title('Search')
        ButtonSearch.connect('clicked', self.search)
        Menu.append(ButtonSearch)
        Menu.show_all()

    def mainView(self, year, month, day):
        global View
        View = 'Main'
        global Year
        Year = year
        global Month
        Month = month
        self.set_title(MonthNameList[month]+' | '+year)
        global Table
        Table = gtk.Table(10, 1, True)

        list1, list2, list3 = [], [], []

        cur.execute('select sum(Expense) from Expenses where \
                    strftime("%Y", Date)="'+year+'" \
                    and strftime("%m", Date)="'+month+'";')
        list1.append(cur.fetchone()[0])
        cur.execute('select sum(Income) from Incomes where \
                    strftime("%Y", Date)="'+year+'" \
                    and strftime("%m", Date)="'+month+'";')
        list2.append(cur.fetchone()[0])
        cur.execute('select sum(Saving) from Savings;')
        list3.append(cur.fetchone()[0])

        label = gtk.Label()
        if list2[0] is not None:
            label.set_text("<span size='21000'>"+str(list2[0] -
                                                     list1[0])+"</span>")
        label.set_use_markup(True)
        label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#a0785a'))

        speedclock = matplotlibQuery.Speedclock(list1[0], list2[0])
        monthlySum = matplotlibQuery.MonthlySum(Year)

        PannableArea = hildon.PannableArea()
        PannableArea.add(self.viewSum(list1, list2, list3, year, month, day))
        Table.attach(PannableArea, 0, 1, 0, 5)
        Table.attach(speedclock, 0, 1, 5, 8)
        Table.attach(monthlySum, 0, 1, 8, 10)
        self.add(Table)
        self.show_all()

    def calendarView(self, year, month):
        global View
        View = 'Calendar'
        global Year
        Year = year
        global Month
        Month = month
        self.set_title(MonthNameList[month]+' | '+year)
        if calendar.monthrange(int(year), int(month))[0] == 5 \
                or calendar.monthrange(int(year), int(month))[0] == 6:
            y = 7
        else:
            y = 6

        global TableCalendar
        TableCalendar = gtk.Table(y, 7, True)
        self.add(TableCalendar)

        for day in DayNameList:
            label = gtk.Label(DayNameList[day])
            TableCalendar.attach(label, day, day+1, 0, 1)

        j = calendar.monthrange(int(year), int(month))[0]
        k = 1
        for i in range(1, calendar.monthrange(int(year), int(month))[1]+1):
            if i < 10:
                cur.execute('select sum(Expense) from Expenses where \
                            strftime("%Y", Date) = "'+year+'" \
                            and strftime("%m", Date) = "'+month+'" \
                            and strftime("%d", Date) = "0'+str(i)+'";')
            else:
                cur.execute('select sum(Expense) from Expenses where \
                            strftime("%Y", Date) = "'+year+'" \
                            and strftime("%m", Date) = "'+month+'" \
                            and strftime("%d", Date) = "'+str(i)+'";')
            expense = cur.fetchone()
            if i < 10:
                cur.execute('select sum(Income) from Incomes where \
                            strftime("%Y", Date) = "'+year+'" \
                            and strftime("%m", Date) = "'+month+'" \
                            and strftime("%d", Date) = "0'+str(i)+'";')
            else:
                cur.execute('select sum(Income) from Incomes where \
                            strftime("%Y", Date) = "'+year+'" \
                            and strftime("%m", Date) = "'+month+'" \
                            and strftime("%d", Date) = "'+str(i)+'";')
            income = cur.fetchone()
            if i < 10:
                cur.execute('select sum(Saving) from Savings where \
                            strftime("%Y", Date) = "'+Year+'" \
                            and strftime("%m", Date) = "'+Month+'" \
                            and strftime("%d", Date) = "0'+str(i)+'";')
            else:
                cur.execute('select sum(Saving) from Savings where \
                            strftime("%Y", Date) = "'+year+'" \
                            and strftime("%m", Date) = "'+month+'" \
                            and strftime("%d", Date) = "'+str(i)+'";')
            saving = cur.fetchone()

            vbox = gtk.VBox(False, 0)
            button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                   gtk.HILDON_SIZE_AUTO_HEIGHT,
                                   hildon.BUTTON_ARRANGEMENT_VERTICAL)
            button.set_style(hildon.BUTTON_STYLE_NORMAL)
            button.set_relief(gtk.RELIEF_NONE)
            button.connect('clicked', self.viewDay, i)
            datelabel = gtk.Label()
            datelabel.set_text("<span size='16000'>"+str(i)+"</span>")
            datelabel.set_use_markup(True)
            if i == int(time.strftime('%d')) and \
                    year+month == time.strftime('%Y%m'):
                datelabel.modify_fg(gtk.STATE_NORMAL,
                                    gtk.gdk.color_parse('#f47500'))
            vbox.pack_start(datelabel, True, True, 0)
            if expense[0] is not None:
                expenselabel = gtk.Label()
                expenselabel.set_text("<span size='11000'>"+str(expense[0])+"</span>")
                expenselabel.set_use_markup(True)
                expenselabel.modify_fg(gtk.STATE_NORMAL,
                                       gtk.gdk.color_parse('#f40005'))
                vbox.pack_start(expenselabel, True, True, 0)
            if income[0] is not None:
                incomelabel = gtk.Label()
                incomelabel.set_text("<span size='11000'>"+str(income[0])+"</span>")
                incomelabel.set_use_markup(True)
                incomelabel.modify_fg(gtk.STATE_NORMAL,
                                      gtk.gdk.color_parse('#00f475'))
                vbox.pack_start(incomelabel, True, True, 0)
            if saving[0] is not None:
                savinglabel = gtk.Label()
                savinglabel.set_text("<span size='11000'>"+str(saving[0])+"</span>")
                savinglabel.set_use_markup(True)
                savinglabel.modify_fg(gtk.STATE_NORMAL,
                                      gtk.gdk.color_parse('#007ff4'))
                vbox.pack_start(savinglabel, True, True, 0)
            button.add(vbox)
            TableCalendar.attach(button, j, j+1, k, k+1)
            j = j+1
            if j % 7 == 0:
                j = 0
                k = k+1
        self.show_all()

    def goToNextMonth(self, data=None):
        if View == 'Calendar':
            self.remove(TableCalendar)
            if Month == '12':
                year = str(int(Year)+1)
                month = '01'
            else:
                year = Year
                month = str(int(Month)+1)
                if int(month) < 10:
                    month = '0'+month
            self.calendarView(year, month)
        else:
            self.remove(Table)
            if Month == '12':
                year = str(int(Year)+1)
                month = '01'
            else:
                year = Year
                month = str(int(Month)+1)
                if int(month) < 10:
                    month = '0'+month
            self.mainView(year, month, None)

    def goToPreviousMonth(self, data=None):
        if View == 'Calendar':
            self.remove(TableCalendar)
            if Month == '01':
                year = str(int(Year)-1)
                month = '12'
            else:
                year = Year
                month = str(int(Month)-1)
                if int(month) < 10:
                    month = '0'+month

            self.calendarView(year, month)
        else:
            self.remove(Table)
            if Month == '01':
                year = str(int(Year)-1)
                month = '12'
            else:
                year = Year
                month = str(int(Month)-1)
                if int(month) < 10:
                    month = '0'+month
            self.mainView(year, month, None)

    def goToSpecificMonth(self, data=None):
        years = ['2016', '2017', '2018', '2019', '2020', '2021',
                 '2022', '2023', '2024', '2025', '2026', '2027',
                 '2028', '2029', '2030', '2031', '2032', '2033',
                 '2034', '2035', '2036', '2037', '2038', '2039',
                 '2040', '2041', '2042', '2043', '2044', '2045']
        months = ['January', 'February', 'March', 'April', 'May',
                  'June', 'July', 'August', 'September', 'October',
                  'November', 'December']

        def getMonth(selector, data=None):
            selected = selector.get_current_text()
            if selected is not None:
                y = selector.get_active(0)
                m = selector.get_active(1)
                year = years[y]
                month = str(int(m+1))
                if int(month) < 10:
                    month = '0'+month
                if month != '00':
                    if View == 'Calendar':
                        self.remove(TableCalendar)
                        self.calendarView(year, month)
                    else:
                        self.remove(Table)
                        self.mainView(year, month, None)

        yearStore = gtk.ListStore(str)
        monthStore = gtk.ListStore(str)
        for year in years:
            yearStore.set(yearStore.append(), 0, year)
        for month in months:
            monthStore.set(monthStore.append(), 0, month)

        selector = hildon.TouchSelector()
        selector.remove_column(0)
        selector.append_text_column(yearStore, True)
        selector.append_text_column(monthStore, True)
        selector.set_active(0, -1)
        selector.set_active(1, -1)
        selector.connect('changed', getMonth)
        dialog = hildon.PickerDialog(self)
        dialog.set_title('Set specific year and month')
        dialog.set_done_label('Go')
        dialog.set_selector(selector)
        dialog.run()
        dialog.destroy()

    def changeView(self, button):
        if View == 'Calendar':
            self.remove(TableCalendar)
            self.mainView(Year, Month, None)
            button.set_title('Calendar view')
        else:
            self.remove(Table)
            self.calendarView(Year, Month)
            button.set_title('Main view')

    def settings(self, data=None):
        global currencyNew
        currencyNew = currency
        global savingCategory
        savingCategory = settings[2][0:len(settings[2])-1]
        global defaultViewNew
        defaultViewNew = defaultView
        global pwdEnabledNew
        pwdEnabledNew = pwdEnabled

        def getCurrency(self):
            global currencyNew
            currencyNew = self.get_text()
            self.set_text('')

        def getSaving(self):
            global savingCategory
            savingCategory = self.get_text()
            self.set_text('')

        def setDefaultView(self):
            def getDefaultView(selector, data=None):
                global defaultViewNew
                defaultViewNew = selector.get_current_text()
                buttonDefaultView.set_value(defaultViewNew)

            liststore = gtk.ListStore(str)
            liststore.append(['Main'])
            liststore.append(['Calendar'])
            selector = hildon.TouchSelector()
            selector.append_text_column(liststore, True)
            selector.connect('changed', getDefaultView)
            selector.set_active(0, -1)
            dialog = hildon.PickerDialog(windowSettings)
            dialog.set_selector(selector)
            dialog.set_title('Choose default view')
            dialog.run()
            dialog.destroy()

        def setPwdEnabled(self):
            def getPwdEnabled(selector, data=None):
                global pwdEnabledNew
                pwdEnabledNew = selector.get_current_text()
                buttonPwdEnabled.set_value(pwdEnabledNew)

            liststore = gtk.ListStore(str)
            liststore.append(['Enabled'])
            liststore.append(['Disabled'])
            selector = hildon.TouchSelector()
            selector.append_text_column(liststore, True)
            selector.connect('changed', getPwdEnabled)
            selector.set_active(0, -1)
            dialog = hildon.PickerDialog(windowSettings)
            dialog.set_selector(selector)
            dialog.set_title('Password protection')
            dialog.run()
            dialog.destroy()

        def saveSettings(self, data=None):
            if len(settings[0]) == 1 and len(settings[1]) == 1 \
                    and len(settings[2]) == 1 and len(settings[3]) == 1:
                windowSettings.connect('destroy', gtk.main_quit)
            settings[0] = currencyNew+'\n'
            settings[1] = defaultViewNew+'\n'
            settings[2] = savingCategory+'\n'
            settings[3] = pwdEnabledNew+'\n'
            with open('/home/user/.maemoneypot/settings.ini', 'w') \
                    as settingsfile:
                settingsfile.writelines(settings)
            windowSettings.destroy()
            os.execl(sys.executable, sys.executable, * sys.argv)

        windowSettings = hildon.StackableWindow()
        windowSettings.set_title('Settings')

        table = gtk.Table(6, 1, True)
        label = gtk.Label('Set currency\nCurrent is: '+currencyNew)
        table.attach(label, 0, 1, 0, 1)
        entryCurrency = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entryCurrency.set_placeholder('Set currency')
        entryCurrency.connect('activate', getCurrency)
        table.attach(entryCurrency, 0, 1, 1, 2)
        buttonDefaultView = \
            hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                gtk.HILDON_SIZE_AUTO_HEIGHT,
                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonDefaultView.set_title('Set default view')
        buttonDefaultView.set_value(defaultViewNew)
        buttonDefaultView.set_style(hildon.BUTTON_STYLE_NORMAL)
        buttonDefaultView.set_relief(gtk.RELIEF_NONE)
        buttonDefaultView.connect('clicked', setDefaultView)
        table.attach(buttonDefaultView, 0, 1, 2, 3)
        entrySaving = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entrySaving.set_placeholder('Set savings category; \
                                    current is: '+savingCategory)
        entrySaving.connect('activate', getSaving)
        table.attach(entrySaving, 0, 1, 3, 4)
        buttonPwdEnabled = \
            hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                gtk.HILDON_SIZE_AUTO_HEIGHT,
                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonPwdEnabled.set_title('Password protection')
        buttonPwdEnabled.set_value(pwdEnabledNew)
        buttonPwdEnabled.set_style(hildon.BUTTON_STYLE_NORMAL)
        buttonPwdEnabled.set_relief(gtk.RELIEF_NONE)
        buttonPwdEnabled.connect('clicked', setPwdEnabled)
        table.attach(buttonPwdEnabled, 0, 1, 4, 5)
        buttonSave = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                   gtk.HILDON_SIZE_AUTO_HEIGHT,
                                   hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonSave.set_title('Save settings')
        buttonSave.set_style(hildon.BUTTON_STYLE_NORMAL)
        buttonSave.set_relief(gtk.RELIEF_NONE)
        buttonSave.connect('clicked', saveSettings)
        table.attach(buttonSave, 0, 1, 5, 6)

        windowSettings.add(table)
        if len(settings[0]) == 1 and len(settings[1]) == 1 \
                and len(settings[2]) == 1 and len(settings[3]) == 1:
            windowSettings.connect('destroy', gtk.main_quit)
        windowSettings.show_all()

    def password(self):
        def getPass(self):
            try:
                with open('/home/user/.maemoneypot/password', 'r') as passfile:
                    _pass = passfile.readline()
                    if hashlib.sha224(self.get_text()).hexdigest() == _pass:
                        window.destroy()
                        iface.SystemNoteInfoprint('Password accepted')
                        if defaultView == 'Main':
                            MainWindow().mainView(time.strftime('%Y'),
                                                  time.strftime('%m'), None)
                        elif defaultView == 'Calendar':
                            MainWindow().calendarView(time.strftime('%Y'), time.strftime('%m'))
                        hildon.Program.get_instance()
                        gtk.main()
                    else:
                        iface.SystemNoteInfoprint('Incorrect password, sorry...')
                        gtk.main_quit()
            except:
                with open('/home/user/.maemoneypot/password', 'w') as passfile:
                    passfile.write(hashlib.sha224(self.get_text()).hexdigest())
                    iface.SystemNoteInfoprint('Password saved')
                    gtk.main_quit()
                os.execl(sys.executable, sys.executable, * sys.argv)

        window = hildon.StackableWindow()
        window.set_title('Authentication')
        table = gtk.Table(1, 1, True)
        entryPass = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        # entryPass.set_placeholder('Type the password')
        entryPass.set_input_mode(gtk.HILDON_GTK_INPUT_MODE_FULL)
        entryPass.set_visibility(False)
        entryPass.connect('activate', getPass)
        table.attach(entryPass, 0, 1, 0, 1)
        window.add(table)
        window.connect('destroy', gtk.main_quit)
        window.show_all()

    def search(self, widget):
        cur.execute('select * from Expenses;')
        allExpense = cur.fetchall()
        cur.execute('select * from Incomes;')
        allIncome = cur.fetchall()
        cur.execute('select * from Savings;')
        allSaving = cur.fetchall()
        tempAllExpense = []
        tempAllIncome = []
        tempAllSaving = []

        def getSeachPhrase(self):
            global searchphrase
            searchphrase = self.get_text()
            self.set_text('')

        def elements():
            table = gtk.Table(1, 1, True)
            entrySearchField = hildon.Entry(gtk.HILDON_SIZE_AUTO)
            entrySearchField.connect('activate', getSeachPhrase)
            table.attach(entrySearchField, 0, 1, 0, 1)
            return table

        pannableArea = hildon.PannableArea()
        pannableArea.add_with_viewport(elements())
        dialog = gtk.Dialog('Search...', self, gtk.DIALOG_NO_SEPARATOR |
                            gtk.DIALOG_DESTROY_WITH_PARENT)
        dialog.set_size_request(0, 200)
        dialog.vbox.add(pannableArea)
        dialog.add_button('Done', gtk.RESPONSE_OK)
        dialog.show_all()
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            for i in xrange(len(allExpense)):
                for j in xrange(len(allExpense[i])):
                    if str(searchphrase).lower() in \
                            str(allExpense[i][j]).lower():
                        tempAllExpense.append(allExpense[i])
            for i in xrange(len(allIncome)):
                for j in xrange(len(allIncome[i])):
                    if str(searchphrase).lower() in \
                            str(allIncome[i][j]).lower():
                        tempAllIncome.append(allIncome[i])
            for i in xrange(len(allSaving)):
                for j in xrange(len(allSaving[i])):
                    if str(searchphrase).lower() in \
                            str(allSaving[i][j]).lower():
                        tempAllSaving.append(allSaving[i])

            self.viewSearchResultsBrief(tempAllExpense, tempAllIncome,
                                        tempAllSaving, searchphrase)
        dialog.destroy()

    def viewSearchResultsBrief(self, allExpense, allIncome,
                               allSaving, searchphrase):
        def elements():
            table = gtk.Table(3, 1, True)
            if len(allExpense) == 0 and len(allIncome) == 0 \
                    and len(allSaving) == 0:
                label = gtk.Label('No result found')
                table.attach(label, 0, 1, 0, 3)
            else:
                resultsExpense = gtk.Label()
                resultsExpense.set_text(str(len(allExpense))+' \
                                        results found in Expenses database.')
                resultsIncome = gtk.Label()
                resultsIncome.set_text(str(len(allIncome))+' \
                                       results found in Incomes database.')
                resultsSaving = gtk.Label()
                resultsSaving.set_text(str(len(allSaving))+' \
                                       results found in Savings database.')

                table.attach(resultsExpense, 0, 1, 0, 1)
                table.attach(resultsIncome, 0, 1, 1, 2)
                table.attach(resultsSaving, 0, 1, 2, 3)
            return table

        pannableArea = hildon.PannableArea()
        pannableArea.add_with_viewport(elements())
        dialog = gtk.Dialog('Search results', self, gtk.DIALOG_NO_SEPARATOR |
                            gtk.DIALOG_DESTROY_WITH_PARENT)
        dialog.set_size_request(0, 200)
        dialog.vbox.add(pannableArea)
        dialog.add_button('View results', gtk.RESPONSE_OK)
        dialog.show_all()
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.viewSearchResults(allExpense, allIncome, allSaving,
                                   searchphrase)
        dialog.destroy()

    def viewSearchResults(self, allExpense, allIncome, allSaving,
                          searchphrase):
        window = hildon.StackableWindow()
        window.set_title("'"+searchphrase+"'")

        def editDetail(menuItem, id, date, amount, category, tag, EorI):
            global dateNew
            dateNew = date
            date = date.strip().split('-')
            year = date[0]
            month = date[1]
            day = date[2]
            global amountNew
            amountNew = amount
            global categoryNew
            categoryNew = category
            if tag is not None:
                global tagNew
                tagNew = tag
                global newTags
                newTags = []

            def getDate(self, widget):
                global dateNew
                dateNew = datetime.datetime.strptime(self.get_current_text(),
                                                     '%A, %B %d, %Y').date()

            def getAmount(self):
                global amountNew
                amountNew = self.get_text()
                self.set_text('')

            def getCategory(self):
                global categoryNew
                categoryNew = self.get_text()
                self.set_text('')
                selectorCategory.prepend_text(categoryNew)

            def selectionChangedCategory(self, widget):
                global categoryNew
                categoryNew = self.get_current_text()
                if tag is not None:
                    selectorTag.remove_column(0)
                    selectorTag.append_text_column(gtk.ListStore(str), 1)
                    cur.execute('select distinct Tag from Expenses where \
                                Category="'+categoryNew+'" order by Tag;')
                    c = cur.fetchall()
                    if len(c) > 0:
                        for i in xrange(len(c)):
                            selectorTag.insert_text(i, c[i][0])
                    else:
                        if len(newTags) > 0:
                            for i in xrange(len(newTags)):
                                selectorTag.prepend_text(newTags[i])
            if tag is not None:
                def getTag(self):
                    global tagNew
                    tagNew = self.get_text()
                    self.set_text('')
                    newTags.append(tag)
                    selectorTag.prepend_text(tag)

                def selectionChangedTag(self, widget):
                    global tagNew
                    tagNew = self.get_current_text()

            def elements():
                if tag is not None:
                    table = gtk.Table(4, 2, True)
                else:
                    table = gtk.Table(3, 2, True)
                buttonDate = \
                    hildon.DateButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                      gtk.HILDON_SIZE_FINGER_HEIGHT,
                                      hildon.BUTTON_ARRANGEMENT_VERTICAL)
                buttonDate.set_relief(gtk.RELIEF_NONE)
                buttonDate.set_date(int(year), int(month)-1, int(day))
                hildon.DateButton.get_selector(buttonDate).connect('changed',
                                                                   getDate)
                entryAmount = hildon.Entry(gtk.HILDON_SIZE_AUTO)
                entryAmount.set_text(str(amount))
                entryAmount.set_input_mode(gtk.HILDON_GTK_INPUT_MODE_NUMERIC)
                entryAmount.connect('activate', getAmount)
                entryCategory = hildon.Entry(gtk.HILDON_SIZE_AUTO)
                entryCategory.set_text(category)
                entryCategory.connect('activate', getCategory)
                global selectorCategory
                selectorCategory = hildon.TouchSelector(text=True)
                selectorCategory.remove_column(0)
                selectorCategory.append_text_column(gtk.ListStore(str), 1)
                if tag is not None:
                    cur.execute('select distinct Category from Expenses \
                                order by Category;')
                else:
                    if EorI == 'I':
                        cur.execute('select distinct Category from Incomes \
                                    order by Category;')
                    elif EorI == 'S':
                        cur.execute('select distinct Category from Savings \
                                    order by Category;')
                c = cur.fetchall()
                for i in xrange(len(c)):
                    selectorCategory.insert_text(i, c[i][0])
                selectorCategory.connect('changed', selectionChangedCategory)
                buttonCategory = \
                    hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                        gtk.HILDON_SIZE_FINGER_HEIGHT,
                                        hildon.BUTTON_ARRANGEMENT_VERTICAL)
                buttonCategory.set_style(hildon.BUTTON_STYLE_PICKER)
                buttonCategory.set_title('Category')
                buttonCategory.set_value(category)
                buttonCategory.set_relief(gtk.RELIEF_NONE)
                buttonCategory.set_selector(selectorCategory)
                if tag is not None:
                    entryTag = hildon.Entry(gtk.HILDON_SIZE_AUTO)
                    entryTag.set_text(tag)
                    entryTag.connect('activate', getTag)
                    global selectorTag
                    selectorTag = hildon.TouchSelector(text=True)
                    selectorTag.connect('changed', selectionChangedTag)
                    buttonTag = \
                        hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                            gtk.HILDON_SIZE_FINGER_HEIGHT,
                                            hildon.BUTTON_ARRANGEMENT_VERTICAL)
                    buttonTag.set_style(hildon.BUTTON_STYLE_PICKER)
                    buttonTag.set_title('Tag')
                    buttonTag.set_value(tag)
                    buttonTag.set_relief(gtk.RELIEF_NONE)
                    buttonTag.set_selector(selectorTag)

                if tag is not None:
                    table.attach(buttonDate, 0, 2, 0, 1)
                    table.attach(entryAmount, 0, 2, 1, 2)
                    table.attach(entryCategory, 0, 1, 2, 3)
                    table.attach(buttonCategory, 1, 2, 2, 3)
                    table.attach(entryTag, 0, 1, 3, 4)
                    table.attach(buttonTag, 1, 2, 3, 4)
                else:
                    table.attach(buttonDate, 0, 2, 0, 1)
                    table.attach(entryAmount, 0, 2, 1, 2)
                    table.attach(entryCategory, 0, 1, 2, 3)
                    table.attach(buttonCategory, 1, 2, 2, 3)
                return table

            pannableArea = hildon.PannableArea()
            pannableArea.add_with_viewport(elements())
            dialog = gtk.Dialog('Edit item', window, gtk.DIALOG_NO_SEPARATOR |
                                gtk.DIALOG_DESTROY_WITH_PARENT)
            dialog.set_size_request(0, 400)
            dialog.vbox.add(pannableArea)
            dialog.add_button('Done', gtk.RESPONSE_OK)
            dialog.show_all()
            response = dialog.run()
            if response == gtk.RESPONSE_OK:
                if tag is not None:
                    cur.execute('update Expenses set Date="'+str(dateNew)+'", \
                                Expense="'+str(amountNew)+'", \
                                Category="'+categoryNew+'", \
                                Tag="'+tagNew+'" where \
                                Id="'+str(id)+'";')
                    db.commit()
                else:
                    if EorI == 'I':
                        cur.execute('update Incomes set \
                                    Date="'+str(dateNew)+'", \
                                    Income="'+str(amountNew)+'", \
                                    Category="'+categoryNew+'" where \
                                    Id="'+str(id)+'";')
                        db.commit()
                    elif EorI == 'S':
                        cur.execute('update Savings set \
                                    Date="'+str(dateNew)+'", \
                                    Saving="'+str(amountNew)+'", \
                                    Category="'+categoryNew+'" where \
                                    Id="'+str(id)+'";')
                        db.commit()
                if year == Year and month == Month:
                    if View == 'Calendar':
                        self.remove(TableCalendar)
                        self.calendarView(Year, Month)
                    elif View == 'Main':
                        self.remove(Table)
                        self.mainView(Year, Month, None)
                window.destroy()
            dialog.destroy()

        def deleteDetail(menuItem, id, date, EorI):
            date = date.strip().split('-')
            year = date[0]
            month = date[1]
            label = gtk.Label('Delete selected item?')
            dialog = gtk.Dialog('', window, gtk.DIALOG_NO_SEPARATOR |
                                gtk.DIALOG_DESTROY_WITH_PARENT)
            dialog.set_size_request(0, 200)
            dialog.vbox.add(label)
            dialog.add_buttons('Yes', 1, 'No', 2)
            dialog.show_all()
            response = dialog.run()
            if response == 1:
                if EorI == 'E':
                    cur.execute('delete from Expenses where Id="'+str(id)+'"')
                    db.commit()
                elif EorI == 'I':
                    cur.execute('delete from Incomes where Id="'+str(id)+'"')
                    db.commit()
                elif EorI == 'S':
                    cur.execute('delete from Savings where Id="'+str(id)+'"')
                    db.commit()
                if year == Year and month == Month:
                    if View == 'Calendar':
                        self.remove(TableCalendar)
                        self.calendarView(Year, Month)
                    elif View == 'Main':
                        self.remove(Table)
                        self.mainView(Year, Month, None)
                window.destroy()
            elif response == 2:
                dialog.destroy()
            dialog.destroy()

        def details(list, EorI):
            if len(list) > 0:
                table = gtk.Table(len(list), 1, True)
            else:
                table = gtk.Table(1, 1, True)
            if EorI == 'E':
                for i in xrange(len(list)):
                    button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                           gtk.HILDON_SIZE_FINGER_HEIGHT,
                                           hildon.BUTTON_ARRANGEMENT_VERTICAL)
                    button.set_title(str(list[i][3])+' | '+str(list[i][4]))
                    button.set_value(str(list[i][1])+' | '+str(list[i][2])+' '+currency)
                    button.set_relief(gtk.RELIEF_NONE)
                    menu = gtk.Menu()
                    menu.set_name('hildon-context-sensitive-menu')
                    menuItemEdit = gtk.MenuItem('Edit')
                    menuItemEdit.connect('activate', editDetail, list[i][0],
                                         list[i][1], list[i][2], list[i][3],
                                         list[i][4], EorI)
                    menu.append(menuItemEdit)
                    menuItemDelete = gtk.MenuItem('Delete')
                    menuItemDelete.connect('activate', deleteDetail,
                                           list[i][0], list[i][1], EorI)
                    menu.append(menuItemDelete)
                    menu.show_all()
                    button.tap_and_hold_setup(menu)
                    button.set_size_request(0, 100)
                    table.attach(button, 0, 1, i, i+1)
            else:
                for i in xrange(len(list)):
                    button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                           gtk.HILDON_SIZE_FINGER_HEIGHT,
                                           hildon.BUTTON_ARRANGEMENT_VERTICAL)
                    button.set_title(str(list[i][3]))
                    button.set_value(str(list[i][1])+' | '+str(list[i][2])+' '+currency)
                    button.set_relief(gtk.RELIEF_NONE)
                    menu = gtk.Menu()
                    menu.set_name('hildon-context-sensitive-menu')
                    menuItemEdit = gtk.MenuItem('Edit')
                    menuItemEdit.connect('activate', editDetail, list[i][0],
                                         list[i][1], list[i][2], list[i][3],
                                         None, EorI)
                    menu.append(menuItemEdit)
                    menuItemDelete = gtk.MenuItem('Delete')
                    menuItemDelete.connect('activate', deleteDetail,
                                           list[i][0], list[i][1], EorI)
                    menu.append(menuItemDelete)
                    menu.show_all()
                    button.tap_and_hold_setup(menu)
                    button.set_size_request(0, 100)
                    table.attach(button, 0, 1, i, i+1)
            return table

        if len(allExpense) > 0 and len(allIncome) > 0 and len(allSaving) > 0:
            table = gtk.Table(9, 9, True)
            labelE = gtk.Label()
            labelE.set_text('Expenses database\n '+str(len(allExpense))+' \
                            results found')
            labelI = gtk.Label()
            labelI.set_text('Incomes database\n '+str(len(allIncome))+' \
                            results found')
            labelS = gtk.Label()
            labelS.set_text('Savings database\n '+str(len(allSaving))+' \
                            results found')
            pannableAreaE = hildon.PannableArea()
            pannableAreaE.add_with_viewport(details(allExpense, 'E'))
            pannableAreaI = hildon.PannableArea()
            pannableAreaI.add_with_viewport(details(allIncome, 'I'))
            pannableAreaS = hildon.PannableArea()
            pannableAreaS.add_with_viewport(details(allSaving, 'S'))
            table.attach(labelE, 0, 3, 0, 2)
            table.attach(labelI, 3, 6, 0, 2)
            table.attach(labelS, 6, 9, 0, 2)
            table.attach(pannableAreaE, 0, 3, 2, 9)
            table.attach(pannableAreaI, 3, 6, 2, 9)
            table.attach(pannableAreaS, 6, 9, 2, 9)
        elif len(allExpense) > 0 and len(allIncome) == 0 and \
                len(allSaving) == 0:
            table = gtk.Table(9, 1, True)
            label = gtk.Label()
            label.set_text('Expenses database\n '+str(len(allExpense))+' \
                           results found')
            pannableArea = hildon.PannableArea()
            pannableArea.add_with_viewport(details(allExpense, 'E'))
            table.attach(label, 0, 1, 0, 2)
            table.attach(pannableArea, 0, 1, 2, 9)
        elif len(allIncome) > 0 and len(allExpense) == 0 and \
                len(allSaving) == 0:
            table = gtk.Table(9, 1, True)
            label = gtk.Label()
            label.set_text('Incomes database\n '+str(len(allIncome))+' \
                           results found')
            pannableArea = hildon.PannableArea()
            pannableArea.add_with_viewport(details(allIncome, 'I'))
            table.attach(label, 0, 1, 0, 2)
            table.attach(pannableArea, 0, 1, 2, 9)
        elif len(allSaving) > 0 and len(allExpense) == 0 and \
                len(allIncome) == 0:
            table = gtk.Table(9, 1, True)
            label = gtk.Label()
            label.set_text('Savings database\n '+str(len(allSaving))+' \
                           results found')
            pannableArea = hildon.PannableArea()
            pannableArea.add_with_viewport(details(allSaving, 'S'))
            table.attach(label, 0, 1, 0, 2)
            table.attach(pannableArea, 0, 1, 2, 9)
        elif len(allSaving) > 0 and len(allExpense) > 0 and \
                len(allIncome) == 0:
            table = gtk.Table(9, 2, True)
            labelE = gtk.Label()
            labelE.set_text('Expenses database\n '+str(len(allExpense))+' \
                            results found')
            labelS = gtk.Label()
            labelS.set_text('Savings database\n '+str(len(allSaving))+' \
                            results found')
            pannableAreaE = hildon.PannableArea()
            pannableAreaE.add_with_viewport(details(allExpense, 'E'))
            pannableAreaS = hildon.PannableArea()
            pannableAreaS.add_with_viewport(details(allSaving, 'S'))
            table.attach(labelE, 0, 1, 0, 2)
            table.attach(labelS, 1, 2, 0, 2)
            table.attach(pannableAreaE, 0, 1, 2, 9)
            table.attach(pannableAreaS, 1, 2, 2, 9)
        elif len(allSaving) > 0 and len(allExpense) == 0 and \
                len(allIncome) > 0:
            table = gtk.Table(9, 2, True)
            labelI = gtk.Label()
            labelI.set_text('Incomes database\n '+str(len(allIncome))+' \
                            results found')
            labelS = gtk.Label()
            labelS.set_text('Savings database\n '+str(len(allSaving))+' \
                            results found')
            pannableAreaI = hildon.PannableArea()
            pannableAreaI.add_with_viewport(details(allIncome, 'I'))
            pannableAreaS = hildon.PannableArea()
            pannableAreaS.add_with_viewport(details(allSaving, 'S'))
            table.attach(labelI, 0, 1, 0, 2)
            table.attach(labelS, 1, 2, 0, 2)
            table.attach(pannableAreaI, 0, 1, 2, 9)
            table.attach(pannableAreaS, 1, 2, 2, 9)
        elif len(allSaving) == 0 and len(allExpense) > 0 and \
                len(allIncome) > 0:
            table = gtk.Table(9, 2, True)
            labelI = gtk.Label()
            labelI.set_text('Incomes database\n '+str(len(allIncome))+' \
                            results found')
            labelE = gtk.Label()
            labelE.set_text('Expenses database\n '+str(len(allExpense))+' \
                            results found')
            pannableAreaI = hildon.PannableArea()
            pannableAreaI.add_with_viewport(details(allIncome, 'I'))
            pannableAreaE = hildon.PannableArea()
            pannableAreaE.add_with_viewport(details(allExpense, 'E'))
            table.attach(labelI, 0, 1, 0, 2)
            table.attach(labelE, 1, 2, 0, 2)
            table.attach(pannableAreaI, 0, 1, 2, 9)
            table.attach(pannableAreaE, 1, 2, 2, 9)
        window.add(table)
        window.show_all()

    def viewDay(self, widget, day):
        if day < 10:
            day = '0'+str(day)
        else:
            day = str(day)
        global daywindow
        daywindow = hildon.StackableWindow()
        month = MonthNameList[Month]
        if day is not None:
            daywindow.set_title(day+' | '+month+' | '+Year)
        else:
            daywindow.set_title(month+' | '+Year)
        table = gtk.Table(1, 1, True)

        list1, list2, list3 = [], [], []

        cur.execute('select sum(Expense) from Expenses where \
                    strftime("%Y", Date)="'+Year+'" and \
                    strftime("%m", Date)="'+Month+'" and \
                    strftime("%d", Date)="'+day+'";')
        list1.append(cur.fetchone()[0])
        cur.execute('select sum(Income) from Incomes where \
                    strftime("%Y", Date)="'+Year+'" and \
                    strftime("%m", Date)="'+Month+'" and \
                    strftime("%d", Date)="'+day+'";')
        list2.append(cur.fetchone()[0])
        cur.execute('select sum(Saving) from Savings where \
                    strftime("%Y", Date)="'+Year+'" and \
                    strftime("%m", Date)="'+Month+'" and \
                    strftime("%d", Date)="'+day+'";')
        list3.append(cur.fetchone()[0])

        pannableArea = hildon.PannableArea()
        pannableArea.add(self.viewSum(list1, list2, list3, Year, Month, day))
        table.attach(pannableArea, 0, 1, 0, 1)
        daywindow.add(table)
        daywindow.show_all()

    def viewSum(self, list1, list2, list3, year, month, day):
        Expense = list1[0]
        Income = list2[0]
        Saving = list3[0]
        query = DatabaseQueries(year, month, day, currency)
        if day is not None:
            expenses_query = query.dayExpensesQuery()
            incomes_query = query.dayIncomesQuery()
            savings_query = query.daySavingsQuery()
            listDiffE, listDiffI, listDiffS = None, None, None
        else:
            expenses_query = query.mainExpensesQuery()
            listDiffE = expenses_query['diffs']
            incomes_query = query.mainIncomesQuery()
            listDiffI = incomes_query['diffs']
            savings_query = query.mainSavingsQuery()
            listDiffS = savings_query['diffs']
        listE1 = expenses_query['list1']
        listE2 = expenses_query['list2']
        listE3 = expenses_query['list3']
        listI1 = incomes_query['list1']
        listI2 = incomes_query['list2']
        listI3 = incomes_query['list3']
        listS1 = savings_query['list1']
        listS2 = savings_query['list2']
        listS3 = savings_query['list3']

        def onAct(treeview, path, data=None):
            global label
            global button
            global buttonByCategory
            if path[0] == 0:
                if Expense is not None:
                    label = gtk.Label(str(Expense)+' '+currency)
                else:
                    label = gtk.Label('No expense')
                image = gtk.Image()
                image.set_from_file('/opt/maemoneypot/img/add.png')
                button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                       gtk.HILDON_SIZE_FINGER_HEIGHT,
                                       hildon.BUTTON_ARRANGEMENT_VERTICAL)
                button.set_style(hildon.BUTTON_STYLE_NORMAL)
                button.set_relief(gtk.RELIEF_NONE)
                button.add(image)
                button.connect('clicked', self.AddExpense, day)
                buttonByCategory = \
                    hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                  gtk.HILDON_SIZE_AUTO_HEIGHT,
                                  hildon.BUTTON_ARRANGEMENT_VERTICAL)
                buttonByCategory.set_title('Expenses by category')
                buttonByCategory.connect('clicked', self.itemsByCategory,
                                         Expense, listE1, day)
                self.viewList(listE1, listE2, listE3, listDiffE, 'E',
                              year, month, day)
            if path[0] == 1:
                if Income is not None:
                    label = gtk.Label(str(Income)+' '+currency)
                else:
                    label = gtk.Label('No income')
                image = gtk.Image()
                image.set_from_file('/opt/maemoneypot/img/add.png')
                button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                       gtk.HILDON_SIZE_FINGER_HEIGHT,
                                       hildon.BUTTON_ARRANGEMENT_VERTICAL)
                button.set_style(hildon.BUTTON_STYLE_NORMAL)
                button.set_relief(gtk.RELIEF_NONE)
                button.add(image)
                button.connect('clicked', self.AddIncome, day)
                buttonByCategory = \
                    hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                  gtk.HILDON_SIZE_AUTO_HEIGHT,
                                  hildon.BUTTON_ARRANGEMENT_VERTICAL)
                buttonByCategory.set_title('Incomes by category')
                buttonByCategory.connect('clicked', self.itemsByCategory,
                                         Income, listI1, day)
                self.viewList(listI1, listI2, listI3, listDiffI, 'I',
                              year, month, day)
            if path[0] == 2:
                if Saving is not None:
                    label = gtk.Label(str(Saving)+' '+currency)
                else:
                    label = gtk.Label('No saving')
                image = gtk.Image()
                image.set_from_file('/opt/maemoneypot/img/add.png')
                button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                       gtk.HILDON_SIZE_FINGER_HEIGHT,
                                       hildon.BUTTON_ARRANGEMENT_VERTICAL)
                button.set_style(hildon.BUTTON_STYLE_NORMAL)
                button.set_relief(gtk.RELIEF_NONE)
                button.add(image)
                button.connect('clicked', self.AddSaving, day)
                buttonByCategory = \
                    hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                  gtk.HILDON_SIZE_AUTO_HEIGHT,
                                  hildon.BUTTON_ARRANGEMENT_VERTICAL)
                buttonByCategory.set_title('Savings by category')
                buttonByCategory.connect('clicked', self.itemsByCategory,
                                         Saving, listS1, day)
                self.viewList(listS1, listS2, listS3, listDiffS, 'S',
                              year, month, day)

        treestore = gtk.TreeStore(gtk.gdk.Pixbuf, str, str, str, str, str)
        if list1[0] is not None:
            treestore.append(None,
                             [gtk.gdk.pixbuf_new_from_file('/opt/maemoneypot/img/expenses.png'),
                              'Expenses ', '#f47500', str(list1[0])+' '+currency, '#f40005', '22'])
        else:
            treestore.append(None,
                             [gtk.gdk.pixbuf_new_from_file('/opt/maemoneypot/img/expenses.png'),
                              'Expenses ', '#f47500', 'No expense',
                              '#f40005', '22'])
        if list2[0] is not None:
            treestore.append(None,
                             [gtk.gdk.pixbuf_new_from_file('/opt/maemoneypot/img/incomes.png'),
                              'Incomes ', '#f47500', str(list2[0])+' '+currency, '#00f475', '22'])
        else:
            treestore.append(None,
                             [gtk.gdk.pixbuf_new_from_file('/opt/maemoneypot/img/incomes.png'),
                              'Incomes ', '#f47500', 'No income',
                              '#00f475', '22'])
        if list3[0] is not None:
            treestore.append(None,
                             [gtk.gdk.pixbuf_new_from_file('/opt/maemoneypot/img/savings.png'),
                              'Savings ', '#f47500', str(list3[0])+' '+currency, '#007ff4', '22'])
        else:
            treestore.append(None,
                             [gtk.gdk.pixbuf_new_from_file('/opt/maemoneypot/img/savings.png'),
                              'Savings ', '#f47500', 'No saving',
                              '#007ff4', '22'])
        treeview = gtk.TreeView(treestore)
        treeview.connect('row-activated', onAct)
        cellrenderer = gtk.CellRendererText()
        renderer = gtk.CellRendererPixbuf()
        treeview.append_column(gtk.TreeViewColumn('', renderer, pixbuf=0))
        treeview.append_column(gtk.TreeViewColumn('', cellrenderer,
                                                  text=1, foreground=2,
                                                  font=5))
        treeview.append_column(gtk.TreeViewColumn('', cellrenderer,
                                                  text=3, foreground=4,
                                                  font=5))
        return treeview

    def viewList(self, list1, list2, list3, listDiff, EorI, year, month, day):
        def onAct(treeview, path, treeviewcolumn):
            if treeview.row_expanded(path):
                treeview.collapse_row(path)

        def goToDetails(cell, path, model, treeview):
            p = [(int(path),)]
            row = model[path][0].strip().split('  ')
            category = row[0]
            sumExpense = row[1]
            self.viewDetails(category, sumExpense, day, p[0], treeview)

        global listwindow
        listwindow = hildon.StackableWindow()
        menu = hildon.AppMenu()
        listwindow.set_app_menu(menu)
        menu.append(buttonByCategory)
        menu.show_all()
        if day is not None:
            listwindow.set_title(day+' | '+MonthNameList[month]+' | '+year)
        else:
            listwindow.set_title(MonthNameList[month]+' | '+year)

        if listDiff is not None:
            treestore = gtk.TreeStore(str, str, str, str, str, str,
                                      gtk.gdk.Pixbuf)
        else:
            treestore = gtk.TreeStore(str, str, str, gtk.gdk.Pixbuf)
        k = 0
        for i in xrange(len(list1)):
            if listDiff is not None:
                if listDiff[i] == '':
                    diff = ''
                    diffColor = '#ffffff'
                elif '-' in listDiff[i] and EorI == 'E':
                    diff = listDiff[i]
                    diffColor = '#00f475'
                elif '-' in listDiff[i] and EorI == 'I':
                    diff = listDiff[i]
                    diffColor = '#f40005'
                elif listDiff[i] == '0.00%':
                    diff = 'Equal'
                    diffColor = '#007ff4'
                else:
                    if listDiff[i] != '' and EorI == 'E':
                        diff = '+'+listDiff[i]
                        diffColor = '#f40005'
                    elif listDiff[i] != '' and EorI == 'I':
                        diff = '+'+listDiff[i]
                        diffColor = '#00f475'
                if EorI == 'E':
                    iter = treestore.append(None,
                                            [list1[i], '#f47500', diff,
                                             diffColor, '16', '14',
                                             gtk.gdk.pixbuf_new_from_file('/opt/maemoneypot/img/goto.png')])
                else:
                    iter = treestore.append(None, [list1[i], '#f47500', diff,
                                                   diffColor, '16', '14',
                                                   None])
            else:
                '''It is a bit ugly but until I add detail viewing function to
                Incomes this remains this way... and will give error message in
                terminal if user taps on the Pixbuf column of the treeview...'''
                if EorI == 'E':
                    iter = treestore.append(None,
                                            [list1[i], '#f47500', '16',
                                             gtk.gdk.pixbuf_new_from_file('/opt/maemoneypot/img/goto.png')])
                else:
                    iter = treestore.append(None, [list1[i], '#f47500',
                                                   '16', None])
            if len(list3) != 0:
                for j in xrange(list3[i]):
                    if listDiff is not None:
                        treestore.append(iter, [list2[j+k], '#ffdcbd',
                                                None, '#ffffff', '14',
                                                None, None])
                    else:
                        treestore.append(iter, [list2[j+k], '#ffdcbd',
                                                '14', None])
                k = j+k+1
        treeview = gtk.TreeView(treestore)
        treeview.connect('row-activated', onAct)
        cellrenderer = gtk.CellRendererText()
        renderer = CellRendererClickablePixbuf()
        renderer.connect('clicked', goToDetails, treestore, treeview)
        if listDiff is not None:
            treeviewcolumn = gtk.TreeViewColumn('', cellrenderer, text=0,
                                                foreground=1, font=4)
            treeviewcolumn1 = gtk.TreeViewColumn('', cellrenderer, text=2,
                                                 foreground=3, font=5)
            treeviewcolumn2 = gtk.TreeViewColumn('', renderer, pixbuf=6)
            treeview.append_column(treeviewcolumn)
            treeview.append_column(treeviewcolumn1)
            treeview.append_column(treeviewcolumn2)
        else:
            treeviewcolumn = gtk.TreeViewColumn('', cellrenderer, text=0,
                                                foreground=1, font=2)
            treeview.append_column(treeviewcolumn)
            treeviewcolumn1 = gtk.TreeViewColumn('', renderer, pixbuf=3)
            treeview.append_column(treeviewcolumn1)

        pannableArea = hildon.PannableArea()
        pannableArea.add(treeview)
        table = gtk.Table(15, 4, True)
        table.attach(pannableArea, 0, 4, 3, 15)
        table.attach(button, 3, 4, 0, 3)
        table.attach(label, 0, 3, 0, 3)
        listwindow.add(table)
        listwindow.show_all()

    # ToDo: apply this function for incomes as well!
    def viewDetails(self, category, sumExpense, day, path, treeview):
        window = hildon.StackableWindow()

        def tagOrderQuery():
            if day is not None:
                cur.execute('select Id, Expense, Tag from Expenses where \
                            strftime("%Y", Date)="'+Year+'" and \
                            strftime("%m", Date)="'+Month+'" and \
                            strftime("%d", Date)="'+day+'" and \
                            Category="'+category+'" order by Tag;')
                window.set_title(category+' | '+day+' | \
                                 '+MonthNameList[Month]+' | '+Year)
            else:
                cur.execute('select Id, strftime("%d", Date), Expense, Tag \
                            from Expenses where \
                            strftime("%Y", Date)="'+Year+'" and \
                            strftime("%m", Date)="'+Month+'" and \
                            Category="'+category+'" order by Tag;')
                window.set_title(category+' | '+MonthNameList[Month]+' \
                                 | '+Year)
            row = cur.fetchall()
            return row

        def expenseOrderQuery():
            if day is not None:
                cur.execute('select Id, Expense, Tag from Expenses where \
                            strftime("%Y", Date)="'+Year+'" and \
                            strftime("%m", Date)="'+Month+'" and \
                            strftime("%d", Date)="'+day+'" and \
                            Category="'+category+'" order by Expense;')
                window.set_title(category+' | '+day+' | \
                                 '+MonthNameList[Month]+' | '+Year)
            else:
                cur.execute('select Id, strftime("%d", Date), Expense, Tag \
                            from Expenses where \
                            strftime("%Y", Date)="'+Year+'" and \
                            strftime("%m", Date)="'+Month+'" and \
                            Category="'+category+'" order by Expense;')
                window.set_title(category+' | '+MonthNameList[Month]+' | \
                                 '+Year)
            row = cur.fetchall()
            return row

        def dayOrderQuery():
            cur.execute('select Id, strftime("%d", Date), Expense, Tag \
                        from Expenses where \
                        strftime("%Y", Date)="'+Year+'" and \
                        strftime("%m", Date)="'+Month+'" and \
                        Category="'+category+'" order by \
                        strftime("%d", Date);')
            window.set_title(category+' | '+MonthNameList[Month]+' | '+Year)
            row = cur.fetchall()
            return row

        def editDetail(menuItem, id, d, expense, tag, order):
            global dateNew
            global expenseNew
            expenseNew = expense
            global categoryNew
            categoryNew = category
            global tagNew
            tagNew = tag
            global newTags
            newTags = []

            if d is not None:
                dateNew = Year+'-'+Month+'-'+d
            else:
                dateNew = Year+'-'+Month+'-'+day

            def getDate(self, widget):
                global dateNew
                dateNew = datetime.datetime.strptime(self.get_current_text(),
                                                     '%A, %B %d, %Y').date()

            def getExpense(self):
                global expenseNew
                expenseNew = self.get_text()
                self.set_text('')

            def getCategory(self):
                global categoryNew
                categoryNew = self.get_text()
                self.set_text('')
                selectorCategory.prepend_text(categoryNew)

            def selectionChangedCategory(self, widget):
                global categoryNew
                categoryNew = self.get_current_text()
                selectorTag.remove_column(0)
                selectorTag.append_text_column(gtk.ListStore(str), 1)
                cur.execute('select distinct Tag from Expenses where \
                            Category="'+categoryNew+'" order by Tag;')
                c = cur.fetchall()
                if len(c) > 0:
                    for i in xrange(len(c)):
                        selectorTag.insert_text(i, c[i][0])
                else:
                    if len(newTags) > 0:
                        for i in xrange(len(newTags)):
                            selectorTag.prepend_text(newTags[i])

            def getTag(self):
                global tagNew
                tagNew = self.get_text()
                self.set_text('')
                newTags.append(tag)
                selectorTag.prepend_text(tag)

            def selectionChangedTag(self, widget):
                global tagNew
                tagNew = self.get_current_text()

            def elements():
                table = gtk.Table(4, 2, True)
                buttonDate = \
                    hildon.DateButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                      gtk.HILDON_SIZE_FINGER_HEIGHT,
                                      hildon.BUTTON_ARRANGEMENT_VERTICAL)
                buttonDate.set_relief(gtk.RELIEF_NONE)
                if d is not None:
                    buttonDate.set_date(int(Year), int(Month)-1, int(d))
                else:
                    buttonDate.set_date(int(Year), int(Month)-1, int(day))
                hildon.DateButton.get_selector(buttonDate).connect('changed',
                                                                   getDate)
                entryExpense = hildon.Entry(gtk.HILDON_SIZE_AUTO)
                entryExpense.set_text(str(expense))
                entryExpense.set_input_mode(gtk.HILDON_GTK_INPUT_MODE_NUMERIC)
                entryExpense.connect('activate', getExpense)
                entryCategory = hildon.Entry(gtk.HILDON_SIZE_AUTO)
                entryCategory.set_text(category)
                entryCategory.connect('activate', getCategory)
                global selectorCategory
                selectorCategory = hildon.TouchSelector(text=True)
                selectorCategory.remove_column(0)
                selectorCategory.append_text_column(gtk.ListStore(str), 1)
                cur.execute('select distinct Category from Expenses \
                            order by Category;')
                c = cur.fetchall()
                for i in xrange(len(c)):
                    selectorCategory.insert_text(i, c[i][0])
                selectorCategory.connect('changed', selectionChangedCategory)
                buttonCategory = \
                    hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                        gtk.HILDON_SIZE_FINGER_HEIGHT,
                                        hildon.BUTTON_ARRANGEMENT_VERTICAL)
                buttonCategory.set_style(hildon.BUTTON_STYLE_PICKER)
                buttonCategory.set_title('Category')
                buttonCategory.set_value(category)
                buttonCategory.set_relief(gtk.RELIEF_NONE)
                buttonCategory.set_selector(selectorCategory)
                entryTag = hildon.Entry(gtk.HILDON_SIZE_AUTO)
                entryTag.set_text(tag)
                entryTag.connect('activate', getTag)
                global selectorTag
                selectorTag = hildon.TouchSelector(text=True)
                selectorTag.connect('changed', selectionChangedTag)
                buttonTag = \
                    hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                        gtk.HILDON_SIZE_FINGER_HEIGHT,
                                        hildon.BUTTON_ARRANGEMENT_VERTICAL)
                buttonTag.set_style(hildon.BUTTON_STYLE_PICKER)
                buttonTag.set_title('Tag')
                buttonTag.set_value(tag)
                buttonTag.set_relief(gtk.RELIEF_NONE)
                buttonTag.set_selector(selectorTag)

                table.attach(buttonDate, 0, 2, 0, 1)
                table.attach(entryExpense, 0, 2, 1, 2)
                table.attach(entryCategory, 0, 1, 2, 3)
                table.attach(buttonCategory, 1, 2, 2, 3)
                table.attach(entryTag, 0, 1, 3, 4)
                table.attach(buttonTag, 1, 2, 3, 4)
                return table

            pannableArea = hildon.PannableArea()
            pannableArea.add_with_viewport(elements())
            dialog = gtk.Dialog('Edit item', window,
                                gtk.DIALOG_NO_SEPARATOR |
                                gtk.DIALOG_DESTROY_WITH_PARENT)
            dialog.set_size_request(0, 400)
            dialog.vbox.add(pannableArea)
            dialog.add_button('Done', gtk.RESPONSE_OK)
            dialog.show_all()
            response = dialog.run()
            if response == gtk.RESPONSE_OK:
                cur.execute('update Expenses set Date="'+str(dateNew)+'", \
                            Expense="'+str(expenseNew)+'", \
                            Category="'+categoryNew+'", \
                            Tag="'+tagNew+'" where Id="'+str(id)+'";')
                db.commit()
                if day is not None:
                    self.remove(TableCalendar)
                    self.calendarView(Year, Month)
                    listwindow.destroy()
                    daywindow.destroy()
                else:
                    self.remove(Table)
                    self.mainView(Year, Month, None)
                    listwindow.destroy()
                window.destroy()
            dialog.destroy()

        def deleteDetail(menuItem, id, expense, order):
            label = gtk.Label('Delete selected item?')
            dialog = gtk.Dialog('', window, gtk.DIALOG_NO_SEPARATOR |
                                gtk.DIALOG_DESTROY_WITH_PARENT)
            dialog.set_size_request(0, 200)
            dialog.vbox.add(label)
            dialog.add_buttons('Yes', 1, 'No', 2)
            dialog.show_all()
            response = dialog.run()
            if response == 1:
                cur.execute('delete from Expenses where Id="'+str(id)+'"')
                db.commit()
                pannableArea.remove(pannableArea.get_child())
                if sumDetailsExpense-expense == 0:
                    label.set_text("<span size='24000'>No Expense</span>")
                else:
                    label.set_text("<span size='24000'> \
                                   "+str(sumDetailsExpense-expense)+" "+currency+"</span>")
                    if order == 'tag':
                        pannableArea.add_with_viewport(details
                                                       (tagOrderQuery(),
                                                        'tag'))
                    elif order == 'expense':
                        pannableArea.add_with_viewport(details
                                                       (expenseOrderQuery(),
                                                        'expense'))
                    elif order == 'day':
                        pannableArea.add_with_viewport(details
                                                       (dayOrderQuery(),
                                                        'day'))
                label.set_use_markup(True)
                label.modify_fg(gtk.STATE_NORMAL,
                                gtk.gdk.color_parse('#a0785a'))
                pannableArea.show_all()

                def onBack(window, data=None):
                    if day is not None:
                        self.remove(TableCalendar)
                        self.calendarView(Year, Month)
                        listwindow.destroy()
                        daywindow.destroy()
                    else:
                        self.remove(Table)
                        self.mainView(Year, Month, None)
                        listwindow.destroy()
                    window.destroy()
                window.connect('delete-event', onBack)
            elif response == 2:
                dialog.destroy()
            dialog.destroy()

        def details(row, order):
            if len(row) > 0:
                table = gtk.Table(len(row), 1, True)
                global sumDetailsExpense
                sumDetailsExpense = 0
            else:
                table = gtk.Table(1, 1, True)
            for i in xrange(len(row)):
                if day is not None:
                    button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                           gtk.HILDON_SIZE_FINGER_HEIGHT,
                                           hildon.BUTTON_ARRANGEMENT_VERTICAL)
                    button.set_title(row[i][2])
                    button.set_value(str(row[i][1])+' '+currency)
                    sumDetailsExpense = sumDetailsExpense+row[i][1]
                    button.set_relief(gtk.RELIEF_NONE)
                    menu = gtk.Menu()
                    menu.set_name('hildon-context-sensitive-menu')
                    menuItemEdit = gtk.MenuItem('Edit')
                    menuItemEdit.connect('activate', editDetail, row[i][0],
                                         None, row[i][1], row[i][2], order)
                    menu.append(menuItemEdit)
                    menuItemDelete = gtk.MenuItem('Delete')
                    menuItemDelete.connect('activate', deleteDetail,
                                           row[i][0], row[i][1], order)
                    menu.append(menuItemDelete)
                    menu.show_all()
                    button.tap_and_hold_setup(menu)
                else:
                    button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                           gtk.HILDON_SIZE_FINGER_HEIGHT,
                                           hildon.BUTTON_ARRANGEMENT_VERTICAL)
                    button.set_relief(gtk.RELIEF_NONE)
                    button.set_title(row[i][3])
                    button.set_value(row[i][1]+' | '+str(row[i][2])+' '+currency)
                    sumDetailsExpense = sumDetailsExpense+row[i][2]
                    menu = gtk.Menu()
                    menu.set_name('hildon-context-sensitive-menu')
                    menuItemEdit = gtk.MenuItem('Edit')
                    menuItemEdit.connect('activate', editDetail, row[i][0],
                                         row[i][1], row[i][2], row[i][3],
                                         order)
                    menu.append(menuItemEdit)
                    menuItemDelete = gtk.MenuItem('Delete')
                    menuItemDelete.connect('activate', deleteDetail,
                                           row[i][0], row[i][2], order)
                    menu.append(menuItemDelete)
                    menu.show_all()
                    button.tap_and_hold_setup(menu)

                button.set_size_request(0, 100)
                table.attach(button, 0, 1, i, i+1)
            return table

        def toggleExpenseOrder(widget):
            if widget.get_active():
                pannableArea.remove(pannableArea.get_child())
                pannableArea.add_with_viewport(details(expenseOrderQuery(),
                                                       'expense'))
                pannableArea.show_all()
                buttonTagOrder.set_active(False)
                if day is None:
                    buttonDayOrder.set_active(False)
            # else:
            #    buttonTagOrder.set_active(True)

        def toggleTagOrder(widget):
            if widget.get_active():
                pannableArea.remove(pannableArea.get_child())
                pannableArea.add_with_viewport(details(tagOrderQuery(), 'tag'))
                pannableArea.show_all()
                buttonExpenseOrder.set_active(False)
                if day is None:
                    buttonDayOrder.set_active(False)
            # else:
            #     buttonExpenseOrder.set_active(True)

        def toggleDayOrder(widget):
            if widget.get_active():
                pannableArea.remove(pannableArea.get_child())
                pannableArea.add_with_viewport(details(dayOrderQuery(), 'day'))
                pannableArea.show_all()
                buttonExpenseOrder.set_active(False)
                buttonTagOrder.set_active(False)
            # else:
            #     buttonTagOrder.set_active(True)

        table = gtk.Table(1, 2, True)
        if day is not None:
            tableDetails = gtk.Table(8, 2, True)
        else:
            tableDetails = gtk.Table(8, 3, True)
            buttonDayOrder = gtk.ToggleButton('Day')
            buttonDayOrder.set_relief(gtk.RELIEF_NONE)
            buttonDayOrder.connect('toggled', toggleDayOrder)
            tableDetails.attach(buttonDayOrder, 2, 3, 7, 8)

        label = gtk.Label()
        label.set_text("<span size='24000'>"+sumExpense+"</span>")
        label.set_use_markup(True)
        label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#a0785a'))
        pannableArea = hildon.PannableArea()
        pannableArea.add_with_viewport(details(tagOrderQuery(), 'tag'))
        # buttonTagOrder = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
        #                               gtk.HILDON_SIZE_FINGER_HEIGHT,
        #                               hildon.BUTTON_ARRANGEMENT_VERTICAL,
        #                               'Tag order')
        buttonTagOrder = gtk.ToggleButton('Tag')
        buttonTagOrder.set_relief(gtk.RELIEF_NONE)
        buttonTagOrder.connect('toggled', toggleTagOrder)
        # buttonExpenseOrder = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
        #                                   gtk.HILDON_SIZE_FINGER_HEIGHT,
        #                                   hildon.BUTTON_ARRANGEMENT_VERTICAL,
        #                                   'Expense order')
        buttonExpenseOrder = gtk.ToggleButton('Expense')
        buttonExpenseOrder.set_relief(gtk.RELIEF_NONE)
        buttonExpenseOrder.connect('toggled', toggleExpenseOrder)
        buttonTagOrder.set_active(True)
        graphDetails = matplotlibQuery.ExpensesByTags(sumExpense, Year,
                                                      Month, day, category)

        if day is not None:
            tableDetails.attach(label, 0, 2, 0, 1)
            tableDetails.attach(pannableArea, 0, 2, 1, 7)
        else:
            tableDetails.attach(label, 0, 3, 0, 1)
            tableDetails.attach(pannableArea, 0, 3, 1, 7)
        tableDetails.attach(buttonTagOrder, 0, 1, 7, 8)
        tableDetails.attach(buttonExpenseOrder, 1, 2, 7, 8)

        table.attach(tableDetails, 0, 1, 0, 1)
        table.attach(graphDetails, 1, 2, 0, 1)

        def onBack(self, data=None):
            if treeview.row_expanded(path):
                treeview.collapse_row(path)

        window.connect('delete-event', onBack)
        window.add(table)
        window.show_all()

    def AddExpense(self, widget, day):
        global date
        if day is not None:
            date = Year+'-'+Month+'-'+day
        else:
            date = time.strftime('%Y-%m-%d')
        global expense
        expense = None
        global category
        category = None
        global tag
        tag = None
        global newTags
        newTags = []

        def getDate(self, widget):
            global date
            date = datetime.datetime.strptime(self.get_current_text(),
                                              '%A, %B %d, %Y').date()

        def getExpense(self):
            global expense
            expense = self.get_text()
            self.set_text('')

        def getCategory(self):
            global category
            category = self.get_text()
            self.set_text('')
            selectorCategory.prepend_text(category)

        def selectionChangedCategory(self, widget):
            global category
            category = self.get_current_text()
            selectorTag.remove_column(0)
            selectorTag.append_text_column(gtk.ListStore(str), 1)
            cur.execute('select distinct Tag from Expenses where \
                        Category="'+category+'" order by Tag;')
            c = cur.fetchall()
            if len(c) > 0:
                for i in xrange(len(c)):
                    selectorTag.insert_text(i, c[i][0])
            else:
                if len(newTags) > 0:
                    for i in xrange(len(newTags)):
                        selectorTag.prepend_text(newTags[i])

        def getTag(self):
            global tag
            tag = self.get_text()
            self.set_text('')
            newTags.append(tag)
            selectorTag.prepend_text(tag)

        def selectionChangedTag(self, widget):
            global tag
            tag = self.get_current_text()

        def save(data=None):
            if expense is None:
                note = hildon.Note('information', window, 'You have to \
                                   specify expense!')
                gtk.Dialog.run(note)
                gtk.Dialog.hide(note)
            if category is None:
                note = hildon.Note('information', window, 'You have to \
                                   specify category!')
                gtk.Dialog.run(note)
                gtk.Dialog.hide(note)
            if tag is None:
                note = hildon.Note('information', window, 'You have to \
                                   specify tag!')
                gtk.Dialog.run(note)
                gtk.Dialog.hide(note)
            else:
                cur.execute('insert into Expenses(Date, Expense, \
                                                  Category, Tag) \
                            values("'+str(date)+'", "'+str(expense)+'", \
                            "'+str(category)+'", "'+str(tag)+'");')
                db.commit()
                iface.SystemNoteInfoprint('Expense was added to database')
                if category == settings[2][0:len(settings[2])-1]:
                    cur.execute('insert into Savings(Date, Saving, \
                                                     Category) \
                                values("'+str(date)+'", "'+str(expense)+'", \
                                "'+str(tag)+'");')
                    db.commit()

        def onBack(window, data=None):
            if day is not None:
                self.remove(TableCalendar)
                self.calendarView(Year, Month)
                listwindow.destroy()
                daywindow.destroy()
            else:
                self.remove(Table)
                self.mainView(Year, Month, None)
                listwindow.destroy()

        window = hildon.StackableWindow()
        window.connect('delete-event', onBack)
        window.set_title('Add Expense')
        table = gtk.Table(4, 8, True)
        buttonDate = hildon.DateButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                       gtk.HILDON_SIZE_FINGER_HEIGHT,
                                       hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonDate.set_style(hildon.BUTTON_STYLE_PICKER)
        buttonDate.set_title('')
        buttonDate.set_relief(gtk.RELIEF_NONE)
        if day is not None:
            buttonDate.set_date(int(Year), int(Month)-1, int(day))
        hildon.DateButton.get_selector(buttonDate).connect('changed', getDate)
        label = gtk.Label(currency)
        entryExpense = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entryExpense.set_placeholder('Add expense')
        entryExpense.set_input_mode(gtk.HILDON_GTK_INPUT_MODE_NUMERIC)
        entryExpense.connect('activate', getExpense)
        entryCategory = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entryCategory.set_placeholder('Add category')
        entryCategory.connect('activate', getCategory)
        selectorCategory = hildon.TouchSelector(text=True)
        selectorCategory.remove_column(0)
        selectorCategory.append_text_column(gtk.ListStore(str), 1)
        cur.execute('select distinct Category from Expenses \
                    order by Category;')
        c = cur.fetchall()
        for i in xrange(len(c)):
            selectorCategory.insert_text(i, c[i][0])
        selectorCategory.connect('changed', selectionChangedCategory)
        buttonCategory = \
            hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                gtk.HILDON_SIZE_FINGER_HEIGHT,
                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonCategory.set_style(hildon.BUTTON_STYLE_PICKER)
        buttonCategory.set_title('Category')
        buttonCategory.set_relief(gtk.RELIEF_NONE)
        buttonCategory.set_selector(selectorCategory)
        entryTag = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entryTag.set_placeholder('Add tag')
        entryTag.connect('activate', getTag)
        selectorTag = hildon.TouchSelector(text=True)
        selectorTag.connect('changed', selectionChangedTag)
        buttonTag = hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                        gtk.HILDON_SIZE_FINGER_HEIGHT,
                                        hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonTag.set_style(hildon.BUTTON_STYLE_PICKER)
        buttonTag.set_title('Tag')
        buttonTag.set_relief(gtk.RELIEF_NONE)
        buttonTag.set_selector(selectorTag)
        buttonSave = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                   gtk.HILDON_SIZE_FINGER_HEIGHT,
                                   hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonSave.set_style(hildon.BUTTON_STYLE_NORMAL)
        buttonSave.set_title('Save')
        buttonSave.set_relief(gtk.RELIEF_NONE)
        buttonSave.connect('clicked', save)
        table.attach(buttonDate, 0, 8, 0, 1)
        table.attach(label, 0, 4, 1, 2)
        table.attach(entryExpense, 4, 8, 1, 2)
        table.attach(entryCategory, 0, 2, 2, 3)
        table.attach(buttonCategory, 2, 4, 2, 3)
        table.attach(entryTag, 4, 6, 2, 3)
        table.attach(buttonTag, 6, 8, 2, 3)
        table.attach(buttonSave, 0, 8, 3, 4)
        window.add(table)
        window.show_all()

    def AddIncome(self, widget, day):
        global date
        if day is not None:
            date = Year+'-'+Month+'-'+day
        else:
            date = time.strftime('%Y-%m-%d')
        global income
        income = None
        global category
        category = None

        def getDate(self, widget):
            global date
            date = datetime.datetime.strptime(self.get_current_text(),
                                              '%A, %B %d, %Y').date()

        def getIncome(self):
            global income
            income = self.get_text()
            self.set_text('')

        def getCategory(self):
            global category
            category = self.get_text()
            self.set_text('')

        def selectionChangedCategory(self, widget):
            global category
            category = self.get_current_text()

        def save(data=None):
            if income is None:
                note = hildon.Note('information', window, 'You have to \
                                   specify income!')
                gtk.Dialog.run(note)
                gtk.Dialog.hide(note)
            if category is None:
                note = hildon.Note('information', window, 'You have to \
                                   specify category!')
                gtk.Dialog.run(note)
                gtk.Dialog.hide(note)
            else:
                cur.execute('insert into Incomes(Date, Income, Category) \
                            values("'+str(date)+'", "'+str(income)+'", \
                            "'+str(category)+'");')
                db.commit()
                bus = dbus.SystemBus()
                iface = \
                    dbus.Interface(bus.get_object('org.freedesktop.Notifications',
                                                  '/org/freedesktop/Notifications'),
                                   'org.freedesktop.Notifications')
                iface.SystemNoteInfoprint('Income was added to database')

        def onBack(window, data=None):
            if day is not None:
                self.remove(TableCalendar)
                self.calendarView(Year, Month)
                listwindow.destroy()
                daywindow.destroy()
            else:
                self.remove(Table)
                self.mainView(Year, Month, None)
                listwindow.destroy()

        window = hildon.StackableWindow()
        window.connect('delete-event', onBack)
        window.set_title('Add Income')
        table = gtk.Table(4, 4, True)
        buttonDate = hildon.DateButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                       gtk.HILDON_SIZE_FINGER_HEIGHT,
                                       hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonDate.set_style(hildon.BUTTON_STYLE_PICKER)
        buttonDate.set_title('')
        buttonDate.set_relief(gtk.RELIEF_NONE)
        if day is not None:
            buttonDate.set_date(int(Year), int(Month)-1, int(day))
        hildon.DateButton.get_selector(buttonDate).connect('changed', getDate)
        label = gtk.Label(currency)
        entryIncome = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entryIncome.set_placeholder('Add income')
        entryIncome.set_input_mode(gtk.HILDON_GTK_INPUT_MODE_NUMERIC)
        entryIncome.connect('activate', getIncome)
        entryCategory = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entryCategory.set_placeholder('Add category')
        entryCategory.connect('activate', getCategory)
        selectorCategory = hildon.TouchSelector(text=True)
        selectorCategory.remove_column(0)
        selectorCategory.append_text_column(gtk.ListStore(str), 1)
        cur.execute('select distinct Category from Incomes order by Category;')
        c = cur.fetchall()
        for i in xrange(len(c)):
            selectorCategory.insert_text(i, c[i][0])
        selectorCategory.connect('changed', selectionChangedCategory)
        buttonCategory = \
            hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                gtk.HILDON_SIZE_FINGER_HEIGHT,
                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonCategory.set_style(hildon.BUTTON_STYLE_PICKER)
        buttonCategory.set_title('Category')
        buttonCategory.set_relief(gtk.RELIEF_NONE)
        buttonCategory.set_selector(selectorCategory)
        buttonSave = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                   gtk.HILDON_SIZE_FINGER_HEIGHT,
                                   hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonSave.set_style(hildon.BUTTON_STYLE_NORMAL)
        buttonSave.set_title('Save')
        buttonSave.set_relief(gtk.RELIEF_NONE)
        buttonSave.connect('clicked', save)
        table.attach(buttonDate, 0, 4, 0, 1)
        table.attach(label, 0, 2, 1, 2)
        table.attach(entryIncome, 2, 4, 1, 2)
        table.attach(entryCategory, 0, 2, 2, 3)
        table.attach(buttonCategory, 2, 4, 2, 3)
        table.attach(buttonSave, 0, 4, 3, 4)
        window.add(table)
        window.show_all()

    def AddSaving(self, widget, day):
        global date
        if day is not None:
            date = Year+'-'+Month+'-'+day
        else:
            date = time.strftime('%Y-%m-%d')
        global saving
        saving = None
        global category
        category = None

        def getDate(self, widget):
            global date
            date = datetime.datetime.strptime(self.get_current_text(),
                                              '%A, %B %d, %Y').date()

        def getSaving(self):
            global saving
            saving = self.get_text()
            self.set_text('')

        def getCategory(self):
            global category
            category = self.get_text()
            self.set_text('')

        def selectionChangedCategory(self, widget):
            global category
            category = self.get_current_text()

        def save(data=None):
            if saving is None:
                note = hildon.Note('information', window, 'You have to \
                                   specify income!')
                gtk.Dialog.run(note)
                gtk.Dialog.hide(note)
            if category is None:
                note = hildon.Note('information', window, 'You have to \
                                   specify category!')
                gtk.Dialog.run(note)
                gtk.Dialog.hide(note)
            else:
                cur.execute('insert into Savings(Date, Saving, Category) \
                            values("'+str(date)+'", "'+str(saving)+'", \
                            "'+str(category)+'");')
                db.commit()
                cur.execute('insert into Expenses(Date, Expense, \
                                                  Category, Tag) \
                            values("'+str(date)+'", "'+str(saving)+'", \
                            "Saving", "'+str(category)+'");')
                db.commit()
                bus = dbus.SystemBus()
                iface = \
                    dbus.Interface(bus.get_object('org.freedesktop.Notifications',
                                                  '/org/freedesktop/Notifications'),
                                   'org.freedesktop.Notifications')
                iface.SystemNoteInfoprint('Income was added to database')

        def onBack(window, data=None):
            if day is not None:
                self.remove(TableCalendar)
                self.calendarView(Year, Month)
                listwindow.destroy()
                daywindow.destroy()
            else:
                self.remove(Table)
                self.mainView(Year, Month, None)
                listwindow.destroy()

        window = hildon.StackableWindow()
        window.connect('delete-event', onBack)
        window.set_title('Add Saving')
        table = gtk.Table(4, 4, True)
        buttonDate = hildon.DateButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                       gtk.HILDON_SIZE_FINGER_HEIGHT,
                                       hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonDate.set_style(hildon.BUTTON_STYLE_PICKER)
        buttonDate.set_title('')
        buttonDate.set_relief(gtk.RELIEF_NONE)
        if day is not None:
            buttonDate.set_date(int(Year), int(Month)-1, int(day))
        hildon.DateButton.get_selector(buttonDate).connect('changed', getDate)
        label = gtk.Label(currency)
        entryIncome = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entryIncome.set_placeholder('Add saving')
        entryIncome.set_input_mode(gtk.HILDON_GTK_INPUT_MODE_NUMERIC)
        entryIncome.connect('activate', getSaving)
        entryCategory = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entryCategory.set_placeholder('Add category')
        entryCategory.connect('activate', getCategory)
        selectorCategory = hildon.TouchSelector(text=True)
        selectorCategory.remove_column(0)
        selectorCategory.append_text_column(gtk.ListStore(str), 1)
        cur.execute('select distinct Category from Savings order by Category;')
        c = cur.fetchall()
        for i in xrange(len(c)):
            selectorCategory.insert_text(i, c[i][0])
        selectorCategory.connect('changed', selectionChangedCategory)
        buttonCategory = \
            hildon.PickerButton(gtk.HILDON_SIZE_AUTO_WIDTH |
                                gtk.HILDON_SIZE_FINGER_HEIGHT,
                                hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonCategory.set_style(hildon.BUTTON_STYLE_PICKER)
        buttonCategory.set_title('Category')
        buttonCategory.set_relief(gtk.RELIEF_NONE)
        buttonCategory.set_selector(selectorCategory)
        buttonSave = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH |
                                   gtk.HILDON_SIZE_FINGER_HEIGHT,
                                   hildon.BUTTON_ARRANGEMENT_VERTICAL)
        buttonSave.set_style(hildon.BUTTON_STYLE_NORMAL)
        buttonSave.set_title('Save')
        buttonSave.set_relief(gtk.RELIEF_NONE)
        buttonSave.connect('clicked', save)
        table.attach(buttonDate, 0, 4, 0, 1)
        table.attach(label, 0, 2, 1, 2)
        table.attach(entryIncome, 2, 4, 1, 2)
        table.attach(entryCategory, 0, 2, 2, 3)
        table.attach(buttonCategory, 2, 4, 2, 3)
        table.attach(buttonSave, 0, 4, 3, 4)
        window.add(table)
        window.show_all()

    def itemsByCategory(self, widget, amount, list, day):
        window = hildon.StackableWindow()
        if day is not None:
            window.set_title(day+' | '+MonthNameList[Month]+' | '+Year)
        else:
            window.set_title(MonthNameList[Month]+' | '+Year)
        table = gtk.Table(1, 1, True)
        items = matplotlibQuery.ItemsByCategory(amount, list)

        table.attach(items, 0, 1, 0, 1)
        window.add(table)
        window.show_all()


if __name__ == '__main__':
    if len(settings[0]) == 1 and len(settings[1]) == 1 and \
            len(settings[2]) == 1 and len(settings[3]) == 1:
        MainWindow().settings()
    else:
        if pwdEnabled == 'Enabled':
            MainWindow().password()
        else:
            if defaultView == 'Main':
                MainWindow().mainView(time.strftime('%Y'),
                                      time.strftime('%m'), None)
            elif defaultView == 'Calendar':
                MainWindow().calendarView(time.strftime('%Y'), time.strftime('%m'))
    hildon.Program.get_instance()
    gtk.main()
