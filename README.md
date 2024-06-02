# Эксперимент. Транслятор и модель
- Терехин Никита Денисович P3208
- ```asm | acc | harv | hw | instr | struct | trap -> stream | mem | cstr | prob2 | spi```
- Базовый вариант
## Язык программирования
### Синтаксис
Описание синтаксиса с использованием расширенной ФБН
- ```?``` - встречается 0 или 1 раз
- ```*``` - встречается 0 или более раз
- ```+``` - встречается 1 или более раз
```
<program> ::= <line> | <line> <program>

<no_arg_op> ::= "HALT"
                | "EI"
                | "DI"
                | "RET"
                | "IRET"
                | "NOP"

<arg_op> ::= "LOAD"
            | "ST"
            | "ADD"
            | "CMP"
            | "JUMP"
            | "JZ"
            | "JNZ"
            | "JEV"
            | "JBE"
            | "CALL"

<line_without_comment> ::= <label> | <space> <instruction>

<line> ::= <line_without_comment> <space> <comment>* "\n"+

<comment> ::= ";" (<label_name> | <space>)*

<space> ::= ("\t" | " " | "\r")*

<word> ::= "WORD " <number>

<vec> ::=  <number> (<label_name> | <number>)

<instruction> ::= <no_arg_op> | <arg_op> " " <adress>

<inner_adress> ::= <label_name> | <number>

<indirect_adress> ::= "[" <inner_adress> "]"

<auto_adress> ::= ("+" | "-") <indirect_adress> | <indirect_adress> ("+" | "-")

<absolute_adress> ::= "#" <inner_adress>

<adress> ::= <indirect_adress> | <inner_adress> | <absolute_adress> | <auto_adress>

<label> ::= <label_name> ":"

<number> ::= [1-9] [0-9]* | "0x" ([0-9] | [A-F])+

<label_name> ::= ([a-z] | [A-Z] | "_") ([a-z] | [A-Z] | "_" | [0-9])*

```

### Семантика
- Язык предполагает последовательное исполнение
- Глобальная область видимости меток

На этапе трансляции метки заменяются численными адресами

### Литералы
- Аргументы команд - численные литералы или метки
- Поддерживаются целочисленные десятичные, а также шестнадцатеричные числа с указанием префикса ```0x```

## Организация памяти
Память организвана согласно Гарвардской модели: инструкций и данные разделены
1. Память команд. Машинное слово - не определено. Реализовано списком классов, описывающих инструкции
2. Память данных. Машинное слово - 32 бита, знаковое. Реализовано целочисленным списком
3. Стек вызовов. Отдельная область памяти для реализации прерываний и подпрограм. Машинное слово - 32 бита, знаковое

Векторы прерывания хранятся в первых `n` ячейках памяти команд

Ввод / вывод мапится на первые ячейки памяти данных

## Система команд
### Инструкции
```LOAD ADDR``` - загрузить данные из ячейки памяти в аккуммулятор

```ST ADDR``` - выгрузить данные из аккуммулятоа в ячейку памяти

```ADD ADDR``` - сложить значение ячейки по адресу с текущим в аккумуляторе

```CMP ADDR``` - выставить флаги после сравнения с числом по адресу из памяти

```JUMP ADDR``` - безусловный переход по адресу

```JZ ADDR``` - переход, если установлен флаг нуля

```JNZ ADDR``` - переход, если флаг нуля не установлен

```JEV ADDR``` - переход, если число в аккумуляторе четное

```JBE ADDR``` - переход, если результат сравнения больше либо равен

```CALL ADDR``` - вызвать подпрограмму по адресу в памяти команд

```HALT``` - остановить процессор

```EI / DI``` - разрешить / запретить прерывания от внешних устройств

```RET``` - вернуться из подпрограммы

```IRET``` - вернуться из программы обработчика и сбросить сигнал прерывания

```NOP``` - пустая команда
### Типы адрессации

<table>
  <thead align="center">
    <tr>
      <td>Тип адрессации</td>
      <td>Синтаксис</td>
      <td>Примеры</td>
    </tr>
  </thead>
  <tbody align="center">
    <tr>
      <td>Абсолютная</td>
      <td>ADDR</td>
      <td><pre>ST 0x01<br>LOAD LABEL</pre></td>
    </tr>
    <tr>
      <td>Прямая загрузка</td>
      <td>#ADDR</td>
      <td><pre>ADD #0x4<br>LOAD #LABEL</pre></td>
    </tr>
    <tr>
      <td>Косвенная</td>
      <td>[ADDR]</td>
      <td><pre>CMP [LABEL]<br>LOAD [0x93] </pre></td>
    </tr>
    <tr>
      <td>Пост-инкремент</td>
      <td>[ADDR]+</td>
      <td><pre>ADD [LABEL]+<br>LOAD [0x93]+ </pre></td>
    </tr>
    <tr>
      <td>Пост-декремент</td>
      <td>[ADDR]-</td>
      <td><pre>ST [LABEL]-<br>LOAD [0x93]- </pre></td>
    </tr>
  </tbody>
