import pandas as pd
import os
import openpyxl
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as font
import statistics

# GUI window settings

gui = tk.Tk()
gui.geometry('320x280')
gui.title("pHluorin Imaging Analysis")

#calculation of a rolling average in the window of n values
def running_mean(a, n) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

# get an average of a list
def average(list):
    return (sum(list) / len(list))

# gets dF/F0 columns of each excel sheet
def get_data(path):
    # ask for bleach correction
    yes_or_no = int(check.get())

    if yes_or_no == 1:
        print("Bleach correction started.")
    else:
        print("No Bleach correction.")

    filter_ask = int(check_filter.get())
    if filter_ask == 1:
        print("Animals with no response will be filtered out.")
    else:
        print("No filter applied.")

    # get pulsestart:
    pulsestart = int(pulse_start.get())
    pulselength = int(pulse_length.get())

    # writes list of filepaths
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.xlsx' in file:
                files.append(os.path.join(r, file))
    print(files)

    dF_columns = []

    dF_columns_min_max = []
    # opens each excel file
    for f in files:
        # opens each sheet in each excel file
        wb = openpyxl.load_workbook(f)
        res = len(wb.sheetnames)
        print("this is file: " + f)
        for j in range(res):
            data1 = pd.read_excel(f, sheet_name=j)
            print("\nThis is Sheet " + str(j + 1))
            column1 = data1["Unnamed: 1"].tolist()
            column3 = data1["Unnamed: 3"].tolist()

            # #bleach correct both columns
            frames = np.arange(len(column1))
            model1 = np.polyfit(frames, column1, 1)
            bleach_coeff1 = model1[0]

            print("Row 1 bleach coefficient :" + str(bleach_coeff1))
            bleach_corrected1 = []
            i = 0
            mean_start1 = average(column1[0:int(framerate.get())])
            print("Mean start: " + str(mean_start1))
            mean_end1 = average(column1[-int(framerate.get()):-1])
            print("Mean end: " + str(mean_end1))
            if mean_end1 / mean_start1 < 0.85:
                print ("Bleach correction.")

                for value1 in column1:
                    corr_value = value1 - (bleach_coeff1*i)
                    bleach_corrected1.append(corr_value)
                    i = i + 1
            else:
                print ("No bleach correction")
                for value1 in column1:
                    bleach_corrected1.append(value1)
                    i = i + 1
            print (bleach_corrected1)

            model2 = np.polyfit(frames, column3, 1)
            bleach_coeff2 = model2[0]
            print("Row 3 bleach coefficient :" + str(bleach_coeff2))

            bleach_corrected2 = []
            j = 0
            if mean_end1 / mean_start1 < 0.85:
                print ("Bleach correction.")
                # popt, pcov = curve_fit(func, frames, column3, maxfev=10000)
                # plt.plot(frames, func(frames, *popt))
                # plt.plot(frames, column3)

                for value2 in column3:
                    corr_value = value2 - (bleach_coeff2*j)
                    bleach_corrected2.append(corr_value)
                    j = j + 1
            else:
                for value2 in column3:
                    bleach_corrected2.append(value2)
                    j = j + 1
            print(bleach_corrected2)
            # plt.plot(frames, bleach_corrected1)
            # plt.plot(frames, bleach_corrected2)
            # plt.xlabel(f)
            # plt.legend()
            # plt.show()
            background_corrected = []
            if yes_or_no == 1:
                for k in range(0, len(bleach_corrected1)):
                    substract_background = bleach_corrected1[k] - bleach_corrected2[k]
                    background_corrected.append(substract_background)
            else:
                for l in range(0, len(column1)):
                    substract_background = column1[l] - column3[l]
                    background_corrected.append(substract_background)
            dF_column = []
            list_tillpulsestart = background_corrected[:pulsestart - 1]
            average_before_pulse = average(list_tillpulsestart)
            for value in background_corrected:
                dF = (value - average_before_pulse) / average_before_pulse
                dF_column.append(dF)

            # get maximum value in background_corrected column
            maximum = max(background_corrected)
            print("This is the max:" + str(maximum))
            dF_column_min_max = []
            for value in background_corrected:
                dF_min_max = (value - average_before_pulse) / (maximum - average_before_pulse)
                dF_column_min_max.append(dF_min_max)

            #filter non-responders with an average signal during the pulse
            SD_dF = statistics.stdev(background_corrected[:pulsestart])
            filter_edge = average(background_corrected[:pulsestart])+(3*SD_dF)
            print("This is the SD until pulse: " + str(SD_dF))
            print("Average of Background corrected till start: " + str(average(background_corrected[:pulsestart])))
            print("Filtered at: " + str(filter_edge))

            #calculate running mean of 1s and find maximum during pulse
            moving_average = running_mean(background_corrected, int(framerate.get()))
            maximum_pulse = max(moving_average[pulsestart:pulsestart+pulselength])
            print ("Maximum during pulse: " + str(maximum_pulse))
            if filter_ask == 1:
                if maximum_pulse > filter_edge and maximum_pulse > 0:
                    dF_columns.append(dF_column)
                    dF_columns_min_max.append(dF_column_min_max)
                    print("This animal shows a strong response\n")
            else:
                dF_columns.append(dF_column)
                dF_columns_min_max.append(dF_column_min_max)
    #plt.show()
    return (dF_columns, dF_columns_min_max, 1 / int(framerate.get()))


