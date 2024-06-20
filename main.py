from web3 import Web3
from web3.middleware import geth_poa_middleware
from accountInfo import abi, contract
from web3.exceptions import TransactionNotFound, ContractLogicError
import re

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=contract, abi=abi)

def registration():
    password = input("Введите пароль: ")
    valid, message = check_password_strength(password)
    if not valid:
        print(message)
        return
    address = w3.geth.personal.new_account(password)
    print(f"Адрес нового аккаунта: {address}")

def auth():
    public_key = input("Введите публичный ключ: ")
    password = input("Введите пароль: ")
    try:
        w3.geth.personal.unlock_account(public_key, password)
        print("Авторизация прошла успешно")
        return public_key
    except Exception as e:
        print("Ошибка авторизации: ", e)
        return None

def check_password_strength(password):
    common_passwords = ['Password12356@', 'password123', 'qwerty123', 'Qwerty12345678#', '1234567891011', '11111111111111111', 'admin12345689', 'letmein', 'admin', 'password', 'qwerty', '123', '1']
    if password in common_passwords:
        return False, "Пароль слишком простой"

    if len(password) < 12:
        return False, "Пароль должен содержать не менее 12 символов"

    if not re.search(r'[A-ZА-Я]', password):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"

    if not re.search(r'[a-zа-я]', password):
        return False, "Пароль должен содержать хотя бы одну строчную букву"

    if not re.search(r'[0-9]', password):
        return False, "Пароль должен содержать хотя бы одну цифру"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Пароль должен содержать хотя бы один специальный символ"

    return True, ""

def create_estate(account):
    name = input("Введите название недвижимости: ")
    address = input("Введите адрес недвижимости: ")
    es_type = get_integer_input("Выберите тип недвижимости (0: Дом, 1: Апартаменты, 2: Квартира, 3: Лофт): ")
    rooms = get_integer_input("Введите количество комнат: ")
    describe = input("Введите описание недвижимости: ")
    try:
        tx_hash = contract.functions.createEstate(name, address, es_type, rooms, describe).transact({
            "from": account
        })
        print(f"Недвижимость успешно создана. Хеш транзации:", tx_hash.hex())
    except Exception as e:
        errors(e)

def create_ad(account):
    estate_id = get_integer_input("Введите ID недвижимости: ")
    price = get_integer_input("Введите цену: ")
    date_time = get_integer_input("Введите дату и время: ")
    try:
        tx_hash = contract.functions.createAd(estate_id, price, date_time).transact({
            "from": account
        })
        print(f"Объявление успешно создано", tx_hash.hex())
    except Exception as e:
        errors(e)

def change_estate_status(account):
    estate_id = get_integer_input("Введите ID недвижимости: ")
    status = get_boolean_input("Введите новый статус (true/false): ")
    try:
        tx_hash = contract.functions.updateEstateStatus(estate_id, status).transact({
            "from": account
        })
        print(f"Статус недвижимости с ID {estate_id} успешно изменен. Хеш транзации:", tx_hash.hex())
    except Exception as e:
        errors(e)

def change_ad_status(account):
    ad_id = get_integer_input("Введите ID объявления: ")
    status_choice = input("Введите новый статус (0: Открыто, 1: Закрыто): ")
    
    status_mapping = {
        "0": 0, 
        "1": 1   
    }
    
    try:
        status = status_mapping[status_choice]
    except KeyError:
        print("Неверный выбор статуса.")
        return
    
    try:
        tx_hash = contract.functions.updateAdStatus(ad_id, status).transact({
            "from": account
        })
        print(f"Статус объявления с ID {ad_id} успешно изменен. Хеш транзации:", tx_hash.hex())
    except Exception as e:
        errors(e)

def purchase_estate(account):
    ad_id = get_integer_input("Введите ID объявления: ")
    try:
        ad_info = contract.functions.getAdById(ad_id).call()
        price = ad_info[2]  
        tx_hash = contract.functions.purchaseEstate(ad_id).transact({
            "from": account,
            "value": price
        })
        print(f"Недвижимость успешно куплена по объявлению с ID {ad_id}. Хеш транзации:", tx_hash.hex())
    except Exception as e:
        errors(e)

def withdraw(account):
    amount = get_integer_input("Введите сумму для вывода: ")
    try:
        tx_hash = contract.functions.withdraw(amount).transact({
            "from": account
        })
        print("Средства успешно выведены. Хеш транзации:", tx_hash.hex())
    except Exception as e:
        errors(e)

