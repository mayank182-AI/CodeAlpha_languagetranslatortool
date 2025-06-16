import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from deep_translator import GoogleTranslator
from langdetect import detect
import pyttsx3, pyperclip, speech_recognition as sr
from PIL import Image, ImageTk
import datetime, os, platform
from fpdf import FPDF
# --- Initialize main window ---
root = tk.Tk()
root.title("🌐 Smart Language Translator")
root.geometry("900x720")
root.resizable(False, False)

# --- Load background wallpaper ---
try:
    bg_image = Image.open(r"C:\\Users\\mayan\\Downloads\\translator.jpg").resize((900, 720))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print("Wallpaper failed to load:", e)

# --- Translation data ---
lang_dict = GoogleTranslator(source='auto', target='en').get_supported_languages(as_dict=True)
lang_name_to_code = {v.capitalize(): k for k, v in lang_dict.items()}
lang_names = sorted(lang_name_to_code.keys())
lang_names.insert(0, "Auto")

# --- Text-to-Speech setup ---
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# --- Create translation history log file if not exists ---
history_file = "translation_history.txt"
if not os.path.exists(history_file):
    open(history_file, "w", encoding='utf-8').close()

# --- Logging function ---
def log_translation(original, translated):
    with open(history_file, "a", encoding='utf-8') as f:
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{time}]\nFrom: {original}\nTo: {translated}\n\n")

# --- View history with search ---
def view_history():
    def search_history():
        keyword = search_entry.get().lower()
        with open(history_file, "r", encoding='utf-8') as f:
            lines = f.readlines()
        matched = [line for line in lines if keyword in line.lower()]
        history_text.config(state="normal")
        history_text.delete("1.0", tk.END)
        history_text.insert(tk.END, ''.join(matched))
        history_text.config(state="disabled")

    if os.path.exists(history_file):
        history_window = tk.Toplevel(root)
        history_window.title("📜 Translation History")
        history_window.geometry("600x400")

        search_entry = tk.Entry(history_window, width=30)
        search_entry.pack(pady=5)
        search_btn = tk.Button(history_window, text="🔍 Search", command=search_history)
        search_btn.pack(pady=2)

        history_text = tk.Text(history_window, wrap=tk.WORD)
        history_text.pack(expand=True, fill=tk.BOTH)
        with open(history_file, "r", encoding='utf-8') as f:
            content = f.read()
        history_text.insert(tk.END, content)
        history_text.config(state="disabled")

        export_btn = tk.Button(history_window, text="📄 Export as PDF", command=export_history_to_pdf)
        export_btn.pack(pady=5)
    else:
        messagebox.showinfo("History", "No translation history found.")

# --- Export history to PDF ---
def export_history_to_pdf():
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        with open(history_file, "r", encoding='utf-8') as f:
            lines = f.readlines()
        for line in lines:
            pdf.multi_cell(0, 10, txt=line.strip())
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if save_path:
            pdf.output(save_path)
            messagebox.showinfo("Exported", f"History exported to {save_path}")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))

# --- Save translated output ---
def save_output():
    text = output_box.get("1.0", tk.END).strip()
    if text:
        try:
            filename = f"translated_output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding='utf-8') as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Output saved as {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving file: {e}")

# --- Main translation logic ---
def translate_text():
    input_text = input_box.get("1.0", tk.END).strip()
    from_lang = from_lang_cb.get()
    to_lang = to_lang_cb.get()

    if not input_text:
        messagebox.showwarning("Input Required", "Please enter text to translate.")
        return

    try:
        from_code = lang_name_to_code.get(from_lang, 'auto')
        to_code = lang_name_to_code[to_lang]

        detected_code = detect(input_text)
        detected_name = next((k for k, v in lang_name_to_code.items() if v == detected_code), detected_code)
        detected_label.config(text=f"Detected: {detected_name}")

        translator = GoogleTranslator(source=from_code, target=to_code)
        translated = translator.translate(text=input_text)

        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, translated)
        log_translation(input_text, translated)

    except Exception as e:
        messagebox.showerror("Translation Error", str(e))

# --- TTS function ---
def speak_output():
    text = output_box.get("1.0", tk.END).strip()
    if text:
        engine.say(text)
        engine.runAndWait()

# --- Clipboard copy ---
def copy_output():
    text = output_box.get("1.0", tk.END).strip()
    if text:
        pyperclip.copy(text)
        messagebox.showinfo("Copied", "Translated text copied to clipboard!")

