import os
import pyperclip
import subprocess
import webbrowser
from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog, messagebox
from pdf2image import convert_from_path

# Title
title = "Py-Tess-OCR"

# Path to the Tesseract and poppler executable
tesseract_path = r'Tesseract\tesseract.exe'
poppler_path = r'Poppler\Library\bin'

# For hide subprocess terminal
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

# For store selected languages
selected_languages = []
# Default output file name placeholder
output_name_placeholder = "Enter the output name here. (Default: 'output' or input-file)"
# Default ouput file name
default_output_name = "output"


def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        input_entry.delete(0, END)
        input_entry.insert(END, directory)


def select_file():
    # Define the allowed file extensions
    filetypes = [
        ("Image files", "*.jpg;*.jpeg;*.png;*.gif;*.bmp"),
        ("PDF files", "*.pdf"),
        # ("All files", "*.*")
    ]
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        input_entry.delete(0, END)
        input_entry.insert(END, file_path)


def generate():
    if input_entry.get() == "":
        messagebox.showerror(
            "Error", "The input field can't be empty. \nPlease select a file or directory, and try again.")
    else:
        process_files(input_entry.get())


def process_files(path, clipb=False):
    if os.path.isfile(path):
        if path.lower().endswith('.pdf'):
            process_pdf(path, clipb)
        elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            process_image(path, clipb)
        else:
            messagebox.showinfo('Invalid File', 'Invalid file selected.')
    elif os.path.isdir(path):
        process_mix(path, clipb)


def get_available_languages():
    command = [tesseract_path, '--list-langs']
    output = subprocess.check_output(
        command, startupinfo=startupinfo).decode('utf-8').strip()
    lang_list = output.splitlines()[1:]
    lang_list.remove('osd')
    return lang_list


def check_output_name():
    if output_entry.get() == output_name_placeholder:
        return default_output_name
    else:
        return output_entry.get()


def process_image(directory, clipb):
    # Output file path
    output_format = output_dropdown.get().lower()
    output_file = os.path.splitext(directory)[0] + f'.{output_format}'
    # Process selected image
    if not clipb:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Run Tesseract OCR command
            if advance_option_selection():
                command = [tesseract_path, directory,
                           'stdout', '-l', check_selected_languages(), '--oem', str(get_oem_value()), '--psm', str(get_psm_value()), output_format]
            else:
                command = [tesseract_path, directory,
                           'stdout', '-l', check_selected_languages(), output_format]
            try:
                output = subprocess.check_output(
                    command, startupinfo=startupinfo).decode('utf-8').strip()

                # Write the OCR result to the output file
                f.write('{}\n\n'.format(output))

                messagebox.showinfo('Conversion Completed',
                                    'File converted successfully.')
            except subprocess.CalledProcessError as e:
                messagebox.showerror('Conversion Failed',
                                     'The selected OCR engine is not supported for the selected language.')
    else:
        # Run Tesseract OCR command
        if advance_option_selection():
            command = [tesseract_path, directory,
                       'stdout', '-l', check_selected_languages(), '--oem', str(get_oem_value()), '--psm', str(get_psm_value()), output_format]
        else:
            command = [tesseract_path, directory,
                       'stdout', '-l', check_selected_languages()]
        try:
            output = subprocess.check_output(
                command, startupinfo=startupinfo).decode('utf-8').strip()
            copy_to_clipboard(output)
        except subprocess.CalledProcessError as e:
            messagebox.showerror('Conversion Failed',
                                 'The selected OCR engine is not supported for the selected language.')


def process_pdf(file, clipb):
    # Convert PDF to images
    images = convert_from_path(file)
    error_status = False

    # Output file path
    output_format = output_dropdown.get().lower()
    output_file = os.path.splitext(file)[0] + f'.{output_format}'

    # Process each image
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, image in enumerate(images):
            # Save the image to a temporary file
            image_path = f'temp_image_{i}.png'
            image.save(image_path)

            # Run Tesseract OCR command
            if advance_option_selection():
                command = [tesseract_path, image_path,
                           'stdout', '-l', check_selected_languages(), '--oem', str(get_oem_value()), '--psm', str(get_psm_value()), output_format]
            else:
                command = [tesseract_path, image_path,
                           'stdout', '-l', check_selected_languages(), output_format]
            try:
                output = subprocess.check_output(
                    command, startupinfo=startupinfo).decode('utf-8').strip()

                # Write the OCR result to the output file
                f.write('## Page {}\n\n'.format(i + 1))
                f.write('{}\n\n'.format(output))
            except subprocess.CalledProcessError as e:
                error_status = True
            # Remove the temporary image file
            os.remove(image_path)
    if not clipb:
        if error_status:
            messagebox.showerror('Conversion Failed',
                                 'The selected OCR engine is not supported for the selected language.')
        else:
            messagebox.showinfo('Conversion Completed',
                                'File converted successfully.')
    else:
        if error_status:
            messagebox.showerror('Conversion Failed',
                                 'The selected OCR engine is not supported for the selected language.')
        else:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            copy_to_clipboard(content)
        os.remove(output_file)


