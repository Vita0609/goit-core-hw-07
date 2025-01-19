from collections import UserDict
from datetime import datetime, timedelta


# Базовий клас Field
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


# Клас для імені
class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


# Клас для телефонних номерів
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


# Новий клас для дня народження
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")  # Перевірка формату дати
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY.")
        super().__init__(value)


# Клас для запису контакту
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
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now().date()
        birth_date = datetime.strptime(self.birthday.value, "%d.%m.%Y").date()
        next_birthday = birth_date.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones = "; ".join([str(phone) for phone in self.phones])
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones}{birthday}"


# Клас для адресної книги
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value.lower()] = record

    def find(self, name):
        return self.data.get(name.lower(), None)

    def delete(self, name):
        if name.lower() in self.data:
            del self.data[name.lower()]

    def upcoming_birthdays(self, days=7):
        today = datetime.now().date()
        result = []
        for record in self.data.values():
            if record.birthday:
                birth_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                next_birthday = birth_date.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                delta = (next_birthday - today).days

                # Урахування перенесення з вихідних на понеділок
                if delta <= days:
                    if next_birthday.weekday() in [5, 6]:  # Субота чи неділя
                        next_birthday += timedelta(days=(7 - next_birthday.weekday()))
                    if (next_birthday - today).days <= days:
                        result.append(record)
        return result

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


# Декоратор для обробки помилок
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command. Not enough arguments."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return inner


# Основний функціонал бота
@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name) or Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return f"Contact {name} added."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found.")
    record.edit_phone(old_phone, new_phone)
    return f"Phone number for {name} updated."


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found.")
    record.add_birthday(birthday)
    return f"Birthday for {name} added."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise ValueError("Contact not found.")
    phones = "; ".join([str(phone) for phone in record.phones])
    return f"Phone(s) for {name}: {phones}"


@input_error
def show_all(book):
    return str(book) if book.data else "No contacts found."


@input_error
def birthdays(book):
    upcoming = book.upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(str(record) for record in upcoming)


# Основна функція
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        command, *args = user_input.split()

        if command.lower() in ["close", "exit"]:
            print("Good bye!")
            break
        elif command.lower() == "add":
            print(add_contact(args, book))
        elif command.lower() == "change":
            print(change_contact(args, book))
        elif command.lower() == "birthday":
            print(add_birthday(args, book))
        elif command.lower() == "phone":
            print(show_phone(args, book))
        elif command.lower() == "all":
            print(show_all(book))
        elif command.lower() == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
