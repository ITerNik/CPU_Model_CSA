VEC 0 INPUT_INT

PTR:
    WORD 0
MSG:
    WORD 0

BEGIN:
    LOAD #MSG
    ST PTR

INPUT:
    JNZ INPUT

    CALL PRINT
END:
    HALT

INPUT_INT:
    LOAD 1 ; IN MEM
    ST [PTR]+
    IRET

PRINT:
    LOAD #MSG
    ST PTR
LOOP:
    LOAD [PTR]+

    JZ END
    ST 1 : OUT MEM
    JUMP LOOP
    RET
