from OPCode_file import generate_OPCode
import time
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
from flask import Flask, redirect, url_for, request, render_template, session, send_file
app = Flask(__name__)
app.secret_key = 'cisco'


#Stack is used to store the value of PC and 8 registers (R0-3), A, B and C when an ISR is called
class Stack:
    PC = 0
    Reg = [0]*4
    A = 0
    B = 0
    C = 0

#Used by ISR    
def Push(current_pc, current_reg, current_A, current_B, current_C):
    Stack.PC = current_pc
    Stack.Reg = current_reg
    Stack.A = current_A
    Stack.B = current_B
    Stack.C = current_C

class Global_variables:
    OPCode_list = []
    instruction_list = []
    input_instruction_list = []
    Reg_0to3 = [0]*4
    A = 0
    B = 0
    C = 0
    memory = [0]*256
    PC = 0
    IR = ""
    filename = ""

def initialise_global_var():
    Global_variables.instruction_list = []
    Global_variables.input_instruction_list = []
    Global_variables.Reg_0to3 = [0]*4
    Global_variables.A = 0
    Global_variables.B = 0
    Global_variables.C = 0
    Global_variables.memory = [0]*256
    Global_variables.PC = 0
    Global_variables.IR = ""

def ISR():
    #print "Entering ISR"
    Push(Global_variables.PC, Global_variables.Reg_0to3, Global_variables.A, Global_variables.B, Global_variables.C)
    ISR_instruction_list = [ReturnOPCode("CPL A")]
    Global_variables.PC = 0   
    Global_variables.IR = ISR_instruction_list[Global_variables.PC]
    Global_variables.PC += 1
    execute_instruction()
    return
    
def ReturnOPCode(Instruction):
    #Register and Indirect addressing modes
    for opcode in Global_variables.OPCode_list:
        if opcode[0] == Instruction:
            return opcode[1]

    #Immediate and Direct addressing modes
    instruction_split = Instruction.strip().split(",")
    for opcode in Global_variables.OPCode_list:
        #print opcode[0].split(",")[0] , instruction_split[0]
        if opcode[0].split(",")[0] == instruction_split[0]:
            opcode_to_return = opcode[1]
            if instruction_split[1].startswith("#") == opcode[0].split(",")[1].startswith("#"):
                #to append the 1 byte hex equivalent of 2nd operand to opcode
                if instruction_split[1].startswith("#") == True:
                    start_index = 1
                else:
                    start_index = 0
                if instruction_split[1].endswith("H") == True:
                    opcode_to_return += (instruction_split[1][start_index:-1])
                    return opcode_to_return
                else:
                    opcode_to_return += str(hex(int(instruction_split[1][start_index:])))[2:]
                    return opcode_to_return
    #Returns NOP equivalent opcode if the instruction is invalid
    return "0x00"

def conv_Ins_to_OPCode(input_file):
    with open(input_file, "r") as file:
        content = file.read().splitlines()
        Global_variables.input_instruction_list = content
        for instruction in content:
            Global_variables.instruction_list.append(ReturnOPCode(instruction))
            #print ReturnOPCode(instruction), " ---> opcode for ", instruction, "\n"
    return

def execute_program():
    Global_variables.IR = Global_variables.instruction_list[Global_variables.PC]
    Global_variables.PC += 1
    execute_instruction()
    if Global_variables.PC < len(Global_variables.instruction_list):
        return (True, Global_variables.input_instruction_list[Global_variables.PC-1])
    else:
        return (False, Global_variables.input_instruction_list[Global_variables.PC-1] + " and END")

