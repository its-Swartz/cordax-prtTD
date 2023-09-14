import tkinter as tk
import PIL
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os, os.path, sys, datetime
import time as tm

from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

# Establish tkinter window
window = tk.Tk()
window.title("PRT Time Drive App - v1.3")
window.geometry("350x460")

# Grab working directory and define path as "none" otherwise tkinter throws a fit
initialDir = os.getcwd()


def ImportShockVibe():
    global file_path_sv
    # Grab Shock/Vibe file based on user input
    file_path_sv = filedialog.askopenfilename(initialdir=initialDir, title='Please select a Shock/Vibe File (*.csv)')
    # Chop the rest of the directory off except for the filename itself
    filename = os.path.basename(os.path.normpath(file_path_sv))
    # Redefine the text below the import button to reflect newly imported file
    text_SV.config(text = filename)
    print(file_path_sv)
    return

def PlotData():
    # Turn imported CSV into Pandas dataframe
    try:    
        df = pd.read_csv(file_path_sv, sep=r'\s*,\s*', engine='python', skiprows = 8)
    except:
        tk.messagebox.showerror("Error", "Unable to import " + os.path.basename(os.path.normpath(file_path_sv)) + "\nShock/Vibe file needs to be from new firmware.")
        return

    # Clean up the data
    df.drop(df.columns[[-1,]], axis=1, inplace=True)
    df.dropna(inplace=True)

    # Debugging
    print(df)

    df = df[df['Date-Time'] != "INVALID (4294967295)"]

    # Debugging
    print(df)

    # Turn text into datetime for later indexing
    try:
        df['Date-Time'] = pd.to_datetime(df['Date-Time'], format = "%Y/%m/%d %H:%M:%S")
    except:
        tk.messagebox.showerror("Error", "Shock/Vibe Date-Time range is too large\nAll NaN values were not removed\n\nAll rows containing 'INVALID (4294967295)' need to be removed manually")
        return

    # Grab start dates and times from tkinter text entries
    start_date = start_date_entry.get()
    start_time = start_time_entry.get()
    end_date = end_date_entry.get()
    end_time = end_time_entry.get()

    # Put the start and end strings together and convert to datetime
    try:
        start_datetime = datetime.datetime.strptime(start_date + " " + start_time, "%Y/%m/%d %H:%M:%S")
    except:
        tk.messagebox.showerror("Error", "Improper Date/Time formatting")
        return
    try:
        end_datetime = datetime.datetime.strptime(end_date + " " + end_time, "%Y/%m/%d %H:%M:%S")
    except:
        tk.messagebox.showerror("Error", "Improper Date/Time formatting")
        return

    # Create a mask for the imported dataframe between the start and end times
    mask = (df["Date-Time"] >= start_datetime) & (df["Date-Time"] <= end_datetime)
    time_chosen_df = df.loc[mask].reset_index(drop=True)

    if len(time_chosen_df.index) < 20:
        tk.messagebox.showerror("Error", "One of the following issues has occurred:\n - Incorrect/Invalid Date-Time range\n - Incorrect PRT firmware version")

    time = time_chosen_df['Date-Time'].values
    xyvibe = time_chosen_df['XYVibLvl'].values
    xy_mask = np.isfinite(xyvibe)
    zvib = time_chosen_df['ZVibLvl'].values
    z_mask = np.isfinite(zvib)

    XYPkAccl = time_chosen_df['XYPkAccl'].values/10
    xy_mask_accl = np.isfinite(XYPkAccl)
    ZPkAccl = time_chosen_df['ZPkAccl'].values/10
    z_mask_accl = np.isfinite(ZPkAccl)

    outFilename = os.path.dirname(file_path_sv) + "/PRT-TimeDrive-Dataset.txt"
    outFile = open(outFilename, "w")
    print("TIME\tXYVIBE\tZVIBE\tXYACCL\tZACCL", file = outFile)
    print("S\tg\tg\tg\tg", file = outFile)
    outFile.close()

    outFile = open(outFilename, "a")

    for i in range(time_chosen_df['Date-Time'].size - 1):
        print(str(30.00*i) + '\t' + str(time_chosen_df.iloc[i+1]['XYVibLvl'])\
        + '\t' + str(time_chosen_df.iloc[i+1]['ZVibLvl']) + '\t' + str(time_chosen_df.iloc[i+1]['XYPkAccl'])\
        + '\t' + str(time_chosen_df.iloc[i+1]['ZPkAccl']), file = outFile)
    
    outFile.close()

    lines = []

    with open(outFilename, 'r') as fp:
        lines = fp.readlines()

    with open(outFilename, 'w') as fp:
        for number, line in enumerate(lines):
            if number not in [2]:
                fp.write(line)

    tk.messagebox.showinfo("PRT Time Drive", "Dataset for GeoBase created in same folder as Shock/Vibe file.")

    plt.subplot(2,1,1)
    plt.title('PRT Time Drive')
    plt.ylabel('Vibration Shock (G)')
    plt.plot(time[xy_mask], xyvibe[xy_mask], label='XY-Vibe', color='red')
    plt.plot(time[z_mask], zvib[z_mask], label='Z-Vibe', color='black')
    plt.grid(True)
    plt.legend()

    plt.subplot(2,1,2)
    plt.ylabel('Accelerometer Shock (Relative)')
    plt.plot(time[xy_mask_accl], XYPkAccl[xy_mask_accl], label='XY-Shock', color='blue')
    plt.plot(time[z_mask_accl], ZPkAccl[z_mask_accl], label='Z-Shock', color='green')
    plt.xlabel('Time')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_tick_params(rotation=75)
    plt.gcf().autofmt_xdate()
    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    plt.show()
    
    return
    

# Logo Image
from prt-logo import *
pic=imageString
render = tk.PhotoImage(data=pic)
logo_label = tk.Label(image=render)

# Text Headers
text_title = tk.Label(window, text="PRT Time Drive Application", font=('Default', 14, 'bold'))
text_SV = tk.Label(window, text="Shock/Vibe File")
text_startdate = tk.Label(window, text="Start Date", font=('Default', 10, 'bold'))
text_starttime = tk.Label(window, text="Start Time", font=('Default', 10, 'bold'))
text_enddate = tk.Label(window, text="End Date", font=('Default', 10, 'bold'))
text_endtime = tk.Label(window, text="End Time", font=('Default', 10, 'bold'))
text_format = tk.Label(window, text="Date/Time format is\n YYYY/MM/DD and HH:MM:SS")

# Import Buttons
sv_button = tk.Button(window, text='Import Shock/Vibe', command=ImportShockVibe)

# Date-Times
start_date_entry = tk.Entry(window)
start_time_entry = tk.Entry(window)
end_date_entry = tk.Entry(window)
end_time_entry = tk.Entry(window)

# Submit button
process_button = tk.Button(window, text='Graph Shock/Vibe', font=('Default', 10, 'bold'), command=PlotData)

# Pack the widgets
logo_label.pack(pady=(15,0))
text_title.pack(pady=(5,0))

# Display CSV path
sv_button.pack(pady=(10,0))
text_SV.pack()

# Data Entry
text_startdate.pack(pady=(15,0))
start_date_entry.pack()
text_starttime.pack(pady=(5,0))
start_time_entry.pack()
text_enddate.pack(pady=(5,0))
end_date_entry.pack()
text_endtime.pack(pady=(5,0))
end_time_entry.pack()
text_format.pack(pady=(5,0))

process_button.pack(pady=(25,0))

window.mainloop()
