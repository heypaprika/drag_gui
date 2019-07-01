import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import Canvas
from PIL import ImageTk, Image
from xml.etree.ElementTree import parse
from pathlib import Path
from lxml import etree
import os.path
import os
from shutil import copyfile
import argparse




win = tk.Tk()
win.title("Python GUI")
w, h = win.winfo_screenwidth(), win.winfo_screenheight()
win.geometry("%dx%d+0+0" % (w, h))
win.resizable(True, True)


def _quit():
    win.quit()
    win.destroy()
    exit()

############## Menu start ##############


menu_bar = Menu(win)
win.config(menu=menu_bar)

file_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New")
file_menu.add_separator()
file_menu.add_command(label="Exit", command=_quit)

help_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About")


############## Menu end ##############


############## Tap start ##############

# 탭바
tabControl = ttk.Notebook(win)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text='Drag')
# tab2 = ttk.Frame(tabControl)
# tabControl.add(tab2, text='Tab 2')
tabControl.pack(expand=1, fill="both")


############## Tap end ##############


############## init start ##############

parser = argparse.ArgumentParser()
parser.add_argument("-p","--dataset_path", default="2m")
parser.add_argument("-n","--number", default=0, help="first number of image")
parser.add_argument("-y","--yolo", default="yolo", help="yolo data result path")
parser.add_argument("-r","--retrieval", default="retrieval", help="retrieval data result path")
parser.add_argument("-e","--extension", default="png")
args = parser.parse_args()

dataset_root = os.path.join(".", args.dataset_path)

if os.path.exists(dataset_root):
    # yolo와 retrieval 만들어 주기.
    yolo_path = os.path.join(dataset_root,args.yolo)
    if not os.path.exists(yolo_path):
        os.mkdir(yolo_path)

    retrieval_path = os.path.join(dataset_root,args.retrieval)
    if not os.path.exists(retrieval_path):
        os.mkdir(retrieval_path)

else:
    print("dataset_path is not exist")
    _quit()
###################################
# 1)디렉토리 지정

############################
# 2)이름 앞 부분
header_name = ''
# 3)시작 번호지정
first_file = args.number
Image_Num = first_file
Image_Count = 0
Image_Temp = 0
# 4)이름 뒷 부분
footer_name = '.'+args.extension
############################

# 다음 파일 인덱스 탐색 최대치 지정
file_width = 1000

# 색깔 지정
rect_color = "yellow"
cir_color = "red"

x = y = 0
rect = 0
box = 0
drag_file_num = 1
count_box = 0

start_x = None
start_y = None
center_x = None
center_y = None
curX = curY = 0
window = None

l = ''
boundlist = []





############## init end ##############


############## Grid start ##############

# mighty = ttk.LabelFrame(tab2, text=' Mighty Python ')
# mighty.grid(column=0,row=0,padx=8,pady=4)

mighty2 = ttk.LabelFrame(tab1, text=' Detail ')
mighty2.grid(column=0, row=0)

# 크기를 키우려면 여기를 고쳐서 이용(단, 기존의 좌표 체계와 달라진다. 다른 부분도 수정 필)
image_file_path = dataset_root
file_name = header_name + str(Image_Num) + footer_name
image = Image.open(os.path.join(image_file_path,file_name))
width, height = image.size
# print(width, height)
png = ImageTk.PhotoImage(image)
canvas = Canvas(mighty2, width=1200, height=1200)
canvas.pack(side="bottom", expand='yes', fill='x')
hicanvas = canvas.create_image(0, 0, image=png, anchor='nw')
canvas.grid(column=0, row=0, rowspan=15)


first_file_name = " filename = "+file_name
ttk.Label(mighty2, width="30", text=first_file_name).grid(column=1, row=0, sticky='w')

write_file_num = tk.StringVar()
write_file_num_entered = ttk.Entry(mighty2, width=17, textvariable=write_file_num)
write_file_num_entered.insert(0, "write file number(ex:3)")
write_file_num_entered.grid(column=2, row=0, sticky=tk.W)

select_obj_button = ttk.Button(mighty2, text=" Select Object(f1) ")
select_obj_button.grid(column=1, row=1)

done_button = ttk.Button(mighty2, text=" Done(f3) ")
done_button.grid(column=1, row=2)

status_label = ttk.Label(mighty2, text="")
status_label.grid(column=1, row=3, columnspan=2)

############## Grid end ##############


############## write file num start ##############

def on_entry_click(_):
    """function that gets called whenever entry is clicked"""
    if write_file_num_entered.get() == 'write file number(ex:3)':
        write_file_num_entered.delete(0, "end")  # delete all the text in the entry
        write_file_num_entered.insert(0, '')  # Insert blank for user input


def on_focusout(_):
    if write_file_num_entered.get() == '':
        write_file_num_entered.insert(0, 'write file number(ex:3)')


write_file_num_entered.bind('<FocusIn>', on_entry_click)
write_file_num_entered.bind('<FocusOut>', on_focusout)


############## write file num end ##############


############## select_object start ##############

