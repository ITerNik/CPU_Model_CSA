SUM:
    WORD 2
FIRST:
    WORD 1
SECOND:
    WORD 2
INF:
    WORD 4000000

BEGIN:
DI
LOOP_FIRST:
  LOAD FIRST
  ADD SECOND
  ST FIRST
  CMP INF
  JBE END
  JEV EVEN_FIRST
LOOP_SECOND:
  LOAD SECOND
  ADD FIRST
  ST SECOND
  CMP INF
  JBE END
  JEV EVEN_SECOND
  JUMP LOOP_FIRST
EVEN_FIRST:
  ADD SUM
  ST SUM
  JUMP LOOP_SECOND
EVEN_SECOND:
  ADD SUM
  ST SUM
  JUMP LOOP_FIRST
END:
  LOAD SUM
  ST 1
  HALT
