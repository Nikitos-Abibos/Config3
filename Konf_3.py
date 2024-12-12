import sys
import re
import json

class ConfigParser:
    def __init__(self):
        self.constants = {}
        self.data = {}

    def parse(self, input_text):
        lines = input_text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Пропуск пустых строк
            if not line:
                i += 1
                continue

            # Пропуск однострочных комментариев
            if line.startswith('#'):
                i += 1
                continue

            # Пропуск многострочных комментариев
            if line.startswith('<#'):
                while not line.endswith('#>'):
                    i += 1
                    line = lines[i].strip()
                i += 1
                continue
            
            # Обработка объявления константы
            if line.startswith('global '):
                self.handle_global_declaration(line)
            else:
                # Обработка значений, массивов и словарей
                self.handle_value(line)

            i += 1

    def handle_global_declaration(self, line):
        match = re.match(r'global ([a-zA-Z][_a-zA-Z0-9]*) = (.+)', line)
        if match:
            name = match.group(1)
            value = self.evaluate_value(match.group(2))
            if name not in self.constants:
                self.constants[name] = value
                print(f"Defined constant: {name} = {value}")  # Отладочное сообщение
            else:
                print(f"Constant {name} already defined")
        else:
            print(f"Syntax error in line: {line}")

    def handle_value(self, line):
        # Проверка на присваивание
        if '=' in line:
            self.handle_assignment(line)
        elif line.startswith('$[') and line.endswith(']'):
            self.handle_dictionary(line)
        elif line.startswith('(') and line.endswith(')'):
            self.handle_array(line)
        elif re.match(r'^[a-zA-Z][_a-zA-Z0-9]*$', line):
            self.handle_name(line)
        elif re.match(r'^\.[a-zA-Z][_a-zA-Z0-9]*\.$', line):
            self.handle_constant(line)
        else:
            print(f"Syntax error in line: {line}")

    def handle_assignment(self, line):
        match = re.match(r'([a-zA-Z][_a-zA-Z0-9]*) = (.+)', line)
        if match:
            name = match.group(1)
            value = self.evaluate_value(match.group(2))
            if value is not None:
                self.data[name] = value
                print(f"Assigned: {name} = {value}")  # Отладочное сообщение
            else:
                print(f"Cannot assign undefined value to {name}")
        else:
            print(f"Syntax error in assignment: {line}")

    def handle_dictionary(self, line):
        content = line[2:-1].strip()
        items = [item.strip() for item in content.split(',')]
        dictionary = {}
        for item in items:
            match = re.match(r'([a-zA-Z][_a-zA-Z0-9]*): (.+)', item)
            if match:
                key = match.group(1)
                value = self.evaluate_value(match.group(2))
                dictionary[key] = value
                print(f"Added to dictionary: {key} = {value}")  # Отладочное сообщение
            else:
                print(f"Syntax error in dictionary entry: {item}")
                return
        self.data.update(dictionary)

    def handle_array(self, line):
        content = line[1:-1].strip()
        items = [self.evaluate_value(item.strip()) for item in content.split(',')]
        self.data['array'] = items  # Можно использовать уникальное имя для массива
        print(f"Added array: {items}")  # Отладочное сообщение

    def handle_name(self, line):
        match = re.match(r'^([a-zA-Z][_a-zA-Z0-9]*)$', line)
        if match:
            name = match.group(1)
            value = self.constants.get(name, None)
            if value is not None:
                self.data[name] = value
                print(f"Added name: {name} = {value}")  # Отладочное сообщение
            else:
                print(f"Undefined constant: {name}")
        else:
            print(f"Syntax error in line: {line}")

    def handle_constant(self, line):
        match = re.match(r'^\.(\w+)\.$', line)
        if match:
            name = match.group(1)
            value = self.constants.get(name, None)
            if value is not None:
                self.data[name] = value
                print(f"Added constant: {name} = {value}")  # Отладочное сообщение
            else:
                print(f"Undefined constant: {name}")
        else:
            print(f"Syntax error in line: {line}")

    def evaluate_value(self, value):
        # Проверка на константы
        const_match = re.match(r'\.([a-zA-Z][_a-zA-Z0-9]*)\.', value)
        if const_match:
            name = const_match.group(1)
            if name in self.constants:
                return self.constants[name]
            else:
                print(f"Undefined constant: {name}")
                return None

        # Проверка на переменные
        if re.match(r'^[a-zA-Z][_a-zA-Z0-9]*$', value):
            if value in self.data:
                return self.data[value]
            elif value in self.constants:
                return self.constants[value]
            else:
                print(f"Undefined variable: {value}")
                return None

        # Проверка на числа
        if re.match(r'^\d+(\.\d+)?$', value):  # Обработка целых и дробных чисел
            return float(value) if '.' in value else int(value)

        # Если значение - это строка, возвращаем ее как строку
        if re.match(r'^".*"$', value):
            return value.strip('"')

        # Если значение - это массив или словарь, возвращаем его
        return value

    def to_json(self):
        return json.dumps(self.data, indent=4, ensure_ascii=False)

    def get_names(self):
        return list(self.constants.keys()) + list(self.data.keys())

def main():
    parser = ConfigParser()
    # Чтение входного текста с указанием кодировки
    input_text = sys.stdin.read()
    parser.parse(input_text)
    output_json = parser.to_json()
    print(output_json)

    # Вывод имен
    names = parser.get_names()
    print("Defined names:", names)

if __name__ == "__main__":
    main()






