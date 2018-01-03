# maemoneypot
An expense, income and saving tracker for Nokia N900 with some extended functions such as different views, graphs.

# ToDo
- Apply details view for incomes and savings
- Connect savings and expense more
- Add export-import-backup functionality
- Make multiple edition available (e.g. whole category)
- Full portrait support - this is quite a good question on n900... Relayout windows on rotation if there is a graph
- More report options (more charts, report between dates, compare years/categories, etc.)
- Make "add budget" option available
- Make bill/reminder option available
- Make recurring expense/income/saving option available
- Automatic rollover between months

# Description

The application does not depend on matplotlib and numpy directly. If you do not have those installed you just simply cannot see the graphs. 
Important: there is no automatic rollover so if you have some money at the end of the month you have to enter that manually for next month's income (maybe I should add rollover function too).

There are two views available: 
- Main view
- Calendar view

Main view: 
You can see all expenses, incomes for the current month, and all Savings that you added so far to the database (not just for current month). You can tap all of them. 
There is a “speedclock” that shows all expense as percentage of all income. 
There is a trend line that shows all expense and all income for the months of the current year. 

If you tap on expenses, incomes or savings you can see the detailed view for the current month by category. There is a menu button that shows a graph which represents summarized expense for categories as percentage of all expense for that month. 
There is also a button which you can click on and add an entry.
There is the category name, amount of money and if there is a difference (+percentage, -percentage, equal) to previous month for that category. If there were no such expense, income or saving for that category in previous month then there is no text. 

There is a difference between expenses, incomes, and savings as for expenses you can add tags. If you tap on a particular category (preferably left side of the screen) then the current row is expanded and you can see the summarized tags and expenses for that tag. 

There is an arrow which you can tap and see the very details for that category: on the left side of the window you can see every entry that is in the database. You can change order by tag, day, and expense. On the right side of the window there is a graph that shows summarized expense for tags as percentage of all expense for that category. If you long press on a particular entry you can edit or delete that entry.

For incomes and savings there are no such options (yet) because for incomes and savings you can specify only category. Therefore you can modify these entries in a different way (I shall improve this in the future).

If you want to add an entry you have to tap on the button next to the all expenses label. The date is automatically set to current date. For amount of money you can enter only numbers (do not have to use blue arrow key with keyboard!). You can specify categories in the entry box or if there is any in the database then you select it from the list if you click on the category button. For expenses there is a tag entry and button. If you selected a category then all tags for that category are shown when you click on the tag button. But you can specify new ones in the entry as well. Be aware the latest information will be written to the database (e.g.: you selected a category but want to modify that you can simply choose another one or specify a new one in the entry). In the entry box you always have to press “enter” to store the information. 
If everything is set you can click on “save”. If something is missing there will be a warning and no entry will be written to the database. If all data is set then clicking on save button will save that entry to the database and a short message will be shown about that. Important! If you add something to savings then it will be set into expenses as “Saving” category! Be aware that all the latest information are stored so if you click on save button again then it will write those information to the database again. For me the advantage of this is that iIf you would like you can set another entry by changing only category or amount or tag or date. This eases setting more entries with the similar category for example as you have to modify only tag and amount of money. If you do not want to set more entry you only have to press on back arrow. Then you will be taken to the main view and all the data will be refreshed. 

Calendar view:
There is a calendar for the particular month. In the calendar you can see expenses, incomes and savings for that day. If you tap on a day then you can see the summarized information for that day – from here all the functions are the same as written in main view. The advantage of calendar view is that if you want to see a particular day or want to add an entry for that day you can do that. In the adding window date is automatically set to that date and all the details are shown for that day if you go to the details window. 

There are menu buttons both in calendar view and main view: 
- Next month
- Previous month
- Specific month
- A button which you can change the view with
- Settings
- Search

I hope the names are speaking for themselves… (: But here are some details:
- Specific month can be selected between 2016 and 2045
- In settings window you can set currency, default view and an expense which if you add to expenses then it will be automatically set as a saving as well (so you do not have to add that amount to savings). 
- You can search for everything and anything in all three databases – no whole words required and capital letter doesn’t matter. Incomes and savings entries can be modified or deleted only this way (for now). Important! If you modify or delete a saving entry, the “connected” expense entry remains the same as before (no automatic modification or deletion done) so you have to manually modify that expense entry as well (and vice versa: if you modify an expense which is technically a saving entry, the saving entry remains…).

# Known bugs

- Date selection with hildon.DateButton results segmentation fault when no date selected – i.e. the user taps outside the date selection dialog. This does not happen in the search window though… 
- Sometimes warnings are raised – maybe in connection to rotation and matplotlib. E.g.: weakref.py:232 – assertion G_IS_OBJECT failed. 
- hildon button relief setting (i.e.: hildon.Button().set_relief(gtk.RELIEF_NONE)) does not always work so it looks like a normal button.
