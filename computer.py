import time  

class RAM:
    def __init__(self, size=256):
        self.size = size
        self.cells = [0]*size # Each cell stores a single byte

    def read(self, address):
        return self.cells[address & 0xFF]

    def write(self, address, value):
        self.cells[address & 0xFF] = value & 0xFF

class CPU:
    def __init__(self, ram):
        self.ram = ram
        self.registers = [0]*4 # R0-R3, each 8-bit
        self.PC = 0 # Program Counter
        self.flags = {"Z":0, "C":0} # Zero and Carry flags
        self.halted = False

    # ALU operations
    def ADD(self, rd, rs):
        result = self.registers[rd] + self.registers[rs]
        self.flags["C"] = int(result > 0xFF)
        result &= 0xFF
        self.flags["Z"] = int(result == 0)
        self.registers[rd] = result

    def SUB(self, rd, rs):
        result = self.registers[rd] - self.registers[rs]
        self.flags["C"] = int(result < 0)
        result &= 0xFF
        self.flags["Z"] = int(result == 0)
        self.registers[rd] = result

    # Fetch Decode Execute
    def step(self):
        instr = self.ram.read(self.PC)
        operand = self.ram.read(self.PC + 1)
        self.PC = (self.PC + 2) & 0xFF

        opcode = (instr >> 4) & 0xF
        rd = (instr >> 2) & 0x3
        rs = instr & 0x3

        if opcode == 0x0: # NOP
            pass
        elif opcode == 0x1: # MOV rd, rs
            self.registers[rd] = self.registers[rs]
        elif opcode == 0x3: # ADD rd, rs
            self.ADD(rd, rs)
        elif opcode == 0x4: # SUB rd, rs
            self.SUB(rd, rs)
        elif opcode == 0x5: # LDI rd, imm
            self.registers[rd] = operand
            self.flags["Z"] = int(self.registers[rd]==0)
        elif opcode == 0x6: # LDR rd, [addr]
            self.registers[rd] = self.ram.read(operand)
            self.flags["Z"] = int(self.registers[rd]==0)
        elif opcode == 0x7: # STR rs, [addr]
            self.ram.write(operand, self.registers[rs])
        elif opcode == 0xF: # HLT
            self.halted = True

class Computer:
    def __init__(self):
        self.ram = RAM()
        self.cpu = CPU(self.ram)
        self.connected_disks = []
        self.plugged_disk = None

    def assemble(self, program):
        regmap = {"R0":0,"R1":1,"R2":2,"R3":3}
        opmap = {"NOP":0x0,"MOV":0x1,"ADD":0x3,"SUB":0x4,"LDI":0x5,"LDR":0x6,"STR":0x7,"HLT":0xF}

        machine_code = []
        for line in program.splitlines():
            line = line.strip()
            if not line or line.startswith(";"):
                continue

            parts = line.replace(",", "").split()
            instr = parts[0].upper()
            rd = rs = byte2 = 0

            if instr in ("MOV","ADD","SUB"):
                rd = regmap[parts[1]]
                rs = regmap[parts[2]]
            elif instr == "LDI":
                rd = regmap[parts[1]]
                byte2 = int(parts[2]) & 0xFF
            elif instr == "LDR":
                rd = regmap[parts[1]]
                byte2 = int(parts[2]) & 0xFF
            elif instr == "STR":
                rs = regmap[parts[1]]
                byte2 = int(parts[2]) & 0xFF

            opcode = opmap[instr]
            byte1 = ((opcode & 0xF)<<4) | ((rd & 0x3)<<2) | (rs & 0x3)
            machine_code.append(byte1)
            machine_code.append(byte2)

        return machine_code

    def load_program(self, machine_code):
        for i, byte in enumerate(machine_code):
            self.ram.write(i, byte)

    def run(self, delay=0):
        while not self.cpu.halted:
            self.cpu.step()
            if delay > 0:
                time.sleep(delay)
