# -*- coding:Utf-8 -*-
import gtk
import imp
import dbus
from pysqlcipher import dbapi2 as sql

'''This is fixed to exclude 'dummy user' actions
as the database content is definite'''
database = '/home/user/.maemoneypot/.maemoneypotdb'
db = sql.connect(database)
cur = db.cursor()

bus = dbus.SystemBus()
iface = dbus.Interface(bus.get_object('org.freedesktop.Notifications',
                                      '/org/freedesktop/Notifications'),
                       'org.freedesktop.Notifications')

print 'Checking if Matplotlib and Numpy are installed...'
try:
    imp.find_module('matplotlib')
    try:
        imp.find_module('numpy')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Wedge
        from matplotlib.backends.backend_gtkagg \
            import FigureCanvasGTKAgg as FigureCanvas
        import numpy as np
        modules = True
        print '\033[92m'+'Matplotlib and Numpy imported successfully'+'\033[0m'
        # pass
    except ImportError:
        modules = False
        print iface.SystemNoteDialog('\nOnly matplotlib installed. \
                                     You have to install numpy as well!\n',
                                     dbus.UInt32(0), 'Ok')
except ImportError:
    iface.SystemNoteDialog('\nMatplotlib module is not installed! \
                           You will not be able to use graphical \
                           functions of the application!\n',
                           dbus.UInt32(0), 'Ok')
    modules = False


