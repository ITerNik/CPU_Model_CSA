VEC 0 INPUT_INT

BEGIN:
  DI
  LOAD #MSG1
  ST PTR
  CALL PRINT
  LOAD #NAME
  ST PTR
  EI
  CALL INPUT_NAME
  DI
  LOAD #MSG2
  ST PTR
  CALL PRINT
  LOAD #NAME
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

INPUT_NAME:
  JNZ INPUT_NAME
  RET

INPUT_INT:
  LOAD 0
  ST [PTR]+
  IRET

MSG1:
    WORD 87 ; 'W'
    WORD 104 ; 'h'
    WORD 97 ; 'a'
    WORD 116 ; 't'
    WORD 39 ; '\''
    WORD 115 ; 's'
    WORD 32 ; ' '
    WORD 121 ; 'y'
    WORD 111 ; 'o'
    WORD 117 ; 'u'
    WORD 114 ; 'r'
    WORD 32 ; ' '
    WORD 110 ; 'n'
    WORD 97 ; 'a'
    WORD 109 ; 'm'
    WORD 101 ; 'e'
    WORD 44 ; ','
    WORD 32 ; ' '
    WORD 116 ; 't'
    WORD 114 ; 'r'
    WORD 97 ; 'a'
    WORD 118 ; 'v'
    WORD 101 ; 'e'
    WORD 108 ; 'l'
    WORD 108 ; 'l'
    WORD 101 ; 'e'
    WORD 114 ; 'r'
    WORD 63 ; '?'
    WORD 32 ; ' '
    WORD 0

MSG2:
    WORD 72 ; 'H'
    WORD 101 ; 'e'
    WORD 108 ; 'l'
    WORD 108 ; 'l'
    WORD 111; 'o'
    WORD 44 ; ','
    WORD 32 ; ' '
    WORD 0

PTR:
    WORD 0
NAME:
    WORD 0