def execute_instruction():
    int_opcode = int(Global_variables.IR[2:4], 16)
    optional_second_operand = False
    if len(Global_variables.IR) > 4:
        optional_second_operand = Global_variables.IR[4:]
    if int_opcode in [0, 16] or int_opcode % 16 == 8:
        if int_opcode == 0:
            time.sleep(0.2)
        elif int_opcode == 16:
            Global_variables.C = 1
        elif int_opcode == 8:
            Global_variables.A = 0
        elif int_opcode == 24:
            Global_variables.C = 0
        elif int_opcode == 40:
            Global_variables.A = int(hex(~Global_variables.A & 255)[2:], 16)
        elif int_opcode == 56:
            Global_variables.C = (1 - Global_variables.C) % 2
        elif int_opcode == 72:
            Global_variables.A = Global_variables.A << 1
            Global_variables.A = (Global_variables.A + Global_variables.A/256 ) % 256
        elif int_opcode == 88:
            Global_variables.A = (Global_variables.A % 2)*256 + Global_variables.A
            Global_variables.A = (Global_variables.A >> 1) % 256
        elif int_opcode == 104:
            Global_variables.A = Global_variables.A << 1 + Global_variables.C
            Global_variables.C = Global_variables.A/256
            Global_variables.A = Global_variables.A % 256
        elif int_opcode == 120:
            Global_variables.A = Global_variables.A + Global_variables.C*256
            Global_variables.C = Global_variables.A%2
            Global_variables.A = (Global_variables.A >> 1) % 256
        elif int_opcode == 136:
            Global_variables.A = Global_variables.A*Global_variables.B
            Global_variables.B = Global_variables.A%256
            Global_variables.A = Global_variables.A/256
            Global_variables.C = 0
        elif int_opcode == 152:
            Global_variables.A = (Global_variables.A/Global_variables.B)*256 | Global_variables.A
            Global_variables.B = (Global_variables.A%256) % Global_variables.B
            Global_variables.A = Global_variables.A/256
            Global_variables.C = 0
    elif int_opcode <= 7:
        #INC Instruction
        if int_opcode == 1:
            Global_variables.A = (Global_variables.A+1) % 256
        elif int_opcode == 2:
            Global_variables.memory[Global_variables.Reg_0to3[0]] = (Global_variables.memory[Global_variables.Reg_0to3[0]]+1) % 256
        elif int_opcode == 3:
            Global_variables.memory[Global_variables.Reg_0to3[1]] = (Global_variables.memory[Global_variables.Reg_0to3[1]]+1) % 256
        else:
            Global_variables.Reg_0to3[int_opcode-4] = (Global_variables.Reg_0to3[int_opcode-4]+1) % 256
    elif int_opcode < 23:
        #DEC Instruction
        if int_opcode %16 == 1:
            Global_variables.A = (Global_variables.A-1) % 256
        elif int_opcode %16 == 2:
            Global_variables.memory[Global_variables.Reg_0to3[0]] = (Global_variables.memory[Global_variables.Reg_0to3[0]] - 1) % 256
        elif int_opcode % 16 == 3:
            Global_variables.memory[Global_variables.Reg_0to3[1]] = (Global_variables.memory[Global_variables.Reg_0to3[1]] - 1) % 256
        else:
            Global_variables.Reg_0to3[int_opcode-20] = (Global_variables.Reg_0to3[int_opcode-20] - 1) % 256
    elif int_opcode <= 119:
        second_operand = find_second_operand(int_opcode, optional_second_operand)
        if int_opcode/16 == 2:
            #ADD instruction
            Global_variables.A = Global_variables.A + second_operand
            if Global_variables.A >= 256:
                Global_variables.C = 1
                Global_variables.A = Global_variables.A % 256
            else:
                Global_variables.C = 0
        elif int_opcode/16 == 3:
            #ADDC instruction
            Global_variables.A = Global_variables.A + second_operand + Global_variables.C
            if Global_variables.A >= 256:
                Global_variables.C = 1
                Global_variables.A = Global_variables.A % 256
            else:
                Global_variables.C = 0
        elif int_opcode/16 == 4:
            #SUBB instruction
            Global_variables.A = Global_variables.A - second_operand - Global_variables.C
            if Global_variables.A < 0:
                Global_variables.C = 1
                Global_variables.A = Global_variables.A % 256
            else:
                Global_variables.C = 0
        elif int_opcode/16 == 5:
            #ORL instruction
            Global_variables.A = ( Global_variables.A | second_operand ) & 255
        elif int_opcode/16 == 6:
            #ANL instruction
            Global_variables.A = ( Global_variables.A & second_operand ) & 255
        elif int_opcode/16 == 7:
            #XRL instruction
            Global_variables.A = ( Global_variables.A ^ second_operand ) & 255
    else:
        #MOV Instructions
        second_operand = find_second_operand(int_opcode, optional_second_operand)
        if int_opcode/16 == 8:
            Global_variables.A = second_operand
        elif int_opcode/16 == 9:
            Global_variables.Reg_0to3[0] = second_operand
        elif int_opcode/16 == 10:
            Global_variables.Reg_0to3[1] = second_operand
        elif int_opcode/16 == 11:
            Global_variables.Reg_0to3[2] = second_operand
        elif int_opcode/16 == 12:
            Global_variables.Reg_0to3[3] = second_operand
        else:
            if int_opcode == 208:
                Global_variables.A = Global_variables.B
            elif int_opcode == 209:
                Global_variables.B = Global_variables.A
            elif int_opcode == 210:
                Global_variables.memory[Global_variables.Reg_0to3[0]] = Global_variables.A
            elif int_opcode == 211:
                Global_variables.memory[Global_variables.Reg_0to3[1]] = Global_variables.A
            elif int_opcode >=212 and int_opcode <= 215:
                Global_variables.Reg_0to3[int_opcode-212] = Global_variables.A
    #print "All registers value"
    #print "\nA, B, C, Reg", Global_variables.A, Global_variables.B, Global_variables.C, Global_variables.Reg_0to3
            
