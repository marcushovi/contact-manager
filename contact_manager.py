import sqlite3
import tkinter.messagebox as tkMessageBox
import tkinter.ttk as ttk
from tkinter import *
import re
from datetime import date

# CONSTANTS
FILE_NAME = "data.db"
BACKGROUND_COLOR = "#085589"
EMAIL_VALIDATION_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_VALIDATION_REGEX = r'\+([0-9]+( [0-9]+)+)'
BIRTHDATE_VALIDATION_REGEX = r'([0-9]+(\.[0-9]+)+)'

# root window
root = Tk()
root.title("Contact Manager")
width = 700
height = 500
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (width / 2)
y = (screen_height / 2) - (height / 2)
root.geometry("%dx%d+%d+%d" % (width, height, x, y))
root.resizable(0, 0)
root.config(bg=BACKGROUND_COLOR)

# Variables
NAME = StringVar()
BIRTHDAY = StringVar()
EMAIL = StringVar()
TEL = StringVar()
DESC = StringVar()
SEARCH_Q = StringVar()


def clear_fields() -> None:
    NAME.set("")
    BIRTHDAY.set("")
    EMAIL.set("")
    TEL.set("")
    DESC.set("")

# executing query to database
def execute_command_db(*command) -> None:
    conn = sqlite3.connect(FILE_NAME)
    cursor = conn.cursor()
    if len(command) > 1:
        cursor.execute(command[0],
                       (command[1])
                       )
    else:
        cursor.execute(*command)

    conn.commit()

    fetch = cursor.fetchall()

    if fetch:
        for data in fetch:
            tree.insert('', 'end', values=data)

    cursor.close()
    conn.close()


def initialize_database() -> None:
    execute_command_db(
        "CREATE TABLE IF NOT EXISTS `contacts` (_id INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT, name TEXT, "
        "birthday TEXT, email TEXT, tel TEXT, desc TEXT)"
    )

    execute_command_db("SELECT * FROM `contacts` ORDER BY `name` ASC")

# input validation
def is_input_valid() -> None:
    msg = ""

    if NAME.get() == "":
        msg = 'Name is required!'
    elif EMAIL.get() != "" and not re.fullmatch(EMAIL_VALIDATION_REGEX, str(EMAIL.get())):
        msg = "Email is not valid!"
    elif TEL.get() != "" and not re.fullmatch(PHONE_VALIDATION_REGEX, str(TEL.get())):
        msg = "Phone number is not valid!"
    elif BIRTHDAY.get() != "" and not re.fullmatch(BIRTHDATE_VALIDATION_REGEX, str(BIRTHDAY.get())):
        msg = "Birthdate is not valid!"

    if msg:
        tkMessageBox.showwarning('', msg, icon="warning")
        return False
    else:
        return True

# create contact
def create_contact() -> None:
    if is_input_valid():
        tree.delete(*tree.get_children())

        execute_command_db(
            "INSERT INTO `contacts` (name, birthday, email, tel, desc) VALUES(?, ?, ?, ?, ?)", (
                str(NAME.get()), str(BIRTHDAY.get()), str(EMAIL.get()), str(TEL.get()), str(DESC.get()),
            )
        )

        execute_command_db("SELECT * FROM `contacts` ORDER BY `name` ASC")

        clear_fields()

# update specific contact
def update_contact() -> None:
    if is_input_valid():
        tree.delete(*tree.get_children())
        execute_command_db(
            "UPDATE `contacts` SET `name` = ?, `birthday` = ?, `email` =?, `tel` = ?,  `desc` = ? WHERE `_id` = ?",
            (str(NAME.get()), str(BIRTHDAY.get()), str(EMAIL.get()), str(TEL.get()), str(DESC.get()),
             int(_id))
        )

        execute_command_db("SELECT * FROM `contacts` ORDER BY `name` ASC")

        clear_fields()

