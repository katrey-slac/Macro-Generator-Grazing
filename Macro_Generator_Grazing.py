import tkinter
import os
import tkinter as tk
from tkinter import Toplevel, ttk, filedialog, messagebox
from pathlib import Path

#message box to confirm GUI closure
def on_closing():
    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        root.destroy()

# Store folder path in variable
def select_folder(folder_var):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)


# Ensures the scrollable area (in the home directory box) is updated after content is added
def update_scrollregion(event=None):
    canvas.config(scrollregion=canvas.bbox("all"))


# Update the label with the variable's value
def update_label(var_value, label_var):
    label_var.set(var_value.get())



def show_success_popup(directory, macro_name):
    popup = tk.Toplevel(root)
    popup.title("Success")
    popup.geometry("500x175")
    popup.resizable(False, False)

    # Message Label
    tk.Label(popup, text="File saved successfully!\nRun this in SPEC:", font=("Arial", 10)).pack(pady=(10, 5))

    path = Path(directory)
    print(path)
    new_path = Path(*path.parts[2:]).as_posix()

    # Copyable Text
    cmd_text = f"qdo ./{new_path}/{macro_name}.txt"

    # Frame to contain the Text and Scrollbar
    text_frame = tk.Frame(popup)
    text_frame.pack(pady=(0, 10))

    # Horizontal scrollbar
    x_scroll = tk.Scrollbar(text_frame, orient="horizontal")
    x_scroll.pack(side="bottom", fill="x")

    # Text box with scrollbar
    text_box = tk.Text(text_frame, height=1, width=60, font=("Courier", 10),
                       wrap="none", xscrollcommand=x_scroll.set)
    text_box.insert(tk.END, cmd_text)
    text_box.configure(state="disabled")
    text_box.pack()
    x_scroll.config(command=text_box.xview)

    # Optional: Add copy button
    def copy_to_clipboard():
        root.clipboard_clear()
        root.clipboard_append(cmd_text)

    copy_btn = tk.Button(popup, text="Copy to Clipboard", command=copy_to_clipboard, bg="PaleTurquoise1", fg="black")
    copy_btn.pack()

    # Close Button
    tk.Button(popup, text="Close", command=popup.destroy, bg="red3", fg="white").pack(pady=5)



