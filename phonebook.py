from datetime import datetime, timedelta
import re

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY.")
        super().__init__(value)

class Record:
    def __init__(self, name: Name):
        self.name = name
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def remove_phone(self, phone: Phone):
        self.phones = [p for p in self.phones if p.value != phone.value]

    def update_phone(self, old_phone: Phone, new_phone: Phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_birthday(self, birthday: Birthday):
        self.birthday = birthday

class AddressBook:
    def __init__(self):
        self.records = {}

    def add_record(self, record: Record):
        self.records[record.name.value] = record

    def find_record(self, name):
        return self.records.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.now()
        upcoming_birthdays = []
        
        for record in self.records.values():
            if record.birthday:
                bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                bday_this_year = bday_date.replace(year=today.year)

                if 0 <= (bday_this_year - today).days <= 7:
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": bday_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"Error: {e}"
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find_record(name)
    if not record:
        record = Record(Name(name))
        book.add_record(record)
    record.add_phone(Phone(phone))
    return f"Contact added/updated for {name}."

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find_record(name)
    if not record:
        return "Contact not found."
    record.update_phone(Phone(old_phone), Phone(new_phone))
    return f"Phone number updated for {name}."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find_record(name)
    if not record:
        return "Contact not found."
    record.add_birthday(Birthday(birthday))
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find_record(name)
    if not record or not record.birthday:
        return "Birthday not found for this contact."
    return f"{name}'s birthday is {record.birthday.value}."

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join([f"{item['name']}: {item['birthday']}" for item in upcoming])

@input_error
def show_all(book: AddressBook):
    if not book.records:
        return "No contacts found."
    result = []
    for record in book.records.values():
        phones = "; ".join([phone.value for phone in record.phones])
        birthday = record.birthday.value if record.birthday else "No birthday"
        result.append(f"Contact name: {record.name.value}, phones: {phones}, birthday: {birthday}")
    return "\n".join(result)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    commands = {
        "add": add_contact,
        "change": change_contact,
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": birthdays,
        "all": show_all
    }

    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, *args = user_input.split()

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        handler = commands.get(command)
        if handler:
            print(handler(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