class MatplotlibQueries(object):

    version = '0.2'

    def __init__(self, currency, key):
        self.currency = currency
        self.key = key

    def Speedclock(self, expense, income):
        if modules is False:
            label = gtk.Label()
            label.set_text('<span size="21000">You should install matplotlib \
                           module to see this...</span>')
            label.set_use_markup(True)
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#a0785a'))
            return label
        else:
            if income and expense is not None:
                available = str(income-expense)
                if income and expense != 0:
                    percentage = float(expense)/float(income)
                elif income == 0:
                    percentage = float(expense)/float(expense)
                elif expense == 0:
                    percentage = float(income)/float(expense)
                fig, ax = plt.subplots(1)
                patch = []
                rad = 0.2
                x, y = 0.4, 0.4
                patch.append(Wedge((x, y), rad, 315, 20.5, width=0.01,
                             color='#f40005', alpha=0.5))
                patch.append(Wedge((x, y), rad, 24.5, 88, width=0.01,
                             color='#f47500', alpha=0.5))
                patch.append(Wedge((x, y), rad, 92, 155.5, width=0.01,
                             color='#00f475', alpha=0.5))
                patch.append(Wedge((x, y), rad, 159.5, 225, width=0.01,
                             color='#00f475', alpha=0.5))
                patch.append(Wedge((x, y), 0.0125, 0, 360, width=0.0025,
                             color='#ffffff', alpha=0.5))
                if (float(percentage)*100)*2.7 > 225:
                    z = 360-(((float(percentage)*100)*2.7)-225)
                else:
                    z = 225-((float(percentage)*100)*2.7)
                    if z > 315:
                        z = 315
                patch.append(Wedge((x, y), rad, z, z, width=rad-0.0125,
                             color='#ffffff', alpha=0.9))
                for p in patch:
                    ax.add_patch(p)
                percentage = '%.1f%%' % float(percentage*100)
                plt.text(0.37, 0.2, percentage, fontsize=22,
                         color='#ffffff', alpha=0.9)
                plt.text(0.25, 0.21, '0', fontsize=16, fontweight='bold',
                         color='#a0785a', alpha=0.5)
                plt.text(0.18, 0.48, '25', fontsize=16, fontweight='bold',
                         color='#a0785a', alpha=0.5)
                plt.text(0.385, 0.61, '50', fontsize=16, fontweight='bold',
                         color='#a0785a', alpha=0.5)
                plt.text(0.6, 0.48, '75', fontsize=16, fontweight='bold',
                         color='#a0785a', alpha=0.5)
                plt.text(0.55, 0.21, '100', fontsize=16, fontweight='bold',
                         color='#a0785a', alpha=0.5)
                plt.text(0.7, 0.48, 'Available', fontsize=18,
                         fontweight='bold', color='#a0785a', alpha=0.5)
                plt.text(0.67, 0.37, available+u' '+self.currency,
                         fontsize=25, color='#ffffff', alpha=0.9)
                plt.axis('off')
                plt.xlim(0.2, 0.84)
                plt.ylim(0.2, 0.62)
                fig.set_facecolor('#101010')
                # fig.set_facecolor('#ffe5cd')
                # fig.set_frameon(False)
                canvas = FigureCanvas(fig)
                canvas.show()
                return canvas
            else:
                label = gtk.Label()
                label.set_text('<span size="21000">Nothing to display</span>')
                label.set_use_markup(True)
                label.modify_fg(gtk.STATE_NORMAL,
                                gtk.gdk.color_parse('#a0785a'))
                label.show()
                return label

    def MonthlySum(self, year):
        if modules is False:
            label = gtk.Label()
            label.set_text('<span size="21000">You should install \
                           matplotlib module to see this...</span>')
            label.set_use_markup(True)
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#a0785a'))
            return label
        else:
            cur.execute('PRAGMA key="'+self.key+'";')
            cur.execute('select count(distinct strftime("%m", Date)) \
                        from Expenses where \
                        strftime("%Y", Date) = "'+year+'";')
            count = cur.fetchone()
            cur.execute('select distinct strftime("%m", Date) \
                        from Expenses where \
                        strftime("%Y", Date) = "'+year+'" \
                        order by Date;')
            Months = []
            Expense = []
            Income = []
            for i in range(count[0]):
                row = cur.fetchone()
                Months.append(row[0])
            for m in Months:
                cur.execute('select sum(Expense) \
                            from Expenses where \
                            strftime("%Y", Date) = "'+year+'" \
                            and strftime("%m", Date) = "'+str(m)+'";')
                row = cur.fetchone()
                Expense.append(row[0])
                cur.execute('select sum(Income) \
                            from Incomes where \
                            strftime("%Y", Date) = "'+year+'" \
                            and strftime("%m", Date) = "'+str(m)+'";')
                row = cur.fetchone()
                Income.append(row[0])
            if count[0] != 0:
                c = np.arange(len(Months))
                p = plt.figure(dpi=96, facecolor='#101010')
                plt.plot(c, Expense, linestyle='-', marker='v',
                         color='#f40005', alpha=0.5, label='Expenses',
                         markersize=8)
                plt.plot(c, Income, linestyle='-', marker='^',
                         color='#00f475', alpha=0.5, label='Incomes',
                         markersize=8)
                # for i in range(len(Expense)):
                #      plt.text(c[i],Expense[i],Expense[i],color='#f47500')
                # for i in range(len(Income)):
                #       plt.text(c[i],Income[i],Income[i],color='#f47500')
                # plt.legend(borderpad=0.2,loc=3,ncol=2,mode='expand',bbox_to_anchor=(0.,1.02,1.,.102))
                if Income[0] is not None:
                    i = 0
                    for num in c:
                        plt.text(num, max(Income)+(max(Income)/23), Months[i],
                                 fontsize=14, fontweight="bold",
                                 color="#a0785a", alpha=0.6)
                        i = i+1
                else:
                    i = 0
                    for num in c:
                        plt.text(num, max(Expense)+(max(Expense)/4), Months[i],
                                 fontsize=14, fontweight="bold",
                                 color="#a0785a", alpha=0.6)
                        i = i+1

                # plt.xlim(-0.5,len(c)-0.5)
                # plt.ylim(0,max(Expense))
                # plt.xticks(c,Months)
                # plt.yticks([],"")
                # plt.yticks([100000,200000,300000],["100000","200000","300000"])
                plt.axis('off')
                p.set_facecolor('#101010')
                # p.set_facecolor('#ffe5cd')
                # p.set_frameon(False)
                canvas = FigureCanvas(p)
                canvas.show()
                return canvas
            else:
                label = gtk.Label()
                label.set_text('<span size="21000">Nothing to display</span>')
                label.set_use_markup(True)
                label.modify_fg(gtk.STATE_NORMAL,
                                gtk.gdk.color_parse('#a0785a'))
                label.show()
                return label

    def ExpensesByTags(self, sumExpense, year, month, day, category):
        if modules is False:
            label = gtk.Label()
            label.set_text('<span size="21000">You should install \
                           matplotlib module to see this...</span>')
            label.set_use_markup(True)
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#a0785a'))
            return label
        else:
            sumExpense = (sumExpense.strip().split(' '))[0]
            if sumExpense > 0:
                cur.execute('PRAGMA key="'+self.key+'";')
                if day is not None:
                    cur.execute('select distinct Tag, sum(Expense) \
                                from Expenses where \
                                strftime("%Y", Date)="'+year+'" \
                                and strftime("%m", Date)="'+month+'" \
                                and strftime("%d", Date)="'+day+'" \
                                and Category="'+category+'" group by Tag;')
                else:
                    cur.execute('select distinct Tag, sum(Expense) \
                                from Expenses where \
                                strftime("%Y", Date)="'+year+'" \
                                and strftime("%m", Date)="'+month+'" \
                                and Category="'+category+'" group by Tag;')
                t = cur.fetchall()
                Legend = []
                degree = []
                for i in xrange(len(t)):
                    degree.append((float(t[i][1])/float(sumExpense))*360)
                    Legend.append(t[i][0]+" %.1f%%"
                                  % float(str((float(t[i][1]) /
                                               float(sumExpense))*100)))

                fig, ax = plt.subplots(1)
                patch = []
                x, y = 0.21, 0.15
                col = np.random.rand(50)
                rad = 0.25
                patch.append(Wedge((x, y), rad, 0, degree[0], width=0.1,
                             color=col, alpha=0.5))
                j = degree[0]
                for i in range(1, len(degree)):
                    col = np.random.rand(50)
                    patch.append(Wedge((x, y), rad, j, j+degree[i], width=0.1,
                                 color=col, alpha=0.5))
                    j = j+degree[i]
                for i in patch:
                    ax.add_patch(i)
                plt.axis('off')
                plt.xlim(-0.05, 0.9)
                plt.ylim(-0.1, 0.4)
                leg = plt.legend(Legend, frameon=False, prop={'size': 12},
                                 borderpad=0.3, labelspacing=0.6,
                                 loc='upper left', bbox_to_anchor=(0.54, 1.1))
                for i in leg.get_texts():
                    plt.setp(i, color='#ffffff')
                fig.set_facecolor('#101010')
                # fig.set_frameon(False)
                canvas = FigureCanvas(fig)
                # canvas.set_size_request(500,0)
                return canvas
            else:
                label = gtk.Label()
                label.set_text('<span size="21000">Nothing to display</span>')
                label.set_use_markup(True)
                label.modify_fg(gtk.STATE_NORMAL,
                                gtk.gdk.color_parse('#a0785a'))
                label.show()
                return label

    def ItemsByCategory(self, Amount, list):
        if modules is False:
            label = gtk.Label()
            label.set_text('<span size="21000">You should install \
                           matplotlib module to see this...</span>')
            label.set_use_markup(True)
            label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#a0785a'))
            return label
        else:
            if Amount is not None and int(Amount) > 0:
                Legend = []
                degree = []
                categories = []
                amounts = []
                for i in list:
                    category = i.strip().split('  ')
                    amount = category[1].strip().split(' ')
                    categories.append(category[0])
                    amounts.append(int(amount[0]))
                for i in xrange(len(categories)):
                    degree.append((float(amounts[i])/float(str(Amount)))*360)
                    Legend.append(categories[i]+" %.1f%%"
                                  % float(str((float(amounts[i]) /
                                               float(str(Amount)))*100)))

                fig, ax = plt.subplots(1)
                patch = []
                x, y = 0.21, 0.15
                col = np.random.rand(50)
                rad = 0.25
                patch.append(Wedge((x, y), rad, 0, degree[0], width=0.1,
                             color=col, alpha=0.5))
                j = degree[0]
                for i in range(1, len(degree)):
                    col = np.random.rand(50)
                    patch.append(Wedge((x, y), rad, j, j+degree[i],
                                 width=0.1, color=col, alpha=0.5))
                    j = j+degree[i]
                for i in patch:
                    ax.add_patch(i)
                plt.axis('off')
                plt.xlim(-0.05, 0.9)
                plt.ylim(-0.1, 0.4)
                leg = plt.legend(Legend, frameon=False,
                                 prop={'size': 16}, borderpad=0.3,
                                 labelspacing=0.6, loc='upper left',
                                 bbox_to_anchor=(0.54, 1.1))
                for i in leg.get_texts():
                    plt.setp(i, color='#ffffff')
                fig.set_facecolor('#101010')
                # fig.set_frameon(False)
                canvas = FigureCanvas(fig)
                # canvas.set_size_request(500,0)
                return canvas
            else:
                label = gtk.Label()
                label.set_text('<span size="21000">Nothing \
                               to display</span>')
                label.set_use_markup(True)
                label.modify_fg(gtk.STATE_NORMAL,
                                gtk.gdk.color_parse('#a0785a'))
                label.show()
                return label
