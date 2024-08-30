import tkinter as tk
import os
import subprocess
import threading
import glob
from os import listdir
from os.path import isfile, join
import ntpath
from tkinter.filedialog import askopenfilename, askdirectory
import psutil
import json
from PIL import ImageTk, Image

file_for_render = ''
location_for_render = ''
location_for_blender = ''
end_frame = 0
start_frame = 0
count = 1
last = 1
last_i = 1
last_img = ''
blenderPid = ''
pause = True
file_for_render_array = []
counter = 0


def process_exists(process_name):
    call = 'TASKLIST', '/FI', f'imagename eq {process_name}'
    output = subprocess.check_output(call).decode()
    last_line = output.strip().split('\r\n')[-1]
    return last_line.lower().startswith(process_name.lower())


def initialize_last_frame():
    global last, last_img, last_i
    files = glob.glob(location_for_render + '/*')
    if files:
        onlyfiles = [f for f in listdir(location_for_render) if isfile(
            join(location_for_render, f))]
        onlyfiles.sort()
        for f in reversed(onlyfiles):
            try:
                last_img = f
                last_i = int(f[0:4]) + 1
                break
            except ValueError:
                continue
    else:
        last_i = 1
    last = str(last_i)


def get_blender_processes():
    blender_processes = []
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'].lower() == 'blender.exe':
            blender_processes.append(proc.info)
    return blender_processes


def start_array():
    global counter, file_for_render, location_for_blender, location_for_render, end_frame, start_frame

    file_for_render = file_for_render_array[counter]['file']
    location_for_blender = file_for_render_array[counter]['blender location']
    location_for_render = file_for_render_array[counter]['render location']
    end_frame = file_for_render_array[counter]['end frame']
    start_frame = file_for_render_array[counter]['start frame']
    initialize_last_frame()
    curent_file_r["text"] = file_for_render
    curent_blender_r["text"] = location_for_blender
    curent_location_r["text"] = location_for_render
    ent_frame_end["text"] = end_frame

    curent_frame_r["text"] = str(int(last) - 1)+' / '+str(end_frame)
    start1()


def start1():
    global count, end_frame, blenderPid, pause, btn_decrease, curent_status_r, start_frame
    if pause:
        pause = False
        btn_decrease.config(text='Pause Render')
        curent_status_r['text'] = 'Rendering...'

        start_frame = ent_frame_start.get()
        # end_frame = ent_frame_end.get()
        if not end_frame:
            return
        if not start_frame:
            initialize_last_frame()
            start_frame = str(last)
        if count == 1:
            count = 2
            output_path = os.path.join(
                os.path.abspath(location_for_render), "####.png")
            cmd = [location_for_blender, '-b', file_for_render, '-s', start_frame, '-e',
                   end_frame, '-o', output_path, '-a', '--', '--cycles-device', 'OPTIX']
            process = subprocess.Popen(cmd)
            blenderPid = process.pid
            print(process.pid)
        count = 1
    else:
        pause = True
        cmd = ['taskkill', '/F', '/PID', str(blenderPid)]
        process = subprocess.Popen(cmd)
        btn_decrease.config(text='Resume Render')
        curent_status_r['text'] = 'Paused'


def add():
    global file_for_render_array
    end_frame = ent_frame_end.get()
    if (file_for_render != '' and location_for_render != '' and location_for_blender != '' and end_frame != ''):

        file_for_render_array.append(
            {'file': file_for_render, 'render location': location_for_render, 'blender location': location_for_blender, 'end frame': end_frame, 'start frame': start_frame})
        print(end_frame)
        clear_all_inside_frame()
        fill_table_frame()


def load_image():
    global img_frame
    try:
        if last_img != '':
            output_path = os.path.join(
                os.path.abspath(location_for_render), last_img)
            img = Image.open(output_path)
            img.thumbnail((400, 400))
            new_img_tk = ImageTk.PhotoImage(img)
            img_frame.config(image=new_img_tk)
            img_frame.image = new_img_tk
    except Exception as e:
        print(f"Error opening image: {e}")


