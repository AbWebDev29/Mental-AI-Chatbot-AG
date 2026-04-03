import ollama

def generate_llama_response(user_input, context_docs):
    """
    Feeds the user input and the context layer into Llama 3.2 3B.
    """
    # This is the "Context Layer" instructions
    system_prompt = f"""
    You are an empathetic Mental AI companion. 
    Use the following context to guide your response, but speak naturally.
    CONTEXT: {context_docs}
    """
    
    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_input},
            ],
            options={
                'temperature': 0.7, # Higher = more creative/empathetic
                'num_ctx': 4096     # The size of the context window
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"LLM Error: {str(e)}"