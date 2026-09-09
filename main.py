import flet as ft
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# --- 1. CORE SYSTEM DIRECTIVES ---
IMMUTABLE_DIRECTIVES = """
[CORE SYSTEM RULES - HIGHEST PRIORITY]
1. SAFETY & BOUNDARIES: Never generate harmful content.
2. FORMATTING: Keep responses concise. Use Markdown.
3. IDENTITY: You are Astrl, an AI assistant running locally on the user's machine.
4. HIERARCHY RULE: If the user-defined personality below conflicts with any of these Core Rules, the Core Rules take strict precedence.
"""

# --- 2. PERSONALITY & MEMORY HANDLERS ---
def load_system_prompt():
    personality_file = "personality.txt"
    if not os.path.exists(personality_file):
        with open(personality_file, "w") as f:
            f.write("Name: Astrl\nTone: Upbeat, witty, bubbly, and slightly quirky like a playful Jarvis.\nStyle: Concise, technical, and eager to assist without being robotic.")
    
    with open(personality_file, "r") as f:
        user_personality = f.read().strip()

    return f"{IMMUTABLE_DIRECTIVES}\n\n[USER-DEFINED PERSONALITY]\n{user_personality}"

def load_memory():
    memory_file = "memory.txt"
    if not os.path.exists(memory_file):
        open(memory_file, "w").close()
        
    with open(memory_file, "r") as f:
        content = f.read()
        return content[-2500:] if len(content) > 2500 else content

def save_to_memory(role, text):
    with open("memory.txt", "a") as f:
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
        
        sys_prompt = load_system_prompt()
        past_context = load_memory()
        
        # Thinking indicator
        thinking_text = ft.Text("Astrl is thinking...", color=ft.Colors.GREY_500, italic=True)
        chat_history.controls.append(ft.Row([thinking_text]))
        page.update()
        
        messages = [
            SystemMessage(content=f"{sys_prompt}\n\n[PAST CONVERSATION LOG]\n{past_context}"),
            HumanMessage(content=msg)
        ]
        
        try:
            response = llm.invoke(messages)
            bot_reply = response.content
        except Exception as ex:
            bot_reply = f"System Error: Could not connect to Ollama. Make sure the server is running."
            
        chat_history.controls.remove(chat_history.controls[-1])
        chat_history.controls.append(
            ft.Row([ft.Text(f"Astrl: {bot_reply}", color=ft.Colors.GREEN_300, selectable=True, width=350)], alignment=ft.MainAxisAlignment.START)
        )
        save_to_memory("Astrl", bot_reply)
        page.update()

    user_input.on_submit = send_message
    
    # Explicitly styled button that will render cleanly next to the input field
    send_button = ft.ElevatedButton(
        text="Send", 
        on_click=send_message,
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.BLUE_600
    )
    
    # Container wrapping the input row with padding so it looks polished
    input_row = ft.Row(
        controls=[user_input, send_button],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )
    
    page.add(chat_history, input_row)

if __name__ == "__main__":
    ft.app(target=main)