# --- Clear all fields ---
def clear_all():
    input_box.delete("1.0", tk.END)
    output_box.delete("1.0", tk.END)
    detected_label.config(text="Detected: None")

# --- Speech-to-text ---
def record_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("🎤 Speak Now", "Start speaking into the microphone...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            input_box.delete("1.0", tk.END)
            input_box.insert(tk.END, text)
        except sr.UnknownValueError:
            messagebox.showerror("Speech Error", "Could not understand audio.")
        except sr.RequestError:
            messagebox.showerror("Service Error", "Speech recognition service is unavailable.")

# --- Swap from and to languages ---
def swap_languages():
    from_val = from_lang_cb.get()
    to_val = to_lang_cb.get()
    if from_val != "Auto":
        from_lang_cb.set(to_val)
        to_lang_cb.set(from_val)

# --- Toggle Dark/Light Mode ---
def toggle_mode():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

# --- Apply theme globally ---
def apply_theme():
    bg = "#1e1e1e" if dark_mode else "#f0f0f0"
    fg = "#ffffff" if dark_mode else "#000000"
    box_bg = "#2e2e2e" if dark_mode else "#ffffff"
    btn_bg = "#444444" if dark_mode else "#dddddd"
    btn_fg = "#ffffff" if dark_mode else "#000000"

    root.configure(bg=bg)
    title.config(bg=bg, fg=fg)
    frame.config(bg=bg)
    detected_label.config(bg=bg, fg=fg)
    input_box.config(bg=box_bg, fg=fg)
    output_box.config(bg=box_bg, fg=fg)

    for widget in button_frame.winfo_children():
        widget.config(bg=btn_bg, fg=btn_fg)

    for widget in frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(bg=btn_bg, fg=btn_fg)

# --- UI Elements ---
dark_mode = True

title = tk.Label(root, text="🌍 Smart Language Translator", font=("Helvetica", 24, "bold"))
title.pack(pady=10)

input_box = tk.Text(root, height=6, width=95, wrap=tk.WORD, font=("Arial", 12), bd=2, relief=tk.GROOVE)
input_box.pack(pady=5)

frame = tk.Frame(root)
frame.pack(pady=5)

from_label = tk.Label(frame, text="From:", font=("Arial", 10))
from_label.grid(row=0, column=0)
from_lang_cb = ttk.Combobox(frame, values=lang_names, width=25, state="readonly")
from_lang_cb.set("Auto")
from_lang_cb.grid(row=0, column=1, padx=10)

to_label = tk.Label(frame, text="To:", font=("Arial", 10))
to_label.grid(row=0, column=2)
to_lang_cb = ttk.Combobox(frame, values=lang_names[1:], width=25, state="readonly")
to_lang_cb.set("English")
to_lang_cb.grid(row=0, column=3, padx=10)

swap_btn = tk.Button(frame, text="🔁 Swap", font=("Arial", 10), command=swap_languages)
swap_btn.grid(row=0, column=4, padx=10)

clear_btn = tk.Button(frame, text="🧹 Clear", font=("Arial", 10), command=clear_all)
clear_btn.grid(row=0, column=5, padx=10)

mode_btn = tk.Button(frame, text="🌗 Toggle Mode", font=("Arial", 10), command=toggle_mode)
mode_btn.grid(row=0, column=6, padx=10)

history_btn = tk.Button(frame, text="📜 View History", font=("Arial", 10), command=view_history)
history_btn.grid(row=0, column=7, padx=10)

translate_btn = tk.Button(root, text="🌐 Translate", font=("Arial", 12, "bold"), command=translate_text)
translate_btn.pack(pady=10)

detected_label = tk.Label(root, text="Detected: None", font=("Arial", 10))
detected_label.pack(pady=2)

output_box = tk.Text(root, height=6, width=95, wrap=tk.WORD, font=("Arial", 12), bd=2, relief=tk.SUNKEN)
output_box.pack(pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

buttons = [
    ("🎤 Mic Input", record_speech),
    ("🔊 Speak Output", speak_output),
    ("📋 Copy Output", copy_output),
    ("💾 Save Output", save_output)
]

for i, (label, cmd) in enumerate(buttons):
    tk.Button(button_frame, text=label, command=cmd, font=("Arial", 10)).grid(row=0, column=i, padx=10)

apply_theme()

# --- Main loop ---
root.mainloop()