</table>

### Директивы
```vec n address``` - инициализирует n-ый вектор прерывания

```word number``` - кладет данные в ячейку памяти в соответствии с линейным порядком

### Кодирование инструкций

Машинный код сериализуется в список JSON
Один элемент списка - одна инструкция
```
{
    "index": 13,
    "opcode": "JBE",
    "arg": "22",
    "addressing": 0
}
```
- `index` - адрес в памяти команд

- `opcode` - строка с кодом операции

- `arg` - аргумент

- `addressing` - тип адрессации

## Транслятор
Интерфейс командной строки: translator.py <input_file> <target_file>

Реализовано в модуле: [translator](translator.py)

Этапы трансляции:

- Проверка корректности программы (пересечение меток, закрывающие скобки)
- Трансформирование текста в машинный код
- Подстановка численных значений вместо меток

## Модель процессора

Интерфейс командной строки: `machine.py <machine_code_file> <input_file>`

Реализовано в модуле: [machine](machine.py)
### ControlUnit
<p align="center">
    <img src="./assets/ControlUnit.svg" alt="control-unit"/>
</p>

Реализован в классе ControlUnit

- Hardwired
- Метод `decode_and_execute_instruction` моделирует выполнение полного цикла инструкции

Сигналы:
- `signal_latch_pc` - сигнал для обновления счётчика команд. Может быть обновлен из стека, адресом вектора прерывания, адресом аргумента текущей команды или увеличен на единицу в зависимости от селектора
- `signal_latch_sp` - защелкивает измененное на единицу значение указателя стека
- `signal_curr_instr` - защелкивает в регистр команд текущую инструкцию


### DataPath
<p align="center">
    <img src="./assets/DataPath.svg" alt="data-path"/>
</p>

Сигналы:
- `signal_latch_ar` - защёлкнуть выбранное значение в AR
- `signal_latch_acc` - защёлкнуть в аккумулятор выход АЛУ
- `signal_data_out` - записать значение из DR в память
- `signal_data_in` - получить значение из памяти в DR

Ввод / вывод данных эквивалентен чтению / записи в память по выделенным адрессам

Флаги:
- `zero` - отражает наличие нулевого значения
- `negative` - отражает знак операции
- `be` - отражает результат сравнения
- `even` - отражает четность числа в аккумуляторе

Выходные данные АЛУ регулируются набором опций для левого и правого входа

Особенности работы модели:

- Для прерываний внешнее устройство выставляет на шину запрос прерывания и вектор, который дешифруется и подается на мультиплексор PC 
- Шаг моделирования соответствует одной инструкции с выводом состояния в журнал
- Количество инструкций для моделирования лимитировано
- Остановка моделирования осуществляется при:
    - превышении лимита количества выполняемых инструкций
  - исключении `EOFError` - если нет данных для чтения из порта ввода
  - исключении `StopIteration` - если выполнена инструкция `HALT`

## Тестирование
Пример проверки исходного кода:
```
>> poetry run pytest . -v                        
=============================================================== test session starts ===============================================================
platform win32 -- Python 3.11.5, pytest-7.4.4, pluggy-1.5.0 -- C:\Users\terni\AppData\Local\pypoetry\Cache\virtualenvs\cpu_model-971P-bPT-py3.11\Scr
ipts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\terni\PycharmProjects\CPU_Model_CSA
configfile: pyproject.toml
plugins: golden-0.2.2
collected 4 items

golden_test.py::test_translator_and_machine[golden/cat.yml] PASSED                                                                           [ 25%]
golden_test.py::test_translator_and_machine[golden/even-fibonacci.yml] PASSED                                                                [ 50%]
golden_test.py::test_translator_and_machine[golden/hello-username.yml] PASSED                                                                [ 75%]
golden_test.py::test_translator_and_machine[golden/hello.yml] PASSED                                                                         [100%]

================================================================ 4 passed in 0.24s ================================================================ 

>> poetry run ruff check .
>> poetry run ruff format .
4 files left unchanged

```
## Результаты
```
|          ФИО             |      алг       | code интср. | инстр. | такт |                                     вариант                                        |
| Терехин Никита Денисович | hello_world    | 10          | 25     | 93   | asm | acc | harv | hw | instr | struct | trap -> stream | mem | cstr | prob2 | spi |
| Терехин Никита Денисович | hello_username | 28          | 222    | 860  | asm | acc | harv | hw | instr | struct | trap -> stream | mem | cstr | prob2 | spi |
| Терехин Никита Денисович | cat            | 22          | 66     | 272  | asm | acc | harv | hw | instr | struct | trap -> stream | mem | cstr | prob2 | spi |
| Терехин Никита Денисович | prob2          | 25          | 228    | 748  | asm | acc | harv | hw | instr | struct | trap -> stream | mem | cstr | prob2 | spi |
```
