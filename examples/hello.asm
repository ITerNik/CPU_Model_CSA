BEGIN:
    LOAD #MSG
    ST PTR
LOOP:
    LOAD [PTR]+
    ST 0x001; OUT MEM
    JNZ LOOP
    HALT

MSG:
    WORD 72
    WORD 101
    WORD 108
    WORD 108
    WORD 111
PTR:
    WORD 0