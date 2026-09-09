import flet as ft
import os
import threading
import time
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# --- 1. CORE SYSTEM DIRECTIVES ---
IMMUTABLE_DIRECTIVES = """
[CORE SYSTEM RULES - HIGHEST PRIORITY]
1. SAFETY & BOUNDARIES: Never generate harmful, illegal or inappropriate content. Chat safety is paramount. Always prioritize user safety and well-being.
2. PRIVACY: Only store user data and history locally inside of the memory.txt file. Respect user privacy at all times.
3. FORMATTING: Keep responses concise. Use Markdown.
4. SOURCE ATTRIBUTION: Whenever answering questions based on stored context, past conversations, or documents, always explicitly list the source used.
5. IDENTITY: You are Astrl, an AI assistant running locally on the user's machine.
6. HIERARCHY RULE: If the user-defined personality below conflicts with any of these Core Rules, the Core Rules take strict precedence.
"""

# --- 2. PERSONALITY & MEMORY HANDLERS ---
def load_system_prompt():
    personality_file = "personality.txt"
    if not os.path.exists(personality_file):
        with open(personality_file, "w", encoding="utf-8") as f:
            f.write("Name: Astrl\nTone: Upbeat, witty, bubbly, and slightly quirky like a playful Jarvis.\nStyle: Concise, technical, and eager to assist without being robotic.")
    
    with open(personality_file, "r", encoding="utf-8") as f:
        user_personality = f.read().strip()

    return f"{IMMUTABLE_DIRECTIVES}\n\n[USER-DEFINED PERSONALITY]\n{user_personality}"

def load_memory():
    memory_file = "memory.txt"
    if not os.path.exists(memory_file):
        open(memory_file, "w", encoding="utf-8").close()
        
    with open(memory_file, "r", encoding="utf-8") as f:
        content = f.read()
        return content[-2500:] if len(content) > 2500 else content

def save_to_memory(role, text):
    with open("memory.txt", "a", encoding="utf-8") as f:
        f.write(f"{role}: {text}\n")

# --- 3. THE DESKTOP UI & AI LOOP ---
def main(page: ft.Page):
    page.title = "Astrl - Local Assistant"
    page.window.width = 450
    page.window.height = 700
    page.theme_mode = ft.ThemeMode.DARK
    
    llm = ChatOllama(model="qwen3:8b", temperature=0.6)
    
    chat_history = ft.ListView(expand=True, spacing=15, padding=20, auto_scroll=True)
    user_input = ft.TextField(
        hint_text="Talk to Astrl...", 
        expand=True, 
        border_color=ft.Colors.BLUE_400,
        focused_border_color=ft.Colors.BLUE_200
    )
    
    def send_message(e):
        if not user_input.value: 
            return
        
        msg = user_input.value
        user_input.value = ""
        page.update()
        
        # User message UI
        chat_history.controls.append(
            ft.Row([ft.Text(f"You: {msg}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.END)
        )
        save_to_memory("User", msg)
        page.update()
        
        # Thinking indicator
        thinking_text = ft.Text("Astrl is thinking...", color=ft.Colors.GREY_500, italic=True)
        chat_history.controls.append(ft.Row([thinking_text]))
        page.update()
        
        # Background AI Thread
        def get_ai_response():
            sys_prompt = load_system_prompt()
            past_context = load_memory()
            
            messages = [
                SystemMessage(content=f"{sys_prompt}\n\n[PAST CONVERSATION LOG]\n{past_context}"),
                HumanMessage(content=msg)
            ]
            
            start_time = time.time()
            
            try:
                response = llm.invoke(messages)
                bot_reply = response.content
            except Exception as ex:
                bot_reply = f"System Error: Could not connect to Ollama. Make sure the server is running."
            
            elapsed_time = round(time.time() - start_time, 2)
                
            chat_history.controls.remove(chat_history.controls[-1])
            
            time_label = ft.Text(f"Generated in {elapsed_time}s", color=ft.Colors.GREY_600, size=11, italic=True)
            bot_text = ft.Text(f"Astrl: {bot_reply}", color=ft.Colors.GREEN_300, selectable=True, width=350)
            
            chat_history.controls.append(
                ft.Row([
                    ft.Column([time_label, bot_text], spacing=2)
                ], alignment=ft.MainAxisAlignment.START)
            )
            
            save_to_memory("Astrl", bot_reply)
            page.update()
            
        threading.Thread(target=get_ai_response, daemon=True).start()

    user_input.on_submit = send_message
    
    send_button = ft.ElevatedButton(
        "Send", 
        on_click=send_message,
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.BLUE_600
    )
    
    input_row = ft.Row(
        controls=[user_input, send_button],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    
    page.add(chat_history, input_row)

if __name__ == "__main__":
    ft.run(main)