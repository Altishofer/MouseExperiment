from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk

# Data structure to hold the experiments
experiments = []


# Function to show the add experiment popup
def show_add_experiment_popup():
    popup = Toplevel(root)
    popup.title("Add Experiment")
    popup.geometry("300x250")

    Label(popup, text="Mouse ID:").grid(row=0, column=0, padx=10, pady=5)
    entry_mouse_id = Entry(popup)
    entry_mouse_id.grid(row=0, column=1, padx=10, pady=5)

    Label(popup, text="Compound:").grid(row=1, column=0, padx=10, pady=5)
    entry_compound = Entry(popup)
    entry_compound.grid(row=1, column=1, padx=10, pady=5)

    current_datetime = datetime.now()
    default_date = current_datetime.strftime('%Y-%m-%d')
    default_time = current_datetime.strftime('%H:%M')

    Label(popup, text="Injection Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=5)
    entry_injection_date = Entry(popup)
    entry_injection_date.insert(0, default_date)
    entry_injection_date.grid(row=2, column=1, padx=10, pady=5)

    Label(popup, text="Injection Time (HH:MM):").grid(row=3, column=0, padx=10, pady=5)
    entry_injection_time = Entry(popup)
    entry_injection_time.insert(0, default_time)
    entry_injection_time.grid(row=3, column=1, padx=10, pady=5)

    def save_experiment():
        mouse_id = entry_mouse_id.get()
        compound = entry_compound.get()
        injection_date_str = entry_injection_date.get()
        injection_time_str = entry_injection_time.get()
        if mouse_id and compound and injection_date_str and injection_time_str:
            try:
                injection_time = datetime.strptime(f"{injection_date_str} {injection_time_str}", '%Y-%m-%d %H:%M')
                experiment = {
                    'mouse_id': mouse_id,
                    'compound': compound,
                    'injection_time': injection_time,
                    'scans': []
                }
                experiments.append(experiment)
                update_experiment_list()
                update_timetable()
                popup.destroy()
            except ValueError:
                output_box.insert(END, "Invalid date or time format. Use YYYY-MM-DD HH:MM\n")
                output_box.see(END)

    def cancel():
        popup.destroy()

    Button(popup, text="Save", command=save_experiment).grid(row=4, column=0, pady=10)
    Button(popup, text="Cancel", command=cancel).grid(row=4, column=1, pady=10)


# Function to show the add scan popup
def show_add_scan_popup(experiment):
    popup = Toplevel(root)
    popup.title("Add Scan")
    popup.geometry("300x150")

    Label(popup, text="Time Difference (hours):").grid(row=0, column=0, padx=10, pady=5)
    entry_time_diff = Entry(popup)
    entry_time_diff.grid(row=0, column=1, padx=10, pady=5)

    Label(popup, text="Person:").grid(row=1, column=0, padx=10, pady=5)
    entry_person = Entry(popup)
    entry_person.grid(row=1, column=1, padx=10, pady=5)

    def save_scan():
        time_diff_str = entry_time_diff.get()
        person = entry_person.get()
        if time_diff_str and person:
            try:
                time_diff = float(time_diff_str)
                scan_time = experiment['injection_time'] + timedelta(hours=time_diff)
                scan = {
                    'time_diff': time_diff,
                    'scan_time': scan_time,
                    'person': person
                }
                experiment['scans'].append(scan)
                update_action_list(experiment)
                update_timetable()
                popup.destroy()
            except ValueError:
                output_box.insert(END, "Invalid time difference format. Use a number.\n")
                output_box.see(END)

    def cancel():
        popup.destroy()

    Button(popup, text="Save", command=save_scan).grid(row=2, column=0, pady=10)
    Button(popup, text="Cancel", command=cancel).grid(row=2, column=1, pady=10)


# Function to update the experiment listbox
def update_experiment_list():
    for item in tree_experiments.get_children():
        tree_experiments.delete(item)
    for experiment in experiments:
        tree_experiments.insert('', 'end', values=(experiment['mouse_id'], experiment['compound']))


# Function to update the actions listbox
def update_action_list(experiment):
    for item in tree_actions.get_children():
        tree_actions.delete(item)
    for scan in experiment['scans']:
        tree_actions.insert('', 'end', values=(
        f"{scan['time_diff']:.2f} hours", scan['person'], scan['scan_time'].strftime('%Y-%m-%d %H:%M')))


# Function to handle experiment selection
def on_experiment_select(event):
    selected_item = tree_experiments.selection()
    if not selected_item:
        return
    selected_experiment_idx = tree_experiments.index(selected_item[0])
    selected_experiment = experiments[selected_experiment_idx]
    update_action_list(selected_experiment)
    button_add_scan.config(state=NORMAL, command=lambda: show_add_scan_popup(selected_experiment))


# Function to update the timetable
def update_timetable():
    for widget in frame_timetable.winfo_children():
        widget.destroy()

    if not experiments:
        return

    first_injection = min(experiments, key=lambda x: x['injection_time'])['injection_time']
    last_day = first_injection + timedelta(days=13)

    days = [(first_injection + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14)]
    mouse_ids = list(set(exp['mouse_id'] for exp in experiments))

    for col, day in enumerate([''] + days):
        Label(frame_timetable, text=day, borderwidth=1, relief="solid", width=12).grid(row=0, column=col, sticky='nsew')

    for row, mouse_id in enumerate(mouse_ids, start=1):
        Label(frame_timetable, text=mouse_id, borderwidth=1, relief="solid", width=12).grid(row=row, column=0,
                                                                                            sticky='nsew')
        for col, day in enumerate(days, start=1):
            day_datetime = datetime.strptime(day, '%Y-%m-%d')
            actions = [
                scan['scan_time'].strftime('%H:%M')
                for exp in experiments if exp['mouse_id'] == mouse_id
                for scan in exp['scans']
                if scan['scan_time'].date() == day_datetime.date()
            ]
            Label(frame_timetable, text='\n'.join(actions), borderwidth=1, relief="solid", width=12, height=4).grid(
                row=row, column=col, sticky='nsew')


# Main window
root = Tk()
root.geometry('1200x800')
root.title("Mouse Experiment Tracker")
root.configure(bg="white")

# Style configuration
style = ttk.Style()
style.configure('Treeview', rowheight=25)
style.configure('TLabel', background="white", foreground="black", font=("Arial", 10))
style.configure('TButton', background="#4CAF50", foreground="white", font=("Arial", 10, "bold"))
style.map('TButton', background=[('active', '#45a049')])

# Experiment List
frame_left = Frame(root, bg="white", relief=GROOVE, borderwidth=2)
frame_left.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=10, pady=10)

Label(frame_left, text="Experiment", bg="white", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5)

tree_experiments = ttk.Treeview(frame_left, columns=('Mouse ID', 'Compound'), show='headings')
tree_experiments.heading('Mouse ID', text='Mouse ID')
tree_experiments.heading('Compound', text='Compound')
tree_experiments.grid(row=1, column=0, sticky='nsew')

button_add_experiment = ttk.Button(frame_left, text="+", command=show_add_experiment_popup)
button_add_experiment.grid(row=2, column=0, pady=5)

# Actions List
frame_right = Frame(root, bg="white", relief=GROOVE, borderwidth=2)
frame_right.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=10, pady=10)

Label(frame_right, text="Actions", bg="white", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5)

tree_actions = ttk.Treeview(frame_right, columns=('Time Diff', 'Person', 'Scan Time'), show='headings')
tree_actions.heading('Time Diff', text='Time Diff')
tree_actions.heading('Person', text='Person')
tree_actions.heading('Scan Time', text='
