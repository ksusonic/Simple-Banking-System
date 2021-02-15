import random
import sqlite3


class DataBase:
    def __init__(self):
        self.ids = 0
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()

    def create_table(self) -> None:
        self.cur.execute('''CREATE TABLE IF NOT EXISTS card (
                                id INTEGER,
                                number TEXT,
                                pin TEXT,
                                balance INTEGER DEFAULT 0);'''
                         )
        self.conn.commit()

    def update_cards_amount(self) -> int:
        self.cur.execute("SELECT * FROM card")
        self.ids = len(self.cur.fetchall())
        return self.ids

    def add_data(self, num, pin, balance=0) -> None:
        self.update_cards_amount()
        self.cur.execute(f'''
                INSERT
                INTO card (id, number, pin, balance)
                VALUES ({self.ids}, {num}, {pin}, {balance});
                ''')
        self.conn.commit()

    def get_card(self, number: str) -> tuple:
        self.cur.execute(f'''
                SELECT * FROM card WHERE number = {number}
        ''')
        return self.cur.fetchone()

    def change_balance(self, amount: int, card: str) -> None:
        self.cur.execute(f'''
                UPDATE card 
                SET balance = balance + {amount}
                WHERE number = {card};
        ''')
        self.conn.commit()

    def transfer(self, card_from: str, card_to: str) -> None:
        if card_from == card_to:
            print("You can't transfer money to the same account!\n")
            return
        card_to_query = self.get_card(card_to)
        if card_to != card_to[:-1] + CreditCard.luhn_checker(card_to[:-1]):
            print("Probably you made a mistake in the card number. Please try again!\n")
        elif not card_to_query:
            print("Such a card does not exist.\n")
        else:
            amount = int(input("Enter how much money you want to transfer:"))
            while amount <= 0:
                print("Incorrect amount. Try again")
                amount = int(input("Enter how much money you want to transfer:"))
            if self.get_card(card_from)[-1] < amount:
                print("Not enough money!\n")
            else:
                self.cur.execute(f'''
                    UPDATE card
                    SET balance = balance - {amount}
                    WHERE number = {card_from};
                ''')
                self.conn.commit()
                self.cur.execute(f'''
                    UPDATE card
                    SET balance = balance + {amount}
                    WHERE number = {card_to};
                ''')
                self.conn.commit()
                print("Success!\n")

    def delete_account(self, number) -> None:
        self.cur.execute(f'''
                    DELETE FROM card
                    WHERE number = {number};
        ''')
        self.conn.commit()

    def __del__(self):
        self.conn.close()


class CreditCard:
    def __init__(self):
        self.num = f"{random.randint(400000000000000, 400000999999999):15}"
        self.num += self.luhn_checker(number=self.num)
        self.pin = f"{random.randint(0000, 9999):04}"
        self.balance = 0

    @staticmethod
    def luhn_checker(number: str) -> str:
        numbers = [int(x) for x in number]
        for i in range(len(numbers)):
            if i % 2 == 0:
                numbers[i] *= 2
            if numbers[i] > 9:
                numbers[i] -= 9
        s = sum(numbers)
        i = 0
        while (s + i) % 10 != 0:
            i += 1
        return str(i)

    def __repr__(self):
        return self.num


def choose_action() -> str:
    res = input("1. Create an account\n"
                "2. Log into account\n"
                "0. Exit\n")
    print()
    return res


def create_account():
    credit_card = CreditCard()
    database.add_data(credit_card.num, credit_card.pin)
    print("Your card has been created\n"
          "Your card number:\n"
          f"{credit_card.num}\n"
          "Your card PIN:\n"
          f"{credit_card.pin}\n")


def log_into_account():
    card_number = input("Enter your card number:")
    pin = input("Enter your PIN:")
    query = database.get_card(card_number)
    if not query or query[2] != pin:
        print("Wrong card number or PIN!")
    else:
        print("You have successfully logged in!")
        while True:
            login_choice = int(input("1. Balance\n"
                                     "2. Add income\n"
                                     "3. Do transfer\n"
                                     "4. Close account\n"
                                     "5. Log out\n"
                                     "0. Exit\n"))
            if login_choice == 1:
                print("Balance:", query[3])
            elif login_choice == 2:
                income = int(input("Enter income:"))
                database.change_balance(income, card_number)
                query = database.get_card(card_number)
                print("Income was added!\n")
            elif login_choice == 3:
                print("Transfer")
                card_to = input("Enter card number:")
                database.transfer(card_number, card_to)
            elif login_choice == 4:
                database.delete_account(card_number)
                print("The account has been closed!\n")
                break
            elif login_choice == 5:
                print("You have successfully logged out!")
                break
            elif login_choice == 0:
                exit()


database = DataBase()
database.create_table()

while True:
    action = choose_action()
    if action == "1":
        create_account()
    elif action == "2":
        log_into_account()
    elif action == "0":
        print("Bye!")
        exit()