# Main function to create the macro text file with user inputs
def create_macro_file():

    if not home_directory_var.get():
        messagebox.showerror("Home Directory Not Selected",
                             "Please select a home directory.",
                             parent=root)

    # Validate macro name
    if " " in macro_name_var.get():
        messagebox.showerror("Invalid Macro Name",
                             "Macro name cannot contain spaces.\nPlease use underscores (_) or hyphens (-).",
                             parent=root)
        return

    #Validate values for inputs
    if exposure_time_var.get()==0:
        messagebox.showerror("Invalid Exposure Time",
                             "Exposure time cannot be zero. Please correct.",
                             parent=root)
        return

    if num_images_var.get()==0:
        messagebox.showerror("Invalid Number of Images",
                             "Number of images cannot be zero. Please correct.",
                             parent=root)
        return

    if num_loops_var.get()==0:
        messagebox.showerror("Invalid Number of Loops",
                             "Number of loops cannot be zero. Please correct.",
                             parent=root)
        return

    if not sample_name_var.get():
        messagebox.showerror("Sample Name Missing",
                             "Please input sample name.",
                             parent=root)
        return

    if not sample_name_var.get():
        messagebox.showerror("Sample Name Missing",
                             "Please input sample name.",
                             parent=root)
        return

    if not AXS_var.get():
        messagebox.showerror("Scattering Range Not Selected",
                             "Please select scattering range.",
                             parent=root)

    # Retrieve values from the input fields
    macro_name = macro_name_var.get()
    home_directory = home_directory_var.get()
    data_folder = data_folder_var.get()
    print(macro_name)
    print(data_folder)
    exposure_time = exposure_time_var.get()
    sleep_time = sleep_time_var.get()
    num_images = num_images_var.get()
    num_loops = num_loops_var.get()
    dark_onoff = dark_onoff_var.get()
    dark_exposure = dark_exposure_var.get()
    sample_name = sample_name_var.get()
    gx = gx_var.get()
    gy = gy_var.get()
    theta = theta_var.get()


    spec_dir = Path(home_directory)
    spec_dir = Path(*spec_dir.parts[2:])
    spec_dir = spec_dir.as_posix()

    cameras = {
        "bottom": bottom_camera_var,
        "side": side_camera_var,
        "top": top_camera_var
    }

    camera_lines = ""
    for label, var in cameras.items():
        if var.get():
            camera_lines += f'      epics_put("MSD_Local_Cameras:BL1-5_{label}_camera:save_frame", base_filename)\n'

    detector_map = axs_mapping = {
    "SAXS": [
        'unix(sprintf("mkdir -p %s/SAXS", pilatus_baseDir))',
        'pd enable # Enable SAXS 1M detector',
        'eval(sprintf("pd savepath %s/SAXS", pilatus_baseDir))',
        'pd save # save SAXS data',
        'pd disable  # Disable SAXS detector after scan'
    ],
    "WAXS": [
        'unix(sprintf("mkdir -p %s/WAXS", pilatus_baseDir))',
        'pdw enable #Enable WAXS detector',
        'eval(sprintf("pd savepath %s/WAXS", pilatus_baseDir))',
        'pdw save	# save WAXS data',
        'pdw disable  # Disable WAXS detector after scan'
    ],
    "Both": [
        'unix(sprintf("mkdir -p %s/SAXS %s/WAXS", pilatus_baseDir, pilatus_baseDir))',
        'pd enable # Enable SAXS 1M detector \n                 pdw enable #Enable WAXS detector',
        'eval(sprintf("pd savepath %s/SAXS", pilatus_baseDir)) \n                  eval(sprintf("pdw savepath %s/WAXS", pilatus_baseDir))',
        'pd save # save SAXS data \n                    pdw save	# save WAXS data',
        'pd disable  # Disable SAXS detector after scan \n                  pdw disable  # Disable WAXS detector after scan'
    ]
    }

    # remove dark data capture from macro if unnecessary
    dark_frame_block = ""
    if dark_onoff != 0:
        dark_frame_block = f"""
        sclose
        sleep({sleep_time})
        data_dir = sprintf("dark_run%d_loop%d", run_ctr, loop_ctr)  # No trailing '/'
        p data_dir

        p "Taking data"

        wait_time = 0

        {detector_map.get(AXS_var.get(), [])[1]}

        eval(sprintf("newfile %s/%s", pilatus_baseDir, data_dir))
        {detector_map.get(AXS_var.get(), [])[2]}

        {detector_map.get(AXS_var.get(), [])[3]}

        # Take the actual data
        eval(sprintf("loopscan %d %d %d", dark_num_images, dark_exposure, wait_time))

        {detector_map.get(AXS_var.get(), [])[4]}
        # Implement sleep time between scans if required
        if (sleep_time > 0) {{
        printf("You can hit control-C for the next %i seconds....\\n", sleep_time)
        sleep(sleep_time)
        p ".... DON'T hit control-C until we sleep again\\n"
        sopen
        }}
                
            """

    # Define the content of the text file with user-defined values - this is the meat
    content = f"""
exposure_time = {exposure_time}          # exposure time for each image (in seconds)
num_loops = {num_loops}                # number of images in the scan 
sleep_time = {sleep_time}                # sleep time between each image (in seconds), enter a value of 0 to disable it
num_images = {num_images}
dark_exposure = {dark_exposure}
dark_num_images = 1

#Define the sample names
sample_name = "{f'{sample_name}-theta{theta}' if theta !="" else f'{sample_name}'}"

# Define list of coordinates (gx, gy, theta)
{ f'umv gx {gx}' if gx !="" else '' }
{ f'umv gy {gy}' if gy !="" else '' }
{ f'umv th {theta}' if theta !="" else '' }

############################
#File name and location
############################

cd ~/data
cd {spec_dir}

pilatus_baseDir = "{data_folder}"

rock no
loop_ctr = 0

# if (!exists("run_ctr")) {{  # Check if run_ctr exists, initialize if not
#     run_ctr = 0;
# }}
run_ctr += 1  # Increment global run counter to prevent accidental deletion

# Execute directory creation using Linux based commands
unix(sprintf("mkdir -p %s", pilatus_baseDir))
{detector_map.get(AXS_var.get(), [])[0]}

##############
pd stop

sleep(5.0)

for (loop_ctr=0; loop_ctr < num_loops; loop_ctr++) {{
    {dark_frame_block}
    base_filename = sample_name
    
    sopen
    #Create a variable for file name containing the data
    data_dir = sprintf("%s_run%d_loop%d", base_filename, run_ctr, loop_ctr)  #No trailing '/'
    sleep(5)

    #save images from cameras (if any listed)
{camera_lines.rstrip()}

    p data_dir

    #############################################################################
    # Create directories for SAXS and WAXS and save data in those
    #############################################################################
    p "Taking data"

    {detector_map.get(AXS_var.get(), [])[1]}

    eval(sprintf("newfile %s/%s", pilatus_baseDir, data_dir))
    {detector_map.get(AXS_var.get(), [])[2]}

    {detector_map.get(AXS_var.get(), [])[3]}

    #Take the actual data
    eval(sprintf("loopscan %d %d %d", num_images, exposure_time, wait_time))

    {detector_map.get(AXS_var.get(), [])[4]}
    
    # Implement sleep time between scans if required
    if (sleep_time > 0) {{
        printf("You can hit control-C for the next %i seconds....\\n", sleep_time)
        sleep(sleep_time)
        p ".... DON'T hit control-C until we sleep again\\n"
    }}   
    sclose 
    
}}
{ f'umv th 0' if theta !="" else '' }
cd ~/data
"""

    file_path = f"{home_directory_var.get()}/{macro_name}.txt"
    print(file_path)

    # If a valid file path is selected, check if file exists and then write content to the file
    try:
        if file_path:
            if os.path.exists(file_path):
                overwrite = messagebox.askyesno("File Exists",
                                                "A file with that name already exists.\nDo you want to overwrite it?",
                                                parent=root)
                if not overwrite:
                    return  # Exit function if user chooses not to overwrite

    #if the file is open it will trigger Errno 13. This checks for that and will produce a prompt for the user
    except PermissionError:
        messagebox.showerror(
        "Permission Denied",
        f"Cannot access or overwrite the file '{file_path}'.\n\nPlease close the file if it's open in another program and restart the application."
        )
        return
    #write/save the text file
    try:
        with open(file_path, "w") as file:
            file.write(content)

        # Show success popup
        show_success_popup(home_directory_var.get(), macro_name)

    except Exception as e:
        messagebox.showerror("Error", f"Error saving file: {e}", parent=root)

