import sqlite3 as sql

database = '/home/user/.maemoneypot/.maemoneypotdb'

db = sql.connect(database)
cur = db.cursor()


class DatabaseQueries(object):

    version = '0.1'

    def __init__(self, year, month, day, currency):
        self.year = year
        self.month = month
        self.day = day
        self.currency = currency

    def mainExpensesQuery(self):
        list1, list2, list3 = [], [], []
        cur.execute('select distinct Category, sum(Expense) \
                    from Expenses where \
                    strftime("%Y", Date)="'+self.year+'" \
                    and strftime("%m", Date)="'+self.month+'" \
                    group by Category;')
        c = cur.fetchall()
        if int(self.month)-1 < 10:
            month = '0'+str(int(self.month)-1)
        else:
            month = str(int(self.month)-1)
        if month == '00':
            month = '12'
            year = str(int(self.year)-1)
        else:
            year = self.year
        cur.execute('select distinct Category, sum(Expense) \
                    from Expenses where \
                    strftime("%Y", Date)="'+year+'" \
                    and strftime("%m", Date)="'+month+'" \
                    group by Category;')
        c1 = cur.fetchall()
        diffs = []
        for i in xrange(len(c)):
            if c[i][0] is not None:
                diff = ''
                for j in xrange(len(c1)):
                    if c[i][0] == c1[j][0]:
                        diff = '%.2f%%' \
                                % ((float(c[i][1])/float(c1[j][1])*100)-100)
                        break
                diffs.append(diff)
                l1 = c[i][0]+'  '+str(c[i][1])+' '+self.currency
                list1.append(l1)
                cur.execute('select distinct Tag, sum(Expense) \
                            from Expenses where \
                            strftime("%Y", Date)="'+self.year+'" \
                            and strftime("%m", Date)="'+self.month+'" \
                            and Category="'+c[i][0]+'" group by Tag;')
                t = cur.fetchall()
                for j in xrange(len(t)):
                    if t[j][0] is not None:
                        l2 = t[j][0]+'  '+str(t[j][1])+' '+self.currency
                        list2.append(l2)
                list3.append(len(t))
        return {'list1': list1, 'list2': list2,
                'list3': list3, 'diffs': diffs}

    def mainIncomesQuery(self):
        list1, list2, list3 = [], [], []
        cur.execute('select distinct Category, sum(Income) \
                    from Incomes where \
                    strftime("%Y", Date)="'+self.year+'" \
                    and strftime("%m", Date)="'+self.month+'" \
                    group by Category;')
        c = cur.fetchall()
        if int(self.month)-1 < 10:
            month = '0'+str(int(self.month)-1)
        else:
            month = str(int(self.month)-1)
        if month == '00':
            month = '12'
            year = str(int(self.year)-1)
        else:
            year = self.year
        cur.execute('select distinct Category, sum(Income) \
                    from Incomes where \
                    strftime("%Y", Date)="'+year+'" \
                    and strftime("%m", Date)="'+month+'" \
                    group by Category;')
        c1 = cur.fetchall()
        diffs = []
        for i in xrange(len(c)):
            if c[i][0] is not None:
                diff = ''
                for j in xrange(len(c1)):
                    if c[i][0] == c1[j][0]:
                        diff = '%.2f%%' \
                                % ((float(c[i][1])/float(c1[j][1])*100)-100)
                        break
                diffs.append(diff)
                l1 = c[i][0]+'  '+str(c[i][1])+' '+self.currency
                list1.append(l1)
        list2, list3 = [], []
        return {'list1': list1, 'list2': list2,
                'list3': list3, 'diffs': diffs}

    def mainSavingsQuery(self):
        list1, list2, list3 = [], [], []
        cur.execute('select distinct Category, sum(Saving) \
                    from Savings where \
                    strftime("%Y", Date)="'+self.year+'" \
                    and strftime("%m", Date)="'+self.month+'" \
                    group by Category;')
        c = cur.fetchall()
        if int(self.month)-1 < 10:
            month = '0'+str(int(self.month)-1)
        else:
            month = str(int(self.month)-1)
        if month == '00':
            month = '12'
            year = str(int(self.year)-1)
        else:
            year = self.year
        cur.execute('select distinct Category, sum(Saving) \
                    from Savings where \
                    strftime("%Y", Date)="'+year+'" \
                    and strftime("%m", Date)="'+month+'" \
                    group by Category;')
        c1 = cur.fetchall()
        diffs = []
        for i in xrange(len(c)):
            if c[i][0] is not None:
                diff = ''
                for j in xrange(len(c1)):
                    if c[i][0] == c1[j][0]:
                        diff = '%.2f%%' \
                                % ((float(c[i][1])/float(c1[j][1])*100)-100)
                        break
                diffs.append(diff)
                l1 = c[i][0]+'  '+str(c[i][1])+' '+self.currency
                list1.append(l1)
        list2, list3 = [], []
        return {'list1': list1, 'list2': list2,
                'list3': list3, 'diffs': diffs}

    def dayExpensesQuery(self):
        list1, list2, list3 = [], [], []
        cur.execute('select distinct Category, sum(Expense) \
                    from Expenses where \
                    strftime("%Y", Date)="'+self.year+'" \
                    and strftime("%m", Date)="'+self.month+'" \
                    and strftime("%d", Date)="'+self.day+'" \
                    group by Category;')
        c = cur.fetchall()
        for i in xrange(len(c)):
            if c[i][0] is not None:
                l1 = c[i][0]+'  '+str(c[i][1])+' '+self.currency
                list1.append(l1)
                cur.execute('select distinct Tag, sum(Expense) \
                            from Expenses where \
                            strftime("%Y", Date)="'+self.year+'" \
                            and strftime("%m", Date)="'+self.month+'" \
                            and strftime("%d", Date)="'+self.day+'" \
                            and Category="'+c[i][0]+'" \
                            group by Tag;')
                t = cur.fetchall()
                for j in xrange(len(t)):
                    if t[j][0] is not None:
                        l2 = t[j][0]+'  '+str(t[j][1])+' '+self.currency
                        list2.append(l2)
                list3.append(len(t))
        return {'list1': list1, 'list2': list2,
                'list3': list3}

    def dayIncomesQuery(self):
        list1, list2, list3 = [], [], []
        cur.execute('select distinct Category, sum(Income) \
                    from Incomes where \
                    strftime("%Y", Date)="'+self.year+'" \
                    and strftime("%m", Date)="'+self.month+'" \
                    and strftime("%d", Date)="'+self.day+'" \
                    group by Category;')
        c = cur.fetchall()
        for i in xrange(len(c)):
            if c[i][0] is not None:
                l1 = c[i][0]+'  '+str(c[i][1])+' '+self.currency
                list1.append(l1)
        list2, list3 = [], []
        return {'list1': list1, 'list2': list2,
                'list3': list3}

    def daySavingsQuery(self):
        list1, list2, list3 = [], [], []
        cur.execute('select distinct Category, sum(Saving) \
                    from Savings where \
                    strftime("%Y", Date)="'+self.year+'" \
                    and strftime("%m", Date)="'+self.month+'" \
                    and strftime("%d", Date)="'+self.day+'" \
                    group by Category;')
        c = cur.fetchall()
        for i in xrange(len(c)):
            if c[i][0] is not None:
                l1 = c[i][0]+'  '+str(c[i][1])+' '+self.currency
                list1.append(l1)
        list2, list3 = [], []
        return {'list1': list1, 'list2': list2,
                'list3': list3}
