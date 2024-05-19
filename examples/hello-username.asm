V0:
    WORD INPUT_INT

BEGIN:
  LOAD #MSG1
  ST PTR
  CALL PRINT
  LOAD #NAME
  ST PTR
  CALL INPUT_NAME
  LOAD #NAME
  ST PTR
  CALL PRINT
  HALT

PRINT:
LOOP:
    LOAD [PTR]+

    JZ END
    ST [1] ; OUT MEM
    JUMP LOOP
END:
    RET

INPUT_NAME:
  JNZ INPUT_NAME

  CALL PRINT
  RET

INPUT_INT:
  DI
  LOAD [2] ; IN MEM
  ST [PTR]+
  EI
  IRET

MSG1:
    WORD “What’s your name, traveler?” 0
MSG2:
    WORD “Hello, ” 0
PTR:
    WORD 0
NAME:
    WORD 0