# 마우스 드래그 콜백 함수
def on_button_press(event):
    global x, y, rect, start_x, start_y
    # save mouse drag start position
    start_x = event.x
    start_y = event.y

    # create rectangle if not yet exist
    # if not self.rect:
    rect = canvas.create_rectangle(x, y, 1, 1, outline=rect_color, width=4)


def on_move_press(event):
    global x, y, rect, start_x, start_y, curX, curY
    curX, curY = event.x, event.y
    #print(rect,start_x,start_y,curX,curY)
    # expand rectangle as you drag the mouse
    canvas.coords(rect, start_x, start_y, curX, curY)


def on_button_press_on_new(event):
    global start_x, start_y, center_x, center_y, window
    center_x = event.x/3 + start_x
    center_y = event.y/3 + start_y


def on_button_release_on_new(_):
    global window
    window.quit()
    window.destroy()


def on_button_release(_):
    global l, x, y, start_x, start_y, curX, curY, box, drag_file_num, image, boundlist
    width, height = image.size
    print(image.size)
    # box = len(l)+1
    object_width = curX - start_x
    object_height = curY - start_y
    center_x = start_x + object_width/2
    center_y = start_y + object_height/2



    # for text file
    l += '0 '
    l += str(center_x/width)[:8] +' '
    l += str(center_y/height)[:8] +' '
    l += str(object_width/width)[:8] +' '
    l += str(object_height/height)[:8]+'\n'

    boundlist.append([start_x,start_y,curX,curY])
    # l.append([0, center_x/width, center_y/height, object_width/width, object_height/height])
    # print(l)

    drag_file_num += 1


def select_object():
    # 마우스 드래그 함수
    canvas.config(cursor='crosshair')
    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move_press)
    canvas.bind("<ButtonRelease-1>", on_button_release)


select_obj_button.configure(command=select_object)


############## select_object end ##############


ind = 1

############## Done start ##############

import cv2
import numpy as np
# XML로 저장하고 다음으로 넘어가는 함수
def done():
    global l, Image_Num, ind, Image_Count, Image_Temp, box, image, boundlist
    canvas.config(cursor='arrow')
    canvas.unbind("<ButtonPress-1>")
    canvas.unbind("<B1-Motion>")
    canvas.unbind("<ButtonRelease-1>")

    print(l)
    with open(os.path.join(image_file_path,args.yolo,str(Image_Num) + '.txt'), 'w') as new_days:
        new_days.write(l)

    l = ''
    file_name = str(Image_Num)+footer_name
    os.rename(os.path.join(dataset_root, file_name),os.path.join(dataset_root,args.yolo,file_name))
    image_numpy = np.array(image)
    for i, bound in enumerate(boundlist):
        cropped_img = image_numpy[ int(bound[1]):int(bound[3]), int(bound[0]):int(bound[2])]
        cv2.imwrite(os.path.join(dataset_root,args.retrieval,str(Image_Num)+"_"+str(i)+'.jpg'),cv2.cvtColor(cropped_img, cv2.COLOR_RGB2BGR))

    boundlist = []

    ind = 1
    # total_obj_label.config(text=tot_state + str(len(l)))

    st_Image_Num = str(Image_Num)

    if write_file_num_entered.get() == 'write file number(ex:3)':
        Image_Count = 0
        while True:
            Image_Num += 1
            Image_Count += 1
            _file = os.path.join(image_file_path,str(Image_Num)+footer_name)
            # print(_file)

            if os.path.isfile(_file):
                image = Image.open(_file)
                # print(image.size)

                gif1 = ImageTk.PhotoImage(image)
                next_canvas = canvas.create_image(0, 0, image=gif1, anchor='nw')
                ttk.Label(mighty2, width="30", text=" Filename = " +header_name+str(Image_Num)+footer_name).grid(column=1, row=0, sticky='w')
                canvas.itemconfig(next_canvas, image=_file)
                break
            elif Image_Count == file_width:
                print(st_Image_Num+"에서 종료: 파일이 "+str(file_width)+"개 범위 안에 없습니다.")
                _quit()
                break
    elif os.path.isfile(dataset_root+'%d_c.png' % int(write_file_num_entered.get())):
        Image_Num = int(write_file_num_entered.get())
        # init_button.focus()
        _file = os.path.join(image_file_path,str(Image_Num)+footer_name)
        write_file_num_entered.config(text='write file number(ex:3)')
        image = Image.open(_file)
        gif1 = ImageTk.PhotoImage(image)
        next_canvas = canvas.create_image(0, 0, image=gif1, anchor='nw')
        ttk.Label(mighty2, width="30", text=" Filename = " +header_name+str(Image_Num)+footer_name).grid(column=1, row=0, sticky='w')
        canvas.itemconfig(next_canvas, image=_file)
    else:
        write_file_num_entered.config(text='write file number(ex:3)')
        status_label.config(text='파일이 없습니다')


done_button.configure(command=done)


############## Done end ##############


############## Shortcut start ##############


def select_object_sc(_):
    select_object()


def done_sc(_):
    done()


win.bind('<Key-F1>', select_object_sc)
win.bind('<Key-F3>', done_sc)

############## Shortcut end ##############

win.mainloop()
