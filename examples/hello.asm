BEGIN:
    LOAD [MSG]+
    ST [1]; OUT MEM
    JNZ BEGIN
    HALT

MSG:
    WORD 72
    WORD 101
    WORD 108
    WORD 108
    WORD 111
END:
    HALT