# on select pop up window with all data about selected contact, also you are able to change data
def on_selected(event) -> None:
    global _id, UpdateWindow
    cur_item = tree.focus()
    contents = (tree.item(cur_item))
    selecteditem = contents['values']

    _id = selecteditem[0]

    clear_fields()

    NAME.set(selecteditem[1])
    BIRTHDAY.set(selecteditem[2])
    EMAIL.set(selecteditem[3])
    TEL.set(selecteditem[4])
    DESC.set(selecteditem[5])

    UpdateWindow = Toplevel()
    UpdateWindow.title("Contact Manager")

    width = 400
    height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = ((screen_width / 2) + 450) - (width / 2)
    y = ((screen_height / 2) + 20) - (height / 2)

    UpdateWindow.resizable(0, 0)
    UpdateWindow.geometry("%dx%d+%d+%d" % (width, height, x, y))
    if 'NewWindow' in globals():
        NewWindow.destroy()

    # Frames
    from_title = Frame(UpdateWindow)
    from_title.pack(side=TOP)
    contact_form = Frame(UpdateWindow)
    contact_form.pack(side=TOP, pady=10)

    # Lables
    lbl_title = Label(from_title, text="Update Contact", font=('arial', 16), bg="purple", width=300)
    lbl_title.pack(fill=X)
    lbl_name = Label(contact_form, text="Name", font=('arial', 14), bd=5)
    lbl_name.grid(row=0, sticky=W)
    lbl_birthday = Label(contact_form, text="Birthday", font=('arial', 14), bd=5)
    lbl_birthday.grid(row=1, sticky=W)
    lbl_email = Label(contact_form, text="Email", font=('arial', 14), bd=5)
    lbl_email.grid(row=2, sticky=W)
    lbl_tel = Label(contact_form, text="Tel", font=('arial', 14), bd=5)
    lbl_tel.grid(row=3, sticky=W)
    lbl_desc = Label(contact_form, text="Desc", font=('arial', 14), bd=5)
    lbl_desc.grid(row=4, sticky=W)

    # Entry
    name = Entry(contact_form, textvariable=NAME, font=('arial', 14))
    name.grid(row=0, column=1)
    birthday = Entry(contact_form, textvariable=BIRTHDAY, font=('arial', 14))
    birthday.grid(row=1, column=1)
    email = Entry(contact_form, textvariable=EMAIL, font=('arial', 14))
    email.grid(row=2, column=1)
    tel = Entry(contact_form, textvariable=TEL, font=('arial', 14))
    tel.grid(row=3, column=1)
    desc = Entry(contact_form, textvariable=DESC, font=('arial', 14))
    desc.grid(row=4, column=1)

    # Buttons
    btn_updatecon = Button(contact_form, text="Update", width=50, command=update_contact)
    btn_updatecon.grid(row=6, columnspan=2, pady=10)

