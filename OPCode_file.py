my_instruction_list = [["NOP", "INC A", "INC @R0", "INC @R1", "INC R0", "INC R1", "INC R2", "INC R3", "CLR A"],
                       ["SETB C", "DEC A", "DEC @R0", "DEC @R1", "DEC R0", "DEC R1", "DEC R2", "DEC R3", "CLR C"],
                       ["ADD A,#data", "ADD A,directAddress", "ADD A,@R0", "ADD A,@R1", "ADD A,R0", "ADD A,R1", "ADD A,R2", "ADD A,R3", "CPL A"],
                       ["ADDC A,#data", "ADDC A,directAddress", "ADDC A,@R0", "ADDC A,@R1", "ADDC A,R0", "ADDC A,R1", "ADDC A,R2", "ADDC A,R3", "CPL C"],
                       ["SUBB A,#data", "SUBB A,directAddress", "SUBB A,@R0", "SUBB A,@R1", "SUBB A,R0", "SUBB A,R1", "SUBB A,R2", "SUBB A,R3", "RL A"],
                       ["ORL A,#data", "ORL A,directAddress", "ORL A,@R0", "ORL A,@R1", "ORL A,R0", "ORL A,R1", "ORL A,R2", "ORL A,R3", "RR A"],
                       ["ANL A,#data", "ANL A,directAddress", "ANL A,@R0", "ANL A,@R1", "ANL A,R0", "ANL A,R1", "ANL A,R2", "ANL A,R3", "RLC A"],
                       ["XRL A,#data", "XRL A,directAddress", "XRL A,@R0", "XRL A,@R1", "XRL A,R0", "XRL A,R1", "XRL A,R2", "XRL A,R3", "RRC A"],
                       ["MOV A,#data", "MOV A,directAddress", "MOV A,@R0", "MOV A,@R1", "MOV A,R0", "MOV A,R1", "MOV A,R2", "MOV A,R3", "MUL AB"],
                       ["MOV R0,#data", "MOV R0,directAddress", "MOV R0,@R0", "MOV R0,@R1", "MOV R0,R0", "MOV R0,R1", "MOV R0,R2", "MOV R0,R3", "DIV AB"],
                       ["MOV R1,#data", "MOV R1,directAddress", "MOV R1,@R0", "MOV R1,@R1", "MOV R1,R0", "MOV R1,R1", "MOV R1,R2", "MOV R1,R3"],
                       ["MOV R2,#data", "MOV R2,directAddress", "MOV R2,@R0", "MOV R2,@R1", "MOV R2,R0", "MOV R2,R1", "MOV R2,R2", "MOV R2,R3"],
                       ["MOV R3,#data", "MOV R3,directAddress", "MOV R3,@R0", "MOV R3,@R1", "MOV R3,R0", "MOV R3,R1", "MOV R3,R2", "MOV R3,R3"],
                       ["MOV A,B", "MOV B,A", "MOV @R0,A", "MOV @R1,A", "MOV R0,A", "MOV R1,A", "MOV R2,A", "MOV R3,A"]
                       ]

def generate_OPCode():
    opcode_list = []
    for i in range(0, len(my_instruction_list)):
        for j in range(0, len(my_instruction_list[i])):
            opcode_list.append((my_instruction_list[i][j], "0x"+str(hex(i))[-1]+str(hex(j))[-1]))
    return opcode_list