def decrease():
    global last, img_frame, btn_decrease, pause, counter
    curent_frame_r["text"] = str(int(last) - 1)+' / '+str(end_frame)
    load_image()
    get_blender_processes()
    count = 0
    if process_exists('blender.exe'):
        for f in get_blender_processes():
            if f['pid'] == blenderPid:
                count += 1
        if count == 0:
            if not pause:
                start1()
        else:
            initialize_last_frame()
            curent_frame_r["text"] = str(int(last) - 1)+' / '+str(end_frame)
    else:
        if location_for_render != '':
            initialize_last_frame()

        if end_frame == 0:
            print('Blender has not started')
        elif int(int(last)-1) < int(end_frame) and not pause:
            start1()
        elif int(int(last)-1) == int(end_frame):

            if (len(file_for_render_array) != 0):
                file_for_render_array.pop(0)
                clear_all_inside_frame()
                fill_table_frame()

            print('finished')
            curent_frame_r["text"] = str(int(last)-1)+' / '+str(end_frame)
            curent_status_r['text'] = 'Finished'
            pause = True

            btn_decrease.config(text='Start Render')

            if (len(file_for_render_array) != 0):

                # counter = counter+1
                start_array()


def clear_all_inside_frame():
    # Iterate through every widget inside the frame
    for widget in frm_table.winfo_children():
        widget.destroy()


def delete_row(i):
    # Iterate through every widget inside the frame
    print(i.grid_info()['row']-1)
    file_for_render_array.pop(i.grid_info()['row']-1)
    clear_all_inside_frame()
    fill_table_frame()


def fill_table_frame():
    lbl_text_rf = tk.Label(
        master=frm_table, text="Render file", pady=5, bg="white")
    lbl_text_rf.grid(row=0, column=0, sticky="e", padx=5)

    lbl_text_of = tk.Label(
        master=frm_table, text="Output Folder", pady=5, bg="white")
    lbl_text_of.grid(row=0, column=1, sticky="e", padx=5)

    lbl_text_fe = tk.Label(
        master=frm_table, text="Frame End", pady=5, bg="white")
    lbl_text_fe.grid(row=0, column=2, sticky="e", padx=5)
    i = 0
    for f in file_for_render_array:

        lbl_text_rf_a = tk.Label(
            master=frm_table, text=f['file'], pady=5, bg="white")
        lbl_text_rf_a.grid(row=i+1, column=0, sticky="e", padx=5)

        lbl_text_of_a = tk.Label(
            master=frm_table, text=f['render location'], pady=5, bg="white")
        lbl_text_of_a.grid(row=i+1, column=1, sticky="e", padx=5)

        lbl_text_fe_a = tk.Label(
            master=frm_table, text=f['end frame'], pady=5, bg="white")
        lbl_text_fe_a.grid(row=i+1, column=2, sticky="e", padx=5)
        m = i
        btn_delete = tk.Button(frm_table, text="X",
                               bg="#b6bab7", border=0)
        btn_delete.configure(
            command=lambda button=btn_delete: delete_row(button))
        btn_delete.grid(row=i+1, column=3, sticky="ew", padx=5, pady=2)
        i += 1


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()


def open_file():
    global file_for_render
    filepath = askopenfilename(filetypes=[("All Files", "*.*")])
    if not filepath:
        return
    file_for_render = filepath

    curent_file_r["text"] = filepath


def save_file():
    global location_for_render
    folder_path = askdirectory()
    if not folder_path:
        return
    location_for_render = folder_path
    curent_location_r["text"] = folder_path
    initialize_last_frame()


def blender_file():
    global location_for_blender, curent_blender_r
    filepath = askopenfilename(filetypes=[("All Files", "*.*")])
    if not filepath:
        return
    location_for_blender = filepath
    curent_blender_r["text"] = filepath


set_interval(decrease, 3)

window = tk.Tk()
window.title("Renderer")
window.geometry('500x600')
top = tk.Toplevel()
top.title('Render list')
top.geometry('400x400')

frm_table = tk.Frame(top, height=100, width=500, bd=3, bg="white")
frm_table.pack_propagate(False)
frm_table.place(x=0, y=0, width=400, height=400)

lbl_text = tk.Label(
    master=frm_table, text="Render file", pady=5, bg="white")
lbl_text.grid(row=0, column=0, sticky="e", padx=5)