def find_second_operand(int_opcode, optional_2nd_arg):
    if optional_2nd_arg != False:
        if int_opcode % 16 == 0:
            return int(optional_2nd_arg, 16)
        elif int_opcode % 16 == 1:
            return Global_variables.memory[int(optional_2nd_arg, 16)]
    else:
        if int_opcode % 16 == 2:
            return Global_variables.memory[Global_variables.Reg_0to3[0]]
        elif int_opcode % 16 == 3:
            return Global_variables.memory[Global_variables.Reg_0to3[1]]
        elif int_opcode % 16 in [4, 5, 6, 7]:
            return Global_variables.Reg_0to3[(int_opcode % 16)-4]
        else:
            return 0

def conv_hex(reg):
    hex_reg = []
    for register in reg:
        hex_reg_elem = hex(register)
        if len(hex_reg_elem) == 3:
            hex_reg_elem = '0x0' + hex_reg_elem[-1]
        hex_reg.append(hex_reg_elem)
    return hex_reg

def render_memory():
    return_array = [0]*16
    for mem_index in range(0,16):
        return_array[mem_index] = [hex(mem_index)+"_"] + conv_hex(Global_variables.memory[16*mem_index:16*(mem_index+1)])
    return return_array

@app.route('/')
def index():
   return render_template("processor_simulator.html", input_file = Global_variables.filename, A = hex(Global_variables.A), B = hex(Global_variables.B), C = Global_variables.C, Reg = conv_hex(Global_variables.Reg_0to3), mem = render_memory(), PC = Global_variables.PC, IR = Global_variables.IR, Stack = [Stack.PC, hex(Stack.A), hex(Stack.B), Stack.C], Stack_reg = conv_hex(Stack.Reg), enable = True, instruction = "")

@app.route('/choose_input', methods = ['POST', 'GET'] )
def choose_input():
    window = Tk()
    Global_variables.filename = tkFileDialog.askopenfilename(title = "Select input file",filetypes = (("text files","*.txt"),("all files","*.*")))
    window.destroy()
    initialise_global_var()
    Global_variables.OPCode_list = generate_OPCode()
    conv_Ins_to_OPCode(Global_variables.filename)
    return render_template("processor_simulator.html", input_file = Global_variables.filename, A = hex(Global_variables.A), B = hex(Global_variables.B), C = Global_variables.C, Reg = conv_hex(Global_variables.Reg_0to3), mem = render_memory(), PC = Global_variables.PC, IR = Global_variables.IR, Stack = [Stack.PC, hex(Stack.A), hex(Stack.B), Stack.C], Stack_reg = conv_hex(Stack.Reg), enable = True, instruction = "")

@app.route('/next_ins', methods = ['POST', 'GET'] )
def next_ins():
    check_for_interrupt =  request.form.getlist('interrupt');
    if check_for_interrupt != [u'True']:
        (enable, instruction) = execute_program()
        return render_template("processor_simulator.html", input_file = Global_variables.filename, A = hex(Global_variables.A), B = hex(Global_variables.B), C = Global_variables.C, Reg = conv_hex(Global_variables.Reg_0to3), mem = render_memory(), PC = Global_variables.PC, IR = Global_variables.IR, Stack = [Stack.PC, hex(Stack.A), hex(Stack.B), Stack.C], Stack_reg = conv_hex(Stack.Reg), enable = enable, instruction = instruction)
    else:
        ISR()
        dummyPC = Global_variables.PC
        dummyReg = Global_variables.Reg_0to3
        dummyA = Global_variables.A
        dummyB = Global_variables.B
        dummyC = Global_variables.C
        Global_variables.PC = Stack.PC
        Global_variables.Reg_0to3 = Stack.Reg
        Global_variables.A = Stack.A
        Global_variables.B = Stack.B
        Global_variables.C = Stack.C
        Push(0, [0]*4, 0, 0, 0)
        return render_template("processor_simulator.html", input_file = Global_variables.filename, A = hex(dummyA), B = hex(dummyB), C = dummyC, Reg = conv_hex(dummyReg), mem = render_memory(), PC = dummyPC, IR = Global_variables.IR, Stack = [Global_variables.PC, hex(Global_variables.A), hex(Global_variables.B), Global_variables.C], Stack_reg = conv_hex(Global_variables.Reg_0to3), enable = True, instruction = "PUSH and CPL A")


if __name__ == '__main__':
   app.run(host='0.0.0.0',port=5000)