####################################################################################################################

# Create the main GUI window
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.title("Macro Generator - Grazing")

#Create the overall frame
frame=tkinter.Frame(root, bg= "dark red")
frame.pack() #with .pack() Tkinter automatically places the widget in the window without needing to manually specify coordinates

#Create the subframe for the folder names section
folder_names=tkinter.LabelFrame(frame, text="Save Location")
folder_names.grid(row=0, column=0, padx=10, pady=10)

# Button and Label for Folder Selection
# Create a canvas to hold the label (text box) with horizontal scroll
canvas = tk.Canvas(folder_names, width=400, height=20)  # Adjust width as necessary
canvas.grid(row=0, column=1, columnspan=2)

# Add a horizontal scrollbar to the canvas
scroll_x = tk.Scrollbar(folder_names, orient="horizontal", command=canvas.xview)
scroll_x.grid(row=1, column=1, sticky="ew")
canvas.configure(xscrollcommand=scroll_x.set)

# Create a frame inside the canvas to place the label (text box) - placing label in canvas directly may complicate things
label_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=label_frame, anchor="nw")

#Now to populate the canvas and the frame with the home directory information...
home_directory_var = tk.StringVar()   # Variable to store selected folder path
home_directory_button = tk.Button(folder_names, text="Select Home Directory folder", command=lambda: select_folder(home_directory_var), bg="PaleTurquoise1", fg="black")     #button to select folder
home_directory_button.grid(row=0, column=0, pady=(10,0), padx=(10,0))     #location of button
home_directory_selection = tk.Label(label_frame, textvariable=home_directory_var, fg="blue")  # Display selected folder path
home_directory_selection.grid(row=0, column=1, columnspan=2)      #location of text box

