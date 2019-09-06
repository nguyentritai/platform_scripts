CFLAGS = -std=c99

PROGRAM = a64_sys_reg 
SOURCE  = Source.c
     
all: $(PROGRAM) OBJ
     
$(PROGRAM): $(SOURCE) ; $(CC) $(CFLAGS) -o $(PROGRAM) $(SOURCE)

OBJ: ;objdump -DS a64_sys_reg > obj
 
clean: ; rm -f $(PROGRAM)
