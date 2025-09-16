import PyPDF2
import google.generativeai as genai
import tkinter as tk
from tkinter import filedialog, scrolledtext

# connect Gemini
genai.configure(api_key="your API key")
model = genai.GenerativeModel("gemini-1.5-flash")

all_text = ""  # will hold all the PDF text

# pick and load PDF
def load_pdf():
    global all_text
    path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not path:
        return
    
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        all_text = ""
        for page in reader.pages:
            all_text += page.extract_text()
    
    # show in chat + save in file
    output_box.insert(tk.END, f"\nPDF Uploaded: {path}\n\n")
    output_box.see(tk.END)
    with open("chat_history.txt", "a", encoding="utf-8") as log:
        log.write(f"\nPDF Uploaded: {path}\n\n")

# ask AI a question about PDF
def ask_question(event=None):
    question = question_entry.get().strip()
    if not question:
        return
    
    if not all_text:
        output_box.insert(tk.END, "\nUpload a PDF first.\n\n")
        return
    
    # make the prompt
    prompt = f"Document:\n{all_text}\n\nQuestion: {question}"
    
    try:
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"Error: {str(e)}"
    
    # show both Q and A
    output_box.insert(tk.END, f"\nQ: {question}\nA: {answer}\n\n")
    output_box.see(tk.END)
    question_entry.delete(0, tk.END)
    
    # also save in chat file
    with open("chat_history.txt", "a", encoding="utf-8") as log:
        log.write(f"Q: {question}\nA: {answer}\n\n")

# clear screen (but still keep in file log)
def clear_chat():
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, "Chat cleared.\n\n")
    with open("chat_history.txt", "a", encoding="utf-8") as log:
        log.write("Chat cleared.\n\n")

# GUI setup
root = tk.Tk()
root.title("PDF Q&A with Gemini")

frame = tk.Frame(root)
frame.pack(pady=5)

tk.Button(frame, text="Upload PDF", command=load_pdf).grid(row=0, column=0, padx=5)
tk.Button(frame, text="Ask", command=ask_question).grid(row=0, column=1, padx=5)
tk.Button(frame, text="Clear Chat", command=clear_chat).grid(row=0, column=2, padx=5)
tk.Button(frame, text="Exit", command=root.quit).grid(row=0, column=3, padx=5)  


question_entry = tk.Entry(root, width=80)
question_entry.pack(pady=5)
question_entry.insert(0, "Type your question here...")

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=25)
output_box.pack(pady=5)

# press Enter to ask
question_entry.bind("<Return>", ask_question)

root.mainloop()