#Ensure scroll region will update after being populated with text
home_directory_selection.bind("<Configure>", update_scrollregion)

#Now to fill in the users chosen name for the macro - this could include their sample name
macro_name_label= tk.Label(folder_names, text="Macro name:")
macro_name_label.grid(row=2, column=0, sticky="E", padx=(0,5))
macro_name_var = tk.StringVar()
macro_name_entry = tk.Entry(folder_names, textvariable=macro_name_var, width= 40)
macro_name_entry.grid(row=2, column=1, sticky = "W")
macro_name_note = tk.Label(folder_names, text="**Cannot include spaces, use - or _. e.g. macro_20250328_air", wraplength=200)
macro_name_note.grid(row=2, column=1, padx=(250,5))

#Now to fill in the users chosen name for the data folder - they can choose to have it be named the same as their macro name
data_folder_label = tk.Label(folder_names, text="Data folder name:")
data_folder_label.grid(row=3, column=0, sticky="E", padx=(0,5))
data_folder_var = tk.StringVar()
data_folder_entry = tk.Entry(folder_names, textvariable=data_folder_var, width= 40)
data_folder_entry.grid(row=3, column=1, sticky = "W")
data_folder_button = tk.Button(folder_names, text="Same as macro", command=lambda: update_label(macro_name_var,data_folder_var), bg="PaleTurquoise1", fg="black")     #button to select folder
data_folder_button.grid(row=4, column=1, sticky="W")     #location of button



###
scan_param_frame=tkinter.LabelFrame(frame, text="Scan Parameters")
scan_param_frame.grid(row=1, column=0, padx=10, pady=(0,10))

# Label and entry for Exposure Time
exposure_time_label = tk.Label(scan_param_frame, text="Exposure Time (seconds):")
exposure_time_label.grid(row=0, column=0, padx=(5,5))
exposure_time_var = tk.IntVar()
exposure_time_entry = tk.Entry(scan_param_frame, textvariable=exposure_time_var, width=10)
exposure_time_entry.grid(row=1, column=0)

# Label and entry for Sleep Time
sleep_time_label = tk.Label(scan_param_frame, text="Sleep Time (seconds):")
sleep_time_label.grid(row=0, column=1, padx=(5,5))
sleep_time_var = tk.IntVar()
sleep_time_entry =tk.Entry(scan_param_frame, textvariable=sleep_time_var, width=10)
sleep_time_entry.grid(row=1, column=1)

# Label and entry for Number of Images
number_of_images_label = tk.Label(scan_param_frame, text="Number of Images:")
number_of_images_label.grid(row=0, column=2, padx=(5,5))
num_images_var = tk.IntVar()
number_of_images_entry = tk.Entry(scan_param_frame, textvariable=num_images_var, width=10)
number_of_images_entry.grid(row=1, column=2)

# Label and entry for Number of Loops
number_of_loops_label = tk.Label(scan_param_frame, text="Number of Loops:")
number_of_loops_label.grid(row=0, column=3, padx=(5,5))
num_loops_var = tk.IntVar()
number_of_loops_entry = tk.Entry(scan_param_frame, textvariable=num_loops_var, width=10)
number_of_loops_entry.grid(row=1, column=3)

#Label and entry for the kind of AXS - SAXS or WAXS
AXS_label = tk.Label(scan_param_frame, text="Scattering Range")
AXS_label.grid(row =0, column = 4, padx=(5,5))
AXS_var = tk.StringVar()
AXS_dropdown = ttk.Combobox(scan_param_frame, textvariable=AXS_var, values= ["SAXS", "WAXS", "Both"], width= 10, state= "readonly")
AXS_dropdown.grid(row=1, column= 4, padx=(0,10))


