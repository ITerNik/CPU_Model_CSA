# Эксперимент. Транслятор и модель
- Терехин Никита Денисович P3208
- ```asm | acc | harv | hw | instr | struct | trap -> stream | mem | cstr | prob2 | spi```
- Базовый вариант
## Язык программирования
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

<arg_op> ::= "LOAD"
            | "ST"
            | "ADD"
            | "CMP"
            | "JUMP"
            | "JZ"
            | "JNZ"
            | "CALL"

<line_without_comment> ::= <label> | ("\t" | " ")* <instruction>

<line> ::= <line_without_comment> ("\t" | " ")* <comment>* "\n"+

<comment> ::= ";" (<label_name> | " ")*

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