import datetime
from collections import UserDict

# Клас для зберігання значень полів
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


# Клас для дня народження
class Birthday(Field):
    def __init__(self, value):
        try:
            # Перевірка коректності формату дати
            self.value = datetime.datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


# Клас для запису контакту
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone_to_remove = None
        for phone in self.phones:
            if phone.value == phone_number:
                phone_to_remove = phone
                break
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError(f"Phone number {phone_number} not found.")

    def edit_phone(self, old_phone, new_phone):
        if old_phone not in [phone.value for phone in self.phones]:
            raise ValueError(f"Phone number {old_phone} not found.")
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def add_birthday(self, birthday_date):
        self.birthday = Birthday(birthday_date)

    def __str__(self):
        phone_numbers = "; ".join([phone.value for phone in self.phones])
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phone_numbers}{birthday_str}"


# Клас для адресної книги
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.date.today()
        for record in self.data.values():
            if record.birthday:
                delta = (record.birthday.value - today).days
                if 0 <= delta <= 7:
                    # Якщо день народження у межах 7 днів
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": record.birthday.value
                    })
        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())


# Декоратор для обробки помилок вводу
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {e}"
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Missing argument."
    return wrapper


# Команди для бота

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise ValueError(f"Contact {name} does not exist.")
    record.add_birthday(birthday)
    return f"Birthday for {name} added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        raise ValueError(f"No birthday information found for {name}.")
    return f"{name}'s birthday is {record.birthday.value}"


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join([f"{entry['name']} - {entry['birthday']}" for entry in upcoming])


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone number for {name} updated."


@input_error
def phone_contact(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    return f"{name}: {', '.join([phone.value for phone in record.phones])}"


# Парсинг команд
def parse_input(user_input):
    return user_input.split()


# Головна функція для взаємодії з ботом
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(phone_contact(args, book))

        elif command == "all":
            print(book)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
