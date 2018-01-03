#!/bin/sh

if [ -f "/home/user/.maemoneypot/.maemoneypotdb" ]; then
    mv /home/user/.maemoneypot/.maemoneypotdb /home/user/.maemoneypot/.maemoneypotdb.bak
fi

sqlite3 -batch /home/user/.maemoneypot/.maemoneypotdb.bak <<"EOF"
ATTACH DATABASE '/home/user/.maemoneypot/.maemoneypotdb' AS db KEY 'temporary_key';
CREATE TABLE db.Expenses(Id integer primary key, Date date, Expense int, Category varchar, Tag varchar);
CREATE TABLE db.Incomes(Id integer primary key, Date date, Income int, Category varchar);
CREATE TABLE db.Savings(Id integer primary key, Date date, Saving int, Category varchar);
INSERT INTO db.Expenses SELECT * FROM Expenses;
INSERT INTO db.Incomes SELECT * FROM Incomes;
INSERT INTO db.Savings SELECT * FROM Savings;
DETACH DATABASE db;
EOF