def get_available_estates():
    try:
        estate_id = int(input("Введите ID недвижимости: "))
        estate = contract.functions.getEstateById(estate_id).call()
        print("Информация о недвижимости:")
        print(f"Имя: {estate[0]}")
        print(f"Адрес: {estate[1]}")
        print(f"ID недвижимости: {estate[2]}")
        print(f"Тип: {estate[3]}")
        print(f"Количество комнат: {estate[4]}")
        print(f"Описание: {estate[5]}")
        print(f"Владелец: {estate[6]}")
        print(f"Активность: {'Да' if estate[7] else 'Нет'}")
    except Exception as e:
        errors(e)

def get_current_ads():
    try:
        ad_id = int(input("Введите ID объявления: "))
        ad = contract.functions.getAdById(ad_id).call()
        print("Информация об объявлении:")
        print(f"Владелец: {ad[0]}")
        print(f"Покупатель: {ad[1]}")
        print(f"Цена: {ad[2]}")
        print(f"Статус объявления: {ad[3]}")
        print(f"ID недвижимости: {ad[4]}")
        print(f"Дата и время: {ad[5]}")
        print(f"ID объявления: {ad[6]}")
    except Exception as e:
        errors(e)

def get_contract_balance():
    try:
        balance_wei = w3.eth.get_balance(contract.address)
        print("Баланс смарт-контракта: ", balance_wei, "WEI")
    except Exception as e:
        errors(e)

def get_account_balance(account):
    try:
        balance_wei = w3.eth.get_balance(account)
        print("Баланс аккаунта: ", balance_wei, "WEI")
    except Exception as e:
        errors(e)

def errors(error):
    if isinstance(error, ContractLogicError):
        print("Ошибка в логике контракта: ", error)
    elif isinstance(error, TransactionNotFound):
        print("Транзакция не найдена")
    else:
        print("Произошла ошибка: ", error)

def deposit_funds(account):
    amount = get_integer_input("Введите сумму для пополнения: ")
    try:
        tx_hash = contract.functions.addBalance().transact({
            "from": account,
            "value": amount
        })
        print("Средства успешно добавлены на баланс. Хеш транзации:", tx_hash.hex())
    except Exception as e:
        errors(e)

def main():
    try:
        account = ""
        is_auth = False
        while True:
            if not is_auth:
                choice = input("Выбор: \n1. Авторизоваться\n2. Регистрация\n3. Выход\n")
                if choice == "1":
                    account = auth()
                    if account is not None:
                        is_auth = True
                elif choice == "2":
                    registration()
                elif choice == "3":
                    print("До свидания!")
                    break  
                else:
                    print("Введите корректное число")
            else:
                choice = input(
                    "Выбор: \n1. Создать запись о недвижимости\n2. Создать объявление о продаже\n3. Изменить статус недвижимости\n4. Изменить статус объявления\n5. Покупка недвижимости\n6. Вывод средств\n7. Получить информацию о балансе аккаунта\n8. Получить информацию о недвижимости\n9. Получить информацию об объявлениях\n10. Получить информацию о балансе контракта\n11. Пополнить\n12. Выйти")
                if choice == "1":
                    create_estate(account)
                elif choice == "2":
                    create_ad(account)
                elif choice == "3":
                    change_estate_status(account)
                elif choice == "4":
                    change_ad_status(account)
                elif choice == "5":
                    purchase_estate(account)
                elif choice == "6":
                    withdraw(account)
                elif choice == "7":
                    get_account_balance(account)
                elif choice == "8":
                    get_available_estates()
                elif choice == "9":
                    get_current_ads()
                elif choice == "10":
                    get_contract_balance()
                elif choice == "11":
                    deposit_funds(account)
                elif choice == "12":
                    is_auth = False
                else:
                    print("Введите корректное число")
    except Exception as e:
        errors(e)

def get_integer_input(prompt):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Введите целое число.")

def get_boolean_input(prompt):
    while True:
        value = input(prompt).lower()
        if value in ['true', 'false']:
            return value == 'true'
        print("Введите 'true' или 'false'.")

def get_valid_choice(prompt, valid_choices):
    while True:
        choice = input(prompt)
        if choice in valid_choices:
            return choice
        print("Введите корректное значение.")

if __name__ == "__main__":
    main()