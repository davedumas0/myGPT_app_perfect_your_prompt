import openai
import requests
import os
import json
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox

def get_required_libraries():
    libraries = {
        "openai": openai.__version__,
        "requests": requests.__version__,
        "tkinter": tkinter.Tcl().eval('info patchlevel'),
        "ttk": ttk.__version__
    }
    return libraries
 


# You can call this function at the end of your program for debugging
if __name__ == "__main__":
    required_libraries = get_required_libraries()
    for library, version in required_libraries.items():
        print(f"{library} version: {version}")


def read_api_key(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()

dir_path = os.path.dirname(os.path.realpath(__file__))
api_key_file_path = os.path.join(dir_path, "api_key.txt")
openai.api_key = read_api_key(api_key_file_path)

def interact_with_chatgpt(prompt, model, max_tokens, temperature, role):
    messages = [
        {"role": "system", "content": f"You are a {role}."},
        {"role": "user", "content": f"{prompt} [improve this prompt]"}
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}",
    }

    response = requests.post(
        f"https://api.openai.com/v1/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": messages,
            "max_tokens": int(max_tokens),
            "temperature": temperature,
        },
    )
    response.raise_for_status()
    response_data = response.json()

    return response_data['choices'][0]['message']['content']

def get_better_prompt():
    user_prompt = prompt_entry.get()
    model = "gpt-3.5-turbo-16k"
    max_tokens = max_tokens_scale.get()
    temperature = temperature_scale.get() / 10.0
    role = "prompt engineer"  # always use 'prompt engineer' as the role
    better_prompt = interact_with_chatgpt(user_prompt, model, max_tokens, temperature, role)
    result_text.delete(1.0, END)
    result_text.insert(END, "Better prompt: " + better_prompt)

def try_again(role, text_widget):
    user_prompt = text_widget.get("1.0", 'end-1c')
    model = "gpt-3.5-turbo-16k"
    max_tokens = max_tokens_scale.get()
    temperature = temperature_scale.get() / 10.0
    better_prompt = interact_with_chatgpt(user_prompt, model, max_tokens, temperature, role)
    text_widget.delete(1.0, END)
    text_widget.insert(END, "Better prompt: " + better_prompt)

def open_multi_agent_window():
    global multi_agent_window
    if 'multi_agent_window' in globals():
        multi_agent_window.destroy()

    selected_roles = roles_listbox.curselection()
    if len(selected_roles) > 3:
        messagebox.showerror("Too many roles", "You can select up to 3 roles at a time.")
        roles_listbox.selection_clear(0, END)
        return

    multi_agent_window = Toplevel(root)
    multi_agent_window.title('Multi Agent Mode')
    multi_agent_window.geometry("800x600")

    user_prompt = prompt_entry.get()
    
    role_frames = []
    for i, selected_role in enumerate(selected_roles):
        role = roles_listbox.get(selected_role)
        frame = ttk.Frame(multi_agent_window)
        frame.pack(fill=BOTH, expand=True)

        role_label = ttk.Label(frame, text=f'Role: {role}')
        role_label.pack(pady=10)

        result_text = Text(frame, width=60, height=10, bg='#434343', fg='#f5f5f5')
        result_text.pack(pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack()

        side = 'left' if i % 2 == 0 else 'right'
        try_again_button = ttk.Button(button_frame, text='Try Again', command=lambda role=role, result_text=result_text: try_again(role, result_text))
        try_again_button.pack(side=side, padx=10)
        
        move_up_button = ttk.Button(button_frame, text='Move Up', command=lambda frame=frame: move_up(frame))
        move_up_button.pack(side=side, padx=10)
        
        move_down_button = ttk.Button(button_frame, text='Move Down', command=lambda frame=frame: move_down(frame))
        move_down_button.pack(side=side, padx=10)

        model = "gpt-3.5-turbo-16k"
        max_tokens = max_tokens_scale.get()
        temperature = temperature_scale.get() / 10.0
        better_prompt = interact_with_chatgpt(user_prompt, model, max_tokens, temperature, role)
        result_text.insert(END, "Better prompt: " + better_prompt)

        user_prompt = better_prompt  # pass the improved prompt to the next role

        # Add the frame to the list of role frames
        role_frames.append(frame)

root = Tk()
root.title('Perfect Your Prompt')
root.geometry("1024x768")

pricedown_font = tkFont.Font(family='Pricedown', size=16)

style = ttk.Style()
style.configure("TFrame", background="#000000")
style.configure("TLabel", background="#000000", foreground="#FFFFFF", font=pricedown_font)
style.configure("TEntry", fieldbackground="#434343", foreground="#000000")
style.configure("TButton", font=pricedown_font, background="#008000", foreground="green")
style.configure("TScale", background="#000000", troughcolor="#008000")

frame = ttk.Frame(root)
frame.pack(fill=BOTH, expand=True)

prompt_label = ttk.Label(frame, text='Enter your prompt:')
prompt_label.pack(pady=10)
prompt_entry = ttk.Entry(frame, width=60)
prompt_entry.pack(pady=10)

roles_label = ttk.Label(frame, text='Select AI roles (up to 3):')
roles_label.pack(pady=10)
roles_listbox = Listbox(frame, selectmode=MULTIPLE)
for role in ["project manager", "AI researcher", "musician", "engineer", "python programmer", "translator", "lua scripting expert", "game artist", "game tester"]:
    roles_listbox.insert(END, role)
roles_listbox.pack(pady=10)

max_tokens_label = ttk.Label(frame, text='Set max tokens (10-200):')
max_tokens_label.pack(pady=10)
max_tokens_scale = ttk.Scale(frame, from_=10, to=200, orient=HORIZONTAL, length=400)
max_tokens_scale.set(100)
max_tokens_scale.pack(pady=10)

temperature_label = ttk.Label(frame, text='Set temperature (0-10):')
temperature_label.pack(pady=10)
temperature_scale = ttk.Scale(frame, from_=0, to=10, orient=HORIZONTAL, length=400)
temperature_scale.set(5)
temperature_scale.pack(pady=10)

result_button = ttk.Button(frame, text='Get Better Prompt', command=get_better_prompt)
result_button.pack(pady=10)
multi_agent_button = ttk.Button(frame, text='Multi Agent Mode', command=open_multi_agent_window)
multi_agent_button.pack(pady=10)

result_text = Text(frame, width=60, height=10, bg='#434343', fg='#f5f5f5')
result_text.pack(pady=10)


a = get_required_libraries()
print(a)
root.mainloop()