###
dark_frame = tk.LabelFrame(frame, text = "Dark")
dark_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))

# "Take dark?"
dark_label = tk.Label(dark_frame, text="Take dark?")
dark_label.grid(row=0, column=0, padx = 10)
dark_onoff_var = tk.IntVar()
dark_checkbox = tk.Checkbutton(dark_frame, text= "Yes", variable= dark_onoff_var, onvalue= 1, offvalue= 0)
dark_checkbox.grid(row=1, column= 0)


# "dark exposure" label
dark_exposure_label = tk.Label(dark_frame, text="Dark exposure time (seconds):")
dark_exposure_label.grid(row=0, column=1, padx = 10)

# Entry box
dark_exposure_var = tk.IntVar()
dark_exposure_entry = tk.Entry(dark_frame, textvariable=dark_exposure_var, width=10)
dark_exposure_entry.grid(row=1, column=1)



###
sample_param_frame=tkinter.LabelFrame(frame, text="Sample Parameters")
sample_param_frame.grid(row=3, column=0, padx=10, pady=(0,10))

#
sample_name_label = tk.Label(sample_param_frame, text="Sample name:")
sample_name_label.grid(row=0, column=0, padx=10)
sample_name_var = tk.StringVar()
sample_name_entry = tk.Entry(sample_param_frame, width=20, textvariable=sample_name_var)
sample_name_entry.grid(row=1, column=0, padx=(10,10))

#
gx_label = tk.Label(sample_param_frame, text="gx:")
gx_label.grid(row=0, column=1, padx=5)
gx_var = tk.StringVar()
gx_entry = tk.Entry(sample_param_frame, width=10, textvariable=gx_var)
gx_entry.grid(row=1, column=1, padx=(0,10))

#
gy_label = tk.Label(sample_param_frame, text="gy:")
gy_label.grid(row=0, column=2, padx=5)
gy_var = tk.StringVar()
gy_entry = tk.Entry(sample_param_frame, width=10, textvariable=gy_var)
gy_entry.grid(row=1, column=2, padx=(0,10))

#
theta_label = tk.Label(sample_param_frame, text="theta:")
theta_label.grid(row=0, column=3, padx=5)
theta_var = tk.StringVar()
theta_entry = tk.Entry(sample_param_frame, width=10, textvariable=theta_var)
theta_entry.grid(row=1, column=3, padx=(0,10))


###
cameras_frame=tkinter.LabelFrame(frame, text="Camera Parameters")
cameras_frame.grid(row=4, column=0, padx=10, pady=(0,10))

cameras_label = tk.Label(cameras_frame, text="What cameras do you want to use?")
cameras_label.grid(row=0, column= 1)

bottom_camera_var = tk.IntVar()
bottom_camera_button = tk.Checkbutton(cameras_frame, text="Bottom Camera", variable= bottom_camera_var, onvalue=1, offvalue=0)
bottom_camera_button.grid(row= 1, column= 0 )

side_camera_var = tk.IntVar()
side_camera_button = tk.Checkbutton(cameras_frame, text="Side Camera", variable= side_camera_var, onvalue=1, offvalue=0)
side_camera_button.grid(row= 1, column= 1)

top_camera_var = tk.IntVar()
top_camera_button = tk.Checkbutton(cameras_frame, text="Top Camera", variable= top_camera_var, onvalue=1, offvalue=0)
top_camera_button.grid(row= 1, column= 2)



###
###
# Footer row frame spans full width
footer_frame = tk.Frame(root)
footer_frame.pack(fill=tk.X, pady=10)

# Save button — centered using `place` in the root window
save_button = tk.Button(root, text="Save File", command=create_macro_file, bg="chartreuse4", fg="white")
save_button.place(relx=0.5, rely=.9850, anchor="s")  # relx=0.5 centers horizontally

# Label — right-aligned inside the footer frame
credit_label = tk.Label(footer_frame, text="Katerina Reynolds 2025", font=("Arial", 8), fg="indianred")
credit_label.pack(side=tk.RIGHT, padx=10)


# Start the GUI event loop
root.mainloop()



