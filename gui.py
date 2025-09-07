import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from computer import Computer

class ComputerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-bit CPU Simulator")
        self.root.geometry("1000x600")
        self.computer = Computer()

        tb.Style(theme="morph")

        # Assembly Editor
        asm_frame = tb.Frame(root)
        asm_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.code_input = tb.Text(asm_frame, wrap="none", font=("consolas", 14))
        self.code_input.grid(row=0, column=0, sticky="nsew")
        scrollbar_v = tb.Scrollbar(asm_frame, orient="vertical", command=self.code_input.yview)
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        self.code_input.configure(yscrollcommand=scrollbar_v.set)
        asm_frame.grid_rowconfigure(0, weight=1)
        asm_frame.grid_columnconfigure(0, weight=1)

        # RAM Viewer
        ram_frame = tb.Frame(root)
        ram_frame.grid(row=0, column=1, sticky="nsew", pady=5)
        self.ram_table = tb.Treeview(ram_frame, columns=("addr", "bin"), show="headings", height=25)
        self.ram_table.heading("addr", text="Address")
        self.ram_table.heading("bin", text="Binary")
        self.ram_table.column("addr", width=70, anchor="center")
        self.ram_table.column("bin", width=150, anchor="center")
        self.ram_table.grid(row=0, column=0, sticky="nsew")
        ram_scroll_v = tb.Scrollbar(ram_frame, orient="vertical", command=self.ram_table.yview)
        ram_scroll_v.grid(row=0, column=1, sticky="ns")
        self.ram_table.configure(yscrollcommand=ram_scroll_v.set)
        ram_frame.grid_rowconfigure(0, weight=1)
        ram_frame.grid_columnconfigure(0, weight=1)

        self.ram_rows = []
        for addr, val in enumerate(self.computer.ram.cells):
            row = self.ram_table.insert("", "end", values=(addr, f"{val:08b}"))
            self.ram_rows.append(row)
        self.last_pc = None
        self.ram_table.tag_configure("pc", background="lightblue")

        # I/O Box (Right)
        io_frame = tb.Frame(root)
        io_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self.io_display = tb.Text(io_frame, height=10, state="disabled")
        self.io_display.pack(fill="both", expand=True)

        # Input + Feed Input
        input_frame = tb.Frame(io_frame)
        input_frame.pack(fill="both")
        self.io_entry = tb.Entry(input_frame)
        self.io_entry.pack(side="left", fill="x", expand=True)
        tb.Button(input_frame, text="Feed Input", command=self.feed_input, bootstyle=INFO).pack(side="left")

        # Registers Table
        self.reg_table = tb.Treeview(io_frame, columns=("reg", "value"), show="headings", height=6)
        self.reg_table.heading("reg", text="Register")
        self.reg_table.heading("value", text="Value (Binary)")
        self.reg_table.column("reg", width=120, anchor="center")
        self.reg_table.column("value", width=120, anchor="center")
        self.reg_table.pack(fill="x")

        # Flags/HALT Table
        self.flag_table = tb.Treeview(io_frame, columns=("flag", "value"), show="headings", height=4)
        self.flag_table.heading("flag", text="Flag")
        self.flag_table.heading("value", text="Value")
        self.flag_table.column("flag", width=120, anchor="center")
        self.flag_table.column("value", width=120, anchor="center")
        self.flag_table.pack(fill="x")

        # Control Buttons
        btn_frame = tb.Frame(io_frame)
        btn_frame.pack(fill="x")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        tb.Button(btn_frame, text="Assemble", command=self.assemble, bootstyle=PRIMARY)\
            .grid(row=0, column=0, sticky="nsew")
        tb.Button(btn_frame, text="Run", command=self.run_program, bootstyle=SUCCESS)\
            .grid(row=0, column=1, sticky="nsew")
        tb.Button(btn_frame, text="Step", command=self.step_program, bootstyle=INFO)\
            .grid(row=0, column=2, sticky="nsew")

        # Reset Button Below
        reset_frame = tb.Frame(io_frame)
        reset_frame.pack(fill="x")
        tb.Button(reset_frame, text="Reset", command=self.reset_computer, bootstyle=DANGER)\
            .pack(fill="x")


        # Configure root grid
        root.grid_columnconfigure(0, weight=3, uniform="group1")
        root.grid_columnconfigure(1, weight=3, uniform="group1")
        root.grid_columnconfigure(2, weight=3, uniform="group1")
        root.grid_rowconfigure(0, weight=1)

        self.update_display()

    def assemble(self):
        program = self.code_input.get("1.0", "end")
        try:
            machine_code = self.computer.assemble(program)
            self.computer = Computer()
            self.computer.load_program(machine_code)
            self.io_display.config(state="normal")
            self.io_display.delete("1.0", "end")
            self.io_display.config(state="disabled")
            self.update_display()
        except Exception as e:
            messagebox.showerror("Assemble Error", str(e))

    def run_program(self):
        def step_loop():
            if not self.computer.cpu.halted:
                self.computer.cpu.step()
                self.update_display()
                self.root.after(50, step_loop)
        step_loop()

    def step_program(self):
        if not self.computer.cpu.halted:
            self.computer.cpu.step()
            self.update_display()

    def feed_input(self):
        text = self.io_entry.get()
        self.io_entry.delete(0, "end")
        self.computer.io.feed_input(text)
        self.update_display()

    def update_display(self):
        # RAM Viewer
        for addr, val in enumerate(self.computer.ram.cells):
            self.ram_table.item(self.ram_rows[addr], values=(addr, f"{val:08b}"))

        pc = self.computer.cpu.PC
        if self.last_pc is not None:
            self.ram_table.item(self.ram_rows[self.last_pc], tags=())
        self.ram_table.item(self.ram_rows[pc], tags=("pc",))
        self.last_pc = pc

        # Registers
        self.reg_table.delete(*self.reg_table.get_children())
        regs = self.computer.cpu.registers
        self.reg_table.insert("", "end", values=("R0", f"{regs[0]:08b}"))
        self.reg_table.insert("", "end", values=("R1", f"{regs[1]:08b}"))
        self.reg_table.insert("", "end", values=("R2", f"{regs[2]:08b}"))
        self.reg_table.insert("", "end", values=("R3", f"{regs[3]:08b}"))
        self.reg_table.insert("", "end", values=("PC", f"{self.computer.cpu.PC:08b}"))

        # Flags
        self.flag_table.delete(*self.flag_table.get_children())
        flags = self.computer.cpu.flags
        self.flag_table.insert("", "end", values=("Z Flag", f"{flags['Z']}"))
        self.flag_table.insert("", "end", values=("C Flag", f"{flags['C']}"))
        self.flag_table.insert("", "end", values=("HALT", f"{self.computer.cpu.halted}"))

        # I/O Output
        self.io_display.config(state="normal")
        self.io_display.delete("1.0", "end")
        output = "".join(chr(b) for b in self.computer.io.output_buff)
        self.io_display.insert("end", output)
        self.io_display.config(state="disabled")

    def reset_computer(self):
        self.computer = Computer()
        self.io_display.config(state="normal")
        self.io_display.delete("1.0", "end")
        self.io_display.config(state="disabled")
        self.code_input.delete("1.0", "end")
        self.update_display()

if __name__ == "__main__":
    root = tb.Window()
    gui = ComputerGUI(root)
    root.mainloop()