# delete specific contact
def delete_contact() -> None:
    if not tree.selection():
        tkMessageBox.showwarning('', 'Please Select Something First!', icon="warning")
    else:
        result = tkMessageBox.askquestion('', 'Are you sure you want to delete this contact?', icon="warning")
        if result == 'yes':
            cur_item = tree.focus()
            contents = (tree.item(cur_item))
            selecteditem = contents['values']
            tree.delete(cur_item)
            conn = sqlite3.connect(FILE_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM `contacts` WHERE `_id` = %d" % selecteditem[0])
            conn.commit()
            cursor.close()
            conn.close()

# function for sorting columns
def treeview_sort_column(tv, col, reverse) -> None:
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # reverse sort next time
    tv.heading(col, command=lambda: \
        treeview_sort_column(tv, col, not reverse)
               )

# delete table and list searched results
def search() -> None:
    tree.delete(*tree.get_children())
    execute_command_db("SELECT * FROM `contacts` WHERE `name` LIKE ? ORDER BY `name` ASC",
                       ["%" + str(SEARCH_Q.get()) + "%"]
                       )


def check_birthday() -> None:
    today = date.today()
    d = today.strftime("%d.%m.%Y")

    conn = sqlite3.connect(FILE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM `contacts` ORDER BY `name` ASC")

    fetch = cursor.fetchall()

    names_list = ""
    if fetch:
        for data in fetch:
            if data[2] == d:
                names_list += data[1] + ", "
    if names_list:
        tkMessageBox.showwarning('', 'Today are ' + names_list + ' birthday')

    cursor.close()
    conn.close()


def add_new_window() -> None:
    global NewWindow

    clear_fields()

    NewWindow = Toplevel()
    NewWindow.title("Contact Manager")
    width = 400
    height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = ((screen_width / 2) - 455) - (width / 2)
    y = ((screen_height / 2) + 20) - (height / 2)
    NewWindow.resizable(0, 0)
    NewWindow.geometry("%dx%d+%d+%d" % (width, height, x, y))
    if 'UpdateWindow' in globals():
        UpdateWindow.destroy()

    # Frames
    FormTitle = Frame(NewWindow)
    FormTitle.pack(side=TOP)
    ContactForm = Frame(NewWindow)
    ContactForm.pack(side=TOP, pady=10)

    # Lables
    lbl_title = Label(FormTitle, text="New Contact", font=('arial', 16), bg="green", width=300)
    lbl_title.pack(fill=X)
    lbl_name = Label(ContactForm, text="Name", font=('arial', 14), bd=5)
    lbl_name.grid(row=0, sticky=W)
    lbl_birthday = Label(ContactForm, text="Birthday", font=('arial', 14), bd=5)
    lbl_birthday.grid(row=1, sticky=W)
    lbl_email = Label(ContactForm, text="Email", font=('arial', 14), bd=5)
    lbl_email.grid(row=2, sticky=W)
    lbl_tel = Label(ContactForm, text="Tel", font=('arial', 14), bd=5)
    lbl_tel.grid(row=3, sticky=W)
    lbl_desc = Label(ContactForm, text="Desc", font=('arial', 14), bd=5)
    lbl_desc.grid(row=4, sticky=W)

    # Entry
    name = Entry(ContactForm, textvariable=NAME, font=('arial', 14))
    name.grid(row=0, column=1)
    birthday = Entry(ContactForm, textvariable=BIRTHDAY, font=('arial', 14))
    birthday.grid(row=1, column=1)
    email = Entry(ContactForm, textvariable=EMAIL, font=('arial', 14))
    email.grid(row=2, column=1)
    tel = Entry(ContactForm, textvariable=TEL, font=('arial', 14))
    tel.grid(row=3, column=1)
    desc = Entry(ContactForm, textvariable=DESC, font=('arial', 14))
    desc.grid(row=4, column=1)

    # Buttons
    btn_addcon = Button(ContactForm, text="Save", width=50, command=create_contact)
    btn_addcon.grid(row=6, columnspan=2, pady=10)


# Frames
Top = Frame(root, width=500, bd=1, relief=SOLID)
Top.pack(side=TOP)
Mid = Frame(root, width=500, bg=BACKGROUND_COLOR, pady=20)
Mid.pack(side=TOP)

TableMargin = Frame(root, width=500)
TableMargin.pack(side=TOP)

search_entry = Entry(Top, textvariable=SEARCH_Q, font=('arial', 14))
search_entry.pack()

# Buttons
btn_search = Button(Top, text="Search", bg="orange", command=search)
btn_search.pack()

btn_add = Button(Mid, text="ADD NEW", bg="green", command=add_new_window)
btn_add.pack()
btn_delete = Button(Mid, text="DELETE", bg="red", command=delete_contact)
btn_delete.pack(side=RIGHT)

# Table
scrollbarx = Scrollbar(TableMargin, orient=HORIZONTAL)
scrollbary = Scrollbar(TableMargin, orient=VERTICAL)
columns = ("ID", "Name", "Birthday", "Email", "Tel", "Desc")
tree = ttk.Treeview(TableMargin, columns=columns,
                    height=400, selectmode="extended", yscrollcommand=scrollbary.set,
                    xscrollcommand=scrollbarx.set
                    )

for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: \
        treeview_sort_column(tree, _col, False)
                 )

scrollbary.config(command=tree.yview)
scrollbary.pack(side=RIGHT, fill=Y)
scrollbarx.config(command=tree.xview)
scrollbarx.pack(side=BOTTOM, fill=X)
tree.heading('ID', text="ID", anchor=W)
tree.heading('Name', text="Name", anchor=W)
tree.heading('Birthday', text="Birthday", anchor=W)
tree.heading('Email', text="Email", anchor=W)
tree.heading('Tel', text="Tel", anchor=W)
tree.heading('Desc', text="Desc", anchor=W)
tree.column('#0', stretch=NO, minwidth=0, width=0)
tree.column('#1', stretch=NO, minwidth=0, width=0)
tree.column('#2', stretch=NO, minwidth=0, width=80)
tree.column('#3', stretch=NO, minwidth=0, width=120)
tree.column('#4', stretch=NO, minwidth=0, width=90)
tree.column('#5', stretch=NO, minwidth=0, width=80)
tree.column('#6', stretch=NO, minwidth=0, width=120)
tree.pack()
tree.bind('<Double-Button-1>', on_selected)

# initialization
if __name__ == '__main__':
    initialize_database()
    check_birthday()
    root.mainloop()