def process_mix(directory, clipb):
    error_status = False
    # List all image files in the directory
    image_files = [file for file in os.listdir(directory) if file.lower().endswith(
        ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf'))]
    if not image_files:
        messagebox.showinfo('No Images/PDF Found',
                            'No image/PDF files found in the selected directory.')
        return

    # Output file path
    output_name = check_output_name()
    output_format = output_dropdown.get().lower()
    output_file = os.path.join(
        directory, f'{output_name}.{output_format}')

    # Process each image file
    with open(output_file, 'w', encoding='utf-8') as f:
        for image_file in image_files:
            if image_file.lower().endswith(
                    ('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                # Run Tesseract OCR command
                image_path = os.path.join(directory, image_file)
                if advance_option_selection():
                    command = [tesseract_path, image_path,
                               'stdout', '-l', check_selected_languages(), '--oem', str(get_oem_value()), '--psm', str(get_psm_value()), output_format]
                else:
                    command = [tesseract_path, image_path,
                               'stdout', '-l', check_selected_languages(), output_format]

                try:
                    output = subprocess.check_output(
                        command, startupinfo=startupinfo).decode('utf-8').strip()

                    # Write the OCR result to the output file
                    f.write('## {}\n\n'.format(image_file))
                    f.write('{}\n\n'.format(output))
                except subprocess.CalledProcessError as e:
                    error_status = True
            else:
                pdf_img = convert_from_path(
                    os.path.join(directory, image_file))
                for i, image in enumerate(pdf_img):
                    image_path = f'temp_image_{i}.png'
                    image.save(image_path)

                    if advance_option_selection():
                        command = [tesseract_path, image_path,
                                   'stdout', '-l', check_selected_languages(), '--oem', str(get_oem_value()), '--psm', str(get_psm_value()), output_format]
                    else:
                        command = [tesseract_path, image_path,
                                   'stdout', '-l', check_selected_languages(), output_format]

                    try:
                        output = subprocess.check_output(
                            command, startupinfo=startupinfo).decode('utf-8').strip()

                        # Write the OCR result to the output file
                        f.write('## {}\n\n'.format(image_file))
                        f.write('{}\n\n'.format(output))
                    except subprocess.CalledProcessError as e:
                        error_status = True

                    # Remove the temporary image file
                    os.remove(image_path)
    if not clipb:
        if error_status:
            messagebox.showerror('Conversion Failed',
                                 'The selected OCR engine is not supported for the selected language.')
        else:
            messagebox.showinfo('Conversion Completed',
                                'Files/Images converted successfully.')
    else:
        if error_status:
            messagebox.showerror('Conversion Failed',
                                 'The selected OCR engine is not supported for the selected language.')
        else:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            copy_to_clipboard(content)
        os.remove(output_file)


def convert_to_image(file):
    return convert_from_path(file, poppler_path=poppler_path)


def copy_to_clipboard(content):
    pyperclip.copy(content)
    if not content == "":
        messagebox.showinfo('Copy to Clipboard',
                            'Content copied to clipboard.')
    else:
        messagebox.showerror('Error',
                             'Content not copied to clipboard.')


def select_clipboard(file):
    if input_entry.get() == "":
        messagebox.showerror(
            "Error", "The input field can't be empty. \nPlease select a file or directory, and try again.")
    else:
        process_files(input_entry.get(), True)


def get_selected_languages():
    selected_options = [label for var, label in zip(
        selected_languages, available_languages) if var.get() == 1]
    return selected_options


def check_selected_languages():
    selected_options = [label for var, label in zip(
        selected_languages, available_languages) if var.get() == 1]
    if selected_options == []:
        return 'eng'
    else:
        return '+'.join(selected_options)


def support():
    url = "https://github.com/HasithaSuneth/Py-Tess-OCR"
    webbrowser.open(url)


# ----------------------------------- GUI ------------------------------------- #
# Main window
window = Tk()
window.title(title)
window.configure(bg='#424242')
window.resizable(False, False)
window.iconbitmap('Data/Images/icon.ico')

# ToolTips


class Tooltip:
    def __init__(self, widget,
                 *,
                 bg='#424242',
                 pad=(5, 3, 5, 3),
                 text='widget info',
                 waittime=400,
                 wraplength=250,
                 enterimage=None,
                 leaveimage=None):

        self.waittime = waittime  # in miliseconds
        self.wraplength = wraplength  # in pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.onEnter)
        self.widget.bind("<Leave>", self.onLeave)
        self.widget.bind("<ButtonPress>", self.onLeave)
        self.bg = bg
        self.pad = pad
        self.id = None
        self.tw = None
        self.enterimage = enterimage
        self.leaveimage = leaveimage

    def onEnter(self, event=None):
        self.schedule()
        if self.enterimage != 'None':
            self.widget.config(image=self.enterimage)

    def onLeave(self, event=None):
        self.unschedule()
        self.hide()
        if self.leaveimage != 'None':
            self.widget.config(image=self.leaveimage)

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self):
        def tip_pos_calculator(widget, label, *, tip_delta=(10, 5), pad=(5, 3, 5, 3)):
            w = widget
            s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()
            width, height = (pad[0] + label.winfo_reqwidth() + pad[2],
                             pad[1] + label.winfo_reqheight() + pad[3])
            mouse_x, mouse_y = w.winfo_pointerxy()
            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            x2, y2 = x1 + width, y1 + height
            x_delta = x2 - s_width
            if x_delta < 0:
                x_delta = 0
            y_delta = y2 - s_height
            if y_delta < 0:
                y_delta = 0
            offscreen = (x_delta, y_delta) != (0, 0)
            if offscreen:
                if x_delta:
                    x1 = mouse_x - tip_delta[0] - width
                if y_delta:
                    y1 = mouse_y - tip_delta[1] - height
            offscreen_again = y1 < 0  # out on the top
            if offscreen_again:
                y1 = 0
            return x1, y1
        bg = self.bg
        pad = self.pad
        widget = self.widget
        # creates a toplevel window
        self.tw = Toplevel(widget)
        self.tw.wm_overrideredirect(True)
        win = Frame(self.tw,
                    background=bg,
                    borderwidth=0)
        label = Label(win,
                      text=self.text,
                      justify=LEFT,
                      background=bg,
                      relief=SOLID,
                      borderwidth=0,
                      wraplength=self.wraplength,
                      fg="white")
        label.grid(padx=(pad[0], pad[2]),
                   pady=(pad[1], pad[3]),
                   sticky=NSEW)
        win.grid()
        x, y = tip_pos_calculator(widget, label)
        self.tw.wm_geometry("+%d+%d" % (x, y))

    def hide(self):
        tw = self.tw
        if tw:
            tw.destroy()
        self.tw = None


def select_file_enter(event):
    button_select_file.config(image=select_file_enter_img)


def select_file_leave(event):
    button_select_file.config(image=select_file_leave_img)


def select_folder_enter(event):
    button_select_directory.config(image=select_folder_enter_img)


def select_folder_leave(event):
    button_select_directory.config(image=select_folder_leave_img)


def generate_enter(event):
    button_generate.config(image=generate_enter_img)


def generate_leave(event):
    button_generate.config(image=generate_leave_img)


def help_enter(event):
    button_help.config(image=help_enter_img)


def help_leave(event):
    button_help.config(image=help_leave_img)


def clipboard_enter(event):
    button_copy_to_clipboard.config(image=clipboard_enter_img)


def clipboard_leave(event):
    button_copy_to_clipboard.config(image=clipboard_leave_img)


def prep(event):
    messagebox.showinfo(
        "About", " Contact : Hasitha Suneth \n Email : hasisuneth@gmail.com \n Website : hasithasuneth.com")


def checkbox_lang_enter(checkbox):
    checkbox.config(selectcolor="#2c4c66")
    checkbox.config(bg="#2c4c66")


def checkbox_lang_leave(checkbox):
    checkbox.config(selectcolor="#2c4c66")
    checkbox.config(bg="#424242")


def advance_head_enter(event):
    advance_head_checkbutton.config(selectcolor="#2c4c66")
    advance_head_checkbutton.config(bg="#2c4c66")


def advance_head_leave(event):
    advance_head_checkbutton.config(selectcolor="#2c4c66")
    advance_head_checkbutton.config(bg="#424242")


def clear_placeholder(event):
    if output_entry.get() == output_name_placeholder:
        output_entry.delete(0, END)


def restore_placeholder(event):
    if output_entry.get() == '':
        output_entry.insert(0, output_name_placeholder)


def advance_toggle():
    if advance_head_var.get() == 1:
        advance_body_frame.grid(
            row=7, column=0, sticky=W+E+S+N, padx=(10, 10), pady=(0, 5))
    else:
        advance_body_frame.grid_forget()
        advance_oem_deselect()
        advance_oem_checkbutton_3.select()
        advance_psm_deselect()
        advance_psm_checkbutton_3.select()


def advance_option_selection():
    if advance_head_var.get() == 1:
        return True
    else:
        return False


def get_oem_value():
    if advance_oem_var_0.get() == 1:
        return 0
    elif advance_oem_var_1.get() == 1:
        return 1
    elif advance_oem_var_2.get() == 1:
        return 2
    else:
        return 3


def get_psm_value():
    if advance_psm_var_0.get() == 1:
        return 0
    elif advance_psm_var_1.get() == 1:
        return 1
    elif advance_psm_var_2.get() == 1:
        return 2
    elif advance_psm_var_3.get() == 1:
        return 3
    elif advance_psm_var_4.get() == 1:
        return 4
    elif advance_psm_var_5.get() == 1:
        return 5
    elif advance_psm_var_6.get() == 1:
        return 6
    elif advance_psm_var_7.get() == 1:
        return 7
    elif advance_psm_var_8.get() == 1:
        return 8
    elif advance_psm_var_9.get() == 1:
        return 9
    elif advance_psm_var_10.get() == 1:
        return 10
    elif advance_psm_var_11.get() == 1:
        return 11
    elif advance_psm_var_12.get() == 1:
        return 12
    else:
        return 13


def advance_oem_toggle_0():
    if advance_oem_var_0.get() == 1:
        advance_oem_deselect()
        advance_oem_checkbutton_0.select()
    else:
        advance_oem_checkbutton_0.select()


def advance_oem_toggle_1():
    if advance_oem_var_1.get() == 1:
        advance_oem_deselect()
        advance_oem_checkbutton_1.select()
    else:
        advance_oem_checkbutton_1.select()


def advance_oem_toggle_2():
    if advance_oem_var_2.get() == 1:
        advance_oem_deselect()
        advance_oem_checkbutton_2.select()
    else:
        advance_oem_checkbutton_2.select()


def advance_oem_toggle_3():
    if advance_oem_var_3.get() == 1:
        advance_oem_deselect()
        advance_oem_checkbutton_3.select()
    else:
        advance_oem_checkbutton_3.select()


def advance_oem_deselect():
    advance_oem_checkbutton_0.deselect()
    advance_oem_checkbutton_1.deselect()
    advance_oem_checkbutton_2.deselect()
    advance_oem_checkbutton_3.deselect()


def advance_psm_toggle_0():
    if advance_psm_var_0.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_0.select()
    else:
        advance_psm_checkbutton_0.select()


def advance_psm_toggle_0():
    if advance_psm_var_0.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_0.select()
    else:
        advance_psm_checkbutton_0.select()


def advance_psm_toggle_1():
    if advance_psm_var_1.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_1.select()
    else:
        advance_psm_checkbutton_1.select()


def advance_psm_toggle_2():
    if advance_psm_var_2.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_2.select()
    else:
        advance_psm_checkbutton_2.select()


def advance_psm_toggle_3():
    if advance_psm_var_3.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_3.select()
    else:
        advance_psm_checkbutton_3.select()


def advance_psm_toggle_4():
    if advance_psm_var_4.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_4.select()
    else:
        advance_psm_checkbutton_4.select()


def advance_psm_toggle_5():
    if advance_psm_var_5.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_5.select()
    else:
        advance_psm_checkbutton_5.select()


def advance_psm_toggle_6():
    if advance_psm_var_6.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_6.select()
    else:
        advance_psm_checkbutton_6.select()


def advance_psm_toggle_7():
    if advance_psm_var_7.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_7.select()
    else:
        advance_psm_checkbutton_7.select()


def advance_psm_toggle_8():
    if advance_psm_var_8.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_8.select()
    else:
        advance_psm_checkbutton_8.select()


def advance_psm_toggle_9():
    if advance_psm_var_9.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_9.select()
    else:
        advance_psm_checkbutton_9.select()


def advance_psm_toggle_10():
    if advance_psm_var_10.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_10.select()
    else:
        advance_psm_checkbutton_10.select()


def advance_psm_toggle_11():
    if advance_psm_var_11.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_11.select()
    else:
        advance_psm_checkbutton_11.select()


def advance_psm_toggle_12():
    if advance_psm_var_12.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_12.select()
    else:
        advance_psm_checkbutton_12.select()


def advance_psm_toggle_13():
    if advance_psm_var_13.get() == 1:
        advance_psm_deselect()
        advance_psm_checkbutton_13.select()
    else:
        advance_psm_checkbutton_13.select()


def advance_psm_deselect():
    advance_psm_checkbutton_0.deselect()
    advance_psm_checkbutton_1.deselect()
    advance_psm_checkbutton_2.deselect()
    advance_psm_checkbutton_3.deselect()
    advance_psm_checkbutton_4.deselect()
    advance_psm_checkbutton_5.deselect()
    advance_psm_checkbutton_6.deselect()
    advance_psm_checkbutton_7.deselect()
    advance_psm_checkbutton_8.deselect()
    advance_psm_checkbutton_9.deselect()
    advance_psm_checkbutton_10.deselect()
    advance_psm_checkbutton_11.deselect()
    advance_psm_checkbutton_12.deselect()
    advance_psm_checkbutton_13.deselect()


# Images
select_file_leave_img = ImageTk.PhotoImage(
    Image.open("Data/Images/select_file_button_leave.jpg"))
select_file_enter_img = ImageTk.PhotoImage(
    Image.open("Data/Images/select_file_button_enter.jpg"))
select_folder_leave_img = ImageTk.PhotoImage(
    Image.open("Data/Images/select_folder_button_leave.jpg"))
select_folder_enter_img = ImageTk.PhotoImage(
    Image.open("Data/Images/select_folder_button_enter.jpg"))
input_label_img = ImageTk.PhotoImage(
    Image.open("Data/Images/input_label.jpg"))
output_label_img = ImageTk.PhotoImage(
    Image.open("Data/Images/output_label.jpg"))
generate_leave_img = ImageTk.PhotoImage(
    Image.open("Data/Images/generate_button_leave.jpg"))
generate_enter_img = ImageTk.PhotoImage(
    Image.open("Data/Images/generate_button_enter.jpg"))
help_leave_img = ImageTk.PhotoImage(
    Image.open("Data/Images/help_button_leave.jpg"))
help_enter_img = ImageTk.PhotoImage(
    Image.open("Data/Images/help_button_enter.jpg"))
clipboard_leave_img = ImageTk.PhotoImage(
    Image.open("Data/Images/clipboard_button_leave.jpg"))
clipboard_enter_img = ImageTk.PhotoImage(
    Image.open("Data/Images/clipboard_button_enter.jpg"))

# Frams
input_upper_frame = LabelFrame(
    window, bg='#424242', relief='flat', bd=0)
input_upper_frame.grid(row=1, column=0, sticky=W+E+S+N,
                       padx=(10, 10), pady=(20, 0))

input_frame = LabelFrame(window, bg='#424242', bd=3, relief='solid')
input_frame.grid(row=2, column=0, sticky=W+E+S+N,
                 padx=(10, 10), pady=(0, 10))

output_upper_frame = LabelFrame(
    window, bg='#424242', relief='flat', bd=0)
output_upper_frame.grid(row=3, column=0, sticky=W+E+S+N,
                        padx=(10, 10), pady=(20, 0))

output_frame = LabelFrame(window, bg='#424242', bd=3, relief='solid')
output_frame.grid(row=4, column=0, sticky=W+E+S +
                  N, padx=(10, 10), pady=(0, 10), columnspan=3)

output_lang_frame = LabelFrame(output_frame, bg='#424242', relief='flat')
output_lang_frame.grid(row=5, column=0,  columnspan=2, sticky=E)

advance_head_frame = LabelFrame(window, bg='#424242', relief='flat')
advance_head_frame.grid(row=6, column=0, sticky=W+E+S+N)

advance_body_frame = LabelFrame(window, bg='#424200', relief='solid', bd=3)
# advance_body_frame.grid(row=7, column=0, sticky=W+E+S+N)

advance_oem_frame = LabelFrame(
    advance_body_frame, bg='#424242', relief='solid')
advance_oem_frame.grid(row=0, column=0, sticky=W+E+S +
                       N, padx=(10, 10), pady=(10, 5), ipady=5)

advance_psm_frame = LabelFrame(
    advance_body_frame, bg='#424242', relief='solid')
advance_psm_frame.grid(row=1, column=0,  padx=(10, 10), pady=(5, 10), ipady=3)

generate_frame = LabelFrame(window, bg='#424242', relief='flat')
generate_frame.grid(row=8, column=0)


# Buttons
button_select_file = Button(
    input_frame, text='Select File', command=select_file, image=select_file_leave_img, bg='blue', fg='white', width=154, height=24, relief="flat")
button_select_file.grid(row=0, column=1, padx=(10, 0), pady=(15, 15))
button_select_file.bind('<Enter>', select_file_enter)
button_select_file.bind('<Leave>', select_file_leave)
Tooltip(button_select_file, text='Select an Image or PDF file.', wraplength=200,
        enterimage=select_file_enter_img, leaveimage=select_file_leave_img)

button_select_directory = Button(
    input_frame, text='Select Directory', command=select_directory, image=select_folder_leave_img, bg='blue', fg='white', width=154, height=24, relief="flat")
button_select_directory.grid(
    row=0, column=2, sticky=W, padx=(10, 10), pady=(10, 10))
button_select_directory.bind('<Enter>', select_folder_enter)
button_select_directory.bind('<Leave>', select_folder_leave)
Tooltip(button_select_directory, text='Select a directory containing Images and PDF files.', wraplength=200,
        enterimage=select_folder_enter_img, leaveimage=select_folder_leave_img)

button_generate = Button(
    generate_frame, text='Generate', command=generate, image=generate_leave_img, bg='blue', fg='white', width=194, height=44, relief="flat")
button_generate.grid(row=0, column=2, padx=(10, 10), pady=(10, 10))
button_generate.bind('<Enter>', generate_enter)
button_generate.bind('<Leave>', generate_leave)
Tooltip(button_generate, text='Start the generation process.', wraplength=200,
        enterimage=generate_enter_img, leaveimage=generate_leave_img)

button_copy_to_clipboard = Button(generate_frame, text='C', image=clipboard_leave_img, command=lambda: select_clipboard(
    'output.md'), bg='blue', fg='white', width=44, height=44, relief="flat")
button_copy_to_clipboard.grid(row=0, column=3, padx=(10, 10), pady=(10, 10))
button_copy_to_clipboard.bind('<Enter>', clipboard_enter)
button_copy_to_clipboard.bind('<Leave>', clipboard_leave)
Tooltip(button_copy_to_clipboard, text='Copy the output text to the clipboard.', wraplength=200,
        enterimage=clipboard_enter_img, leaveimage=clipboard_leave_img)

button_help = Button(generate_frame, text='H', command=support, image=help_leave_img,
                     bg='blue', fg='white', width=44, height=44, relief="flat")
button_help.grid(row=0, column=1, padx=(10, 10), pady=(10, 10))
button_help.bind('<Enter>', help_enter)
button_help.bind('<Leave>', help_leave)
Tooltip(button_help, text='Help & Support', wraplength=200,
        enterimage=help_enter_img, leaveimage=help_leave_img)


available_languages = get_available_languages()
# Check button
for index in range(len(available_languages)):
    lang = available_languages[index]
    text = " " + lang.upper()
    colume_num = 1 + index
    var = IntVar()
    lang = Checkbutton(output_lang_frame, indicatoron=0, text=text, variable=var, width=6, font=("Comic Sans MS", "9", "bold"),
                       anchor=W, bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242")
    lang.grid(row=0, column=colume_num, padx=(5, 0), pady=2)
    selected_languages.append(var)
    lang.bind("<Enter>", lambda event,
              checkbox=lang: checkbox_lang_enter(checkbox))
    lang.bind("<Leave>", lambda event,
              checkbox=lang: checkbox_lang_leave(checkbox))
    # Default English
    if available_languages[index] == "eng":
        lang.select()

advance_head_var = IntVar()
advance_head_checkbutton = Checkbutton(advance_head_frame, indicatoron=0, text="Advance Options", width=91, variable=advance_head_var, font=("Helvetica", "9", "bold"),
                                       bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_toggle)
advance_head_checkbutton.grid(
    row=0, column=0, padx=(8, 8), pady=2, sticky=W+E)
advance_head_checkbutton.bind("<Enter>", advance_head_enter)
advance_head_checkbutton.bind("<Leave>", advance_head_leave)

# OEM
advance_oem_var_0 = IntVar()
advance_oem_checkbutton_0 = Checkbutton(advance_oem_frame, indicatoron=0, text="Legacy OCR Engine", width=20, variable=advance_oem_var_0, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_oem_toggle_0)
advance_oem_checkbutton_0.grid(
    row=1, column=0, padx=(8, 0), pady=2, sticky=W+E)
Tooltip(advance_oem_checkbutton_0, text='Legacy engine only', wraplength=200)

advance_oem_var_1 = IntVar()
advance_oem_checkbutton_1 = Checkbutton(advance_oem_frame, indicatoron=0, text="LSTM OCR Engine", width=20, variable=advance_oem_var_1, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_oem_toggle_1)
advance_oem_checkbutton_1.grid(
    row=1, column=1, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_oem_checkbutton_1,
        text='Neural nets LSTM engine only', wraplength=200)

advance_oem_var_2 = IntVar()
advance_oem_checkbutton_2 = Checkbutton(advance_oem_frame, indicatoron=0, text="Legacy + LSTM Engines", width=20, variable=advance_oem_var_2, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_oem_toggle_2)
advance_oem_checkbutton_2.grid(
    row=1, column=2, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_oem_checkbutton_2, text='Legacy + LSTM engines', wraplength=200)

advance_oem_var_3 = IntVar()
advance_oem_checkbutton_3 = Checkbutton(advance_oem_frame, indicatoron=0, text="Automatic", width=20, variable=advance_oem_var_3, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_oem_toggle_3)
advance_oem_checkbutton_3.grid(
    row=1, column=3, padx=(0, 8), pady=2, sticky=W+E)
Tooltip(advance_oem_checkbutton_3,
        text='Default, based on what is available', wraplength=200)
advance_oem_checkbutton_3.select()

# PSM
psm_width = 4
advance_psm_var_0 = IntVar()
advance_psm_checkbutton_0 = Checkbutton(advance_psm_frame, indicatoron=0, text="0", width=psm_width, variable=advance_psm_var_0, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_0)
advance_psm_checkbutton_0.grid(
    row=1, column=0, padx=(42, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_0,
        text='Orientation and script detection (OSD) only', wraplength=200)

advance_psm_var_1 = IntVar()
advance_psm_checkbutton_1 = Checkbutton(advance_psm_frame, indicatoron=0, text="1", width=psm_width, variable=advance_psm_var_1, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_1)
advance_psm_checkbutton_1.grid(
    row=1, column=1, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_1,
        text='Automatic page segmentation with OSD', wraplength=200)

advance_psm_var_2 = IntVar()
advance_psm_checkbutton_2 = Checkbutton(advance_psm_frame, indicatoron=0, text="2", width=psm_width, variable=advance_psm_var_2, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_2)
advance_psm_checkbutton_2.grid(
    row=1, column=2, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_2,
        text='Automatic page segmentation, but no OSD, or OCR', wraplength=200)

advance_psm_var_3 = IntVar()
advance_psm_checkbutton_3 = Checkbutton(advance_psm_frame, indicatoron=0, text="3", width=psm_width, variable=advance_psm_var_3, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_3)
advance_psm_checkbutton_3.grid(
    row=1, column=3, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_3,
        text='Default, Fully automatic page segmentation, but no OSD', wraplength=200)
advance_psm_checkbutton_3.select()

advance_psm_var_4 = IntVar()
advance_psm_checkbutton_4 = Checkbutton(advance_psm_frame, indicatoron=0, text="4", width=psm_width, variable=advance_psm_var_4, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_4)
advance_psm_checkbutton_4.grid(
    row=1, column=4, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_4,
        text='Assume a single column of text of variable sizes', wraplength=200)

advance_psm_var_5 = IntVar()
advance_psm_checkbutton_5 = Checkbutton(advance_psm_frame, indicatoron=0, text="5", width=psm_width, variable=advance_psm_var_5, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_5)
advance_psm_checkbutton_5.grid(
    row=1, column=5, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_5,
        text='Assume a single uniform block of vertically aligned text', wraplength=200)

advance_psm_var_6 = IntVar()
advance_psm_checkbutton_6 = Checkbutton(advance_psm_frame, indicatoron=0, text="6", width=psm_width, variable=advance_psm_var_6, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_6)
advance_psm_checkbutton_6.grid(
    row=1, column=6, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_6,
        text='Assume a single uniform block of text', wraplength=200)

advance_psm_var_7 = IntVar()
advance_psm_checkbutton_7 = Checkbutton(advance_psm_frame, indicatoron=0, text="7", width=psm_width, variable=advance_psm_var_7, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_7)
advance_psm_checkbutton_7.grid(
    row=1, column=7, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_7,
        text='Treat the image as a single text line', wraplength=200)

advance_psm_var_8 = IntVar()
advance_psm_checkbutton_8 = Checkbutton(advance_psm_frame, indicatoron=0, text="8", width=psm_width, variable=advance_psm_var_8, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_8)
advance_psm_checkbutton_8.grid(
    row=1, column=8, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_8,
        text='Treat the image as a single word', wraplength=200)

advance_psm_var_9 = IntVar()
advance_psm_checkbutton_9 = Checkbutton(advance_psm_frame, indicatoron=0, text="9", width=psm_width, variable=advance_psm_var_9, font=("monospace", "9", "bold"),
                                        bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_9)
advance_psm_checkbutton_9.grid(
    row=1, column=9, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_9,
        text='Treat the image as a single word in a circle', wraplength=200)

advance_psm_var_10 = IntVar()
advance_psm_checkbutton_10 = Checkbutton(advance_psm_frame, indicatoron=0, text="10", width=psm_width, variable=advance_psm_var_10, font=("monospace", "9", "bold"),
                                         bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_10)
advance_psm_checkbutton_10.grid(
    row=1, column=10, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_10,
        text='Treat the image as a single character', wraplength=200)

advance_psm_var_11 = IntVar()
advance_psm_checkbutton_11 = Checkbutton(advance_psm_frame, indicatoron=0, text="11", width=psm_width, variable=advance_psm_var_11, font=("monospace", "9", "bold"),
                                         bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_11)
advance_psm_checkbutton_11.grid(
    row=1, column=11, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_11,
        text='Sparse text. Find as much text as possible in no particular order', wraplength=200)

advance_psm_var_12 = IntVar()
advance_psm_checkbutton_12 = Checkbutton(advance_psm_frame, indicatoron=0, text="12", width=psm_width, variable=advance_psm_var_12, font=("monospace", "9", "bold"),
                                         bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_12)
advance_psm_checkbutton_12.grid(
    row=1, column=12, padx=(0, 0), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_12,
        text='Sparse text with OSD', wraplength=200)

advance_psm_var_13 = IntVar()
advance_psm_checkbutton_13 = Checkbutton(advance_psm_frame, indicatoron=0, text="13", width=psm_width, variable=advance_psm_var_13, font=("monospace", "9", "bold"),
                                         bg="#424242", fg="White", selectcolor="#2c4c66", activebackground="#424242", command=advance_psm_toggle_13)
advance_psm_checkbutton_13.grid(
    row=1, column=13, padx=(0, 42), pady=2, sticky=W+E)
Tooltip(advance_psm_checkbutton_13,
        text='Raw line. Treat the image as a single text line', wraplength=200)

# Label
title_label = Label(window, text=title, bg='#515A5A',
                    fg="white", relief="flat", font=("Helvetica", "14", "bold"))
title_label.grid(row=0, column=0, columnspan=2, sticky=W+E, pady=(0, 0))

language_label = Label(output_lang_frame, text="Languages:", font=(
    "Verdana", "10",), fg="white", bg='#424242')
language_label.grid(row=0, column=0)
Tooltip(language_label, text='Available OCR languages', wraplength=200)

input_label = Label(input_upper_frame, text="INPUT", image=input_label_img, width=146, height=22, font=(
    "Verdana", "8",), fg="white", bg='#424242')
input_label.grid(row=0, column=0)

output_label = Label(output_upper_frame, text="OUTPUT", image=output_label_img, width=146, height=22, font=(
    "Verdana", "8",), fg="white", bg='#424242')
output_label.grid(row=0, column=0)

about_label = Label(window, text="Created by Hasitha Suneth", padx=5, bg='#515A5A',
                    fg="white", relief="flat", font=("Comic Sans MS", "8", "italic"))
about_label.grid(row=9, column=0, columnspan=2, sticky=W+E, pady=(10, 0))
about_label.bind('<Button-1>', prep)

advance_oem_label = Label(advance_oem_frame, text="OCR ENGINE MODES", bg='#424242',
                          fg="white", relief="flat", font=("Helvetica", "10", "bold"))
advance_oem_label.grid(row=0, column=0, columnspan=4, sticky=W+E, pady=(5, 0))

advance_psm_label = Label(advance_psm_frame, text="PAGE SEGMENTATION MODES", bg='#424242',
                          fg="white", relief="flat", font=("Helvetica", "10", "bold"))
advance_psm_label.grid(row=0, column=0, columnspan=14, sticky=W+E, pady=(5, 0))


# Entry
input_entry = Entry(input_frame, width=30, borderwidth=3, bg="#515A5A",
                    relief="flat", fg="white", font=("Verdana", "10", "bold"))
input_entry.grid(
    row=0, column=0, sticky=W, padx=(10, 0), pady=(10, 10))

output_entry = Entry(output_frame, width=49, borderwidth=3, bg="#515A5A",
                     relief="flat", fg="white", font=("Verdana", "10", "bold"))
output_entry.grid(
    row=0, column=0, padx=(10, 0), pady=(15, 10))
output_entry.insert(0, output_name_placeholder)
output_entry.bind('<FocusIn>', clear_placeholder)
output_entry.bind('<FocusOut>', restore_placeholder)


# Dropdown
output_options = ['TXT', 'DOC', 'MD', 'HOCR', 'TSV']
output_dropdown = StringVar(output_frame)
output_dropdown.set(output_options[0])
output_menu = OptionMenu(output_frame, output_dropdown, *output_options)
output_menu.config(width=13, bg="#515A5A", font=("Times", "13", "bold"), activebackground="#2c4c66",
                   activeforeground="white", bd=0, highlightthickness=0, fg='white')
output_menu["menu"].config(bg="#515A5A", font=(
    "time", "11", "bold "), fg="White", activebackground="#2c4c66")
output_menu.grid(
    row=0, column=1, padx=(10, 0), pady=(5, 0), sticky=E)
Tooltip(output_menu, text='Available output formats', wraplength=200)

# Start the Tkinter event loop
window.mainloop()
