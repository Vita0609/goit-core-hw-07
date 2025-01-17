from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value): 
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")  # Validate format
        except ValueError:
            raise ValueError("Birthday must be in format DD.MM.YYYY.")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError(f"Phone number {phone_number} not found.")

    def edit_phone(self, old_phone, new_phone):
        old_phone_obj = self.find_phone(old_phone)
        if not old_phone_obj:
            raise ValueError(f"Phone number {old_phone} not found.")

        try:
            new_phone_obj = Phone(new_phone)  # Validate new phone
        except ValueError as e:
            raise ValueError(f"Cannot replace with invalid phone: {e}")

        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def set_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        birthday_date = datetime.strptime(self.birthday.value, "%d.%m.%Y").replace(year=today.year)
        if birthday_date < today:
            birthday_date = birthday_date.replace(year=today.year + 1)
        return (birthday_date - today).days

    def __str__(self):
        phone_numbers = "; ".join([phone.value for phone in self.phones])
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phone_numbers}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def upcoming_birthdays(self, days=7):
        today = datetime.now()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").replace(year=today.year)
                if today <= birthday_date < today + timedelta(days=days):
                    upcoming.append(record)
        return upcoming

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

# Парсер вводу

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

# Команди

def add_contact(args, contacts):
    if len(args) < 2:
        return "Invalid command. Please provide name and at least one phone number."
    name, phone = args[0], args[1]
    record = contacts.find(name) or Record(name)
    try:
        record.add_phone(phone)
    except ValueError as e:
        return str(e)
    contacts.add_record(record)
    return "Contact added."

def change_contact(args, contacts):
    if len(args) != 3:
        return "Invalid command. Please provide name, old phone, and new phone."
    name, old_phone, new_phone = args
    record = contacts.find(name)
    if not record:
        return "Contact not found."
    try:
        record.edit_phone(old_phone, new_phone)
    except ValueError as e:
        return str(e)
    return "Contact updated."

def show_phone(args, contacts):
    if len(args) != 1:
        return "Invalid command. Please provide a name."
    name = args[0]
    record = contacts.find(name)
    if not record:
        return "Contact not found."
    return str(record)

def show_all(contacts):
    if not contacts.data:
        return "No contacts found."
    return str(contacts)

def birthdays(args, contacts):
    try:
        days = int(args[0]) if args else 7
    except ValueError:
        return "Invalid number of days."
    upcoming = contacts.upcoming_birthdays(days)
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(str(record) for record in upcoming)

def main():
    contacts = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        elif command == "birthdays":
            print(birthdays(args, contacts))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