def write_data():
    # get source folder to get data
    sourcepath = source_path.get()
    list_subdirectories = os.listdir(sourcepath)
    print(list_subdirectories)
    for subdirectory in list_subdirectories:
        column_list = get_data(sourcepath + "/" + subdirectory)
        framerate = column_list[2]
        df = pd.DataFrame(column_list[0])
        df = pd.DataFrame.transpose(df)
        time = np.arange(framerate, framerate * len(df), framerate)
        timedf = pd.DataFrame(time)
        mean = df.mean(axis=1, skipna=True)
        sem = df.sem(axis=1, skipna=True)
        n = df.count(axis=1)
        df_final = pd.concat([df, timedf, mean, sem, n], axis=1)
        column_names = [str(x) for x in range(1, len(column_list[0]) + 1)]
        column_names.append("time[s]")
        column_names.append("Mean")
        column_names.append("SEM")
        column_names.append("n")
        df_final.columns = [column_names]
        print(df_final)

        # enter output path and sheetname
        with pd.ExcelWriter(sourcepath + "/" + subdirectory + "_results.xlsx") as writer:
            df_final.to_excel(writer, sheet_name=subdirectory, engine='openpyxl')

        # write min_max normalized columns
        df = pd.DataFrame(column_list[1])
        df = pd.DataFrame.transpose(df)
        time = np.arange(framerate, framerate * len(df), framerate)
        timedf = pd.DataFrame(time)
        mean = df.mean(axis=1, skipna=True)
        sem = df.sem(axis=1, skipna=True)
        n = df.count(axis=1)
        df_final = pd.concat([df, timedf, mean, sem, n], axis=1)
        column_names = [str(x) for x in range(1, len(column_list[1]) + 1)]
        column_names.append("time[s]")
        column_names.append("Mean")
        column_names.append("SEM")
        column_names.append("n")
        df_final.columns = [column_names]
        print(df_final)
        # enter output path and sheetname
        with pd.ExcelWriter(sourcepath + "/" + subdirectory + "_results_min_max.xlsx") as writer:
            df_final.to_excel(writer, sheet_name=subdirectory, engine='openpyxl')

def getsource_path():
    source_selected = filedialog.askdirectory(title="Select directory")
    source_path.set(source_selected)

def close():
    gui.destroy()


# GUI setup

# GUI font styles
myFont = font.Font(family='Cambria', size=10, weight="bold")
titleFont = font.Font(family='Cambria', size=15, weight="bold")
fileFont = font.Font(size=9, weight="bold")

# Title
gui_title = tk.Label(gui, text="pHluorin Imaging Analysis", font=titleFont)
gui_title.grid(row=1, column=1, pady=15, sticky='w', padx=17)

border_label = tk.Label(gui, text="   ")
border_label.grid(row=2, column=0, sticky="w")

# Path selection
source_path = tk.StringVar()
path_label = tk.Label(gui, text="Path")
path_label.grid(row=2, column=1, sticky="w")
path_entry = tk.Entry(gui, textvariable=source_path, width=28)
path_entry.grid(row=2, column=1, sticky='w', padx=30)
btn_path_entry = ttk.Button(gui, text="Browse", command=getsource_path)
btn_path_entry.grid(row=2, column=1, sticky='w', padx=210)

# Pulse start
pulse_start = tk.StringVar()

pulse_label = tk.Label(gui, text="Pulse start:             (frames)")
pulse_label.grid(row=3, column=1, sticky="w")
pulse_entry = tk.Entry(gui, textvariable=pulse_start, width=4)
pulse_entry.grid(row=3, column=1, pady=5, padx=72, sticky='w')

# Pulse length
pulse_length = tk.StringVar()
length_label = tk.Label(gui, text="Pulse length:          (frames)")
length_label.grid(row=4, column=1, sticky="w")
length_entry = tk.Entry(gui, textvariable=pulse_length, width=4)
length_entry.grid(row=4, column=1, pady=5, padx=72, sticky='w')

# Framerate
framerate = tk.StringVar()
framerate_label = tk.Label(gui, text="Framerate:              (fps)")
framerate_label.grid(row=5, column=1, sticky="w")
framerate_entry = tk.Entry(gui, textvariable=framerate, width=4)
framerate_entry.grid(row=5, column=1, pady=5, padx=72, sticky='w')

# Bleach correction
check = tk.IntVar()
bleach_check = tk.Checkbutton(gui, text="Correct for bleaching?", variable=check)
bleach_check.grid(row=6, column=1, sticky='w')

# Bleach correction
check_filter = tk.IntVar()
check_filter_button = tk.Checkbutton(gui, text="Filter?", variable=check_filter)
check_filter_button.grid(row=7, column=1, sticky='w')

# Start Button
btn_start = tk.Button(gui, text="Start",
                      relief='groove', activebackground='#99ccff',
                      command=write_data)
btn_start.grid(row=8, column=1, padx=90, sticky="w")

# GUI Close Window Button
btn_close = tk.Button(gui, text="Close",
                      bg='#ff6666', relief='groove',
                      command=close)
btn_close.grid(row=8, column=1, padx=150, sticky="w")

# GUI window loop
gui.mainloop()