lbl_text1 = tk.Label(
    master=frm_table, text="Output Folder", pady=5, bg="white")
lbl_text1.grid(row=0, column=1, sticky="e", padx=5)

lbl_text2 = tk.Label(
    master=frm_table, text="Frame End", pady=5, bg="white")
lbl_text2.grid(row=0, column=2, sticky="e", padx=5)


frm_buttons = tk.Frame(window, height=100, width=500, bd=3, bg="white")
frm_buttons.pack_propagate(False)
frm_buttons.place(x=0, y=0, width=500, height=100)

frm_inputs = tk.Frame(window, height=100, width=500, bd=3, bg="white")
frm_inputs.pack_propagate(False)
frm_inputs.place(x=0, y=100, width=500, height=100)

frm_image = tk.Frame(window, height=400, width=500, bd=3, bg="white")
frm_image.pack_propagate(False)
frm_image.place(x=0, y=160, width=500, height=400)

frm_frame = tk.Frame(window, height=50, width=500, bd=3, bg="white")
frm_frame.pack_propagate(False)
frm_frame.place(x=0, y=560, width=500, height=50)

btn_open = tk.Button(frm_buttons, text="Open File",
                     command=open_file, bg="#b6bab7", border=0)
btn_save = tk.Button(frm_buttons, text="Output Folder",
                     command=save_file, bg="#b6bab7", border=0)
btn_blend = tk.Button(
    frm_buttons, text="Blender Location", command=blender_file, bg="#b6bab7", border=0)
btn_decrease = tk.Button(
    frm_inputs, pady=5, text="Start Render", command=start_array, bg="#b6bab7", border=0)

btn_add = tk.Button(
    frm_inputs, pady=5, text="Add", command=add, bg="#b6bab7", border=0)

lbl_frame_start = tk.Label(
    master=frm_inputs, text="Frame start:", pady=5, bg="white")
ent_frame_start = tk.Entry(master=frm_inputs, width=10, bg="#b6bab7", border=0)
curent_frame_r = tk.Label(master=frm_frame, text="", bg="white")
curent_frame = tk.Label(master=frm_frame, text="Frame:", bg="white")
curent_status_r = tk.Label(master=frm_frame, text="Not started", bg="white")
curent_status = tk.Label(master=frm_frame, text="Status:", bg="white")
curent_file_r = tk.Label(master=frm_buttons, text="-", bg="white")
curent_blender_r = tk.Label(master=frm_buttons, text="-", bg="white")
curent_location_r = tk.Label(master=frm_buttons, text="-", bg="white")

curent_frame_r["text"] = str(int(last) - 1)+' / '+str(end_frame)

lbl_frame_end = tk.Label(
    master=frm_inputs, text="Frame end:", pady=5, bg="white")
ent_frame_end = tk.Entry(master=frm_inputs, width=10, bg="#b6bab7", border=0)

img = Image.open("1160358.png")
img.thumbnail((400, 400))
img_tk = ImageTk.PhotoImage(img)
img_frame = tk.Label(master=frm_image, image=img_tk)
img_frame.pack(side="bottom", fill="both", expand="no")

lbl_frame_start.grid(row=0, column=0, sticky="e", padx=5)
ent_frame_start.grid(row=0, column=1, padx=5)
lbl_frame_end.grid(row=0, column=2, sticky="e", padx=5)
ent_frame_end.grid(row=0, column=3, padx=5)
curent_frame.grid(row=0, column=2, sticky="e", padx=(250, 0))
curent_frame_r.grid(row=0, column=3, sticky="ns")

curent_status.grid(row=0, column=0, sticky="e", padx=5)
curent_status_r.grid(row=0, column=1, sticky="ns")

curent_file_r.grid(row=0, column=1, sticky="ns")
curent_location_r.grid(row=1, column=1, sticky="ns")
curent_blender_r.grid(row=2, column=1, sticky="ns")

btn_decrease.grid(row=0, column=4, sticky="ew", padx=20, pady=5)
btn_add.grid(row=0, column=5, sticky="ew", padx=20, pady=5)
btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
btn_blend.grid(row=2, column=0, sticky="ew", padx=5, pady=2)

window.mainloop()
