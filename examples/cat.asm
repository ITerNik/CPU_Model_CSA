VEC 0 INPUT_INT

PTR:
    WORD 0
MSG:
    WORD 0

BEGIN:
  DI
  LOAD #MSG
  ST PTR
  EI
  CALL INPUT
  DI
  LOAD #MSG
  ST PTR
  CALL PRINT
  HALT

PRINT:
LOOP:
    LOAD [PTR]+

    JZ END
    ST 1
    JUMP LOOP
END:
    RET

INPUT:
  JNZ INPUT
  RET

INPUT_INT:
  LOAD 0
  ST [PTR]+
  IRET
