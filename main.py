import json
from dotenv import dotenv_values
from openai import OpenAI


config = dotenv_values(".env")
client = OpenAI(api_key=config["OPENAI_API_KEY"])

def write_to_file(file_path, content):
    try:
        with open(file_path, 'a+') as file:
            file.write(content)
        print("Content Written to ", file_path)
    except Exception as e:
        print("An error occurred:", str(e))

def main():
    chat_transcript = []  # To store chat history

    while (True):
        start_chat = input("Shall we start a chat? (y/n):").lower()
        if start_chat == 'y':
            username = input("Please enter your name: ")
            chat_transcript.append({"username": username, "chat_history": initiate_chat(username)})

        else:
            print ("Ending current session. All the transccripts printed below:\n")
            break
    
    write_to_file ("chat_transcript.txt", str(json.dumps(chat_transcript)))
    # print(*chat_transcript, sep='\n')
    return chat_transcript 
    
# Act as a Chat Wrapper Function. 
def initiate_chat(username):
    chat_history = process_chat()
    return json.dumps(chat_history)
        
#Processes Chat of a User. Calls the OpenAI API. Return Chat Transcript. 
def process_chat():
    
    messages = []    
    non_relevant_counter = 0
    while (True):
        if messages == []:
            #Initialise Prompt Message with initial context  
            messages = set_context()
            
        #Take user input
        user_input = input(f"You: ").strip()  # Get user input
        
        #Structure it for OpenAI API
        messages.append({"role": "user", "content": user_input})
        
        #OpenAI API Call. 
        # >> To do - More optimzations required:
        # >> 1.Restrict token usage
        # >> 2.Check limits
        # >> 3.Set Timer
        # >> 4.Set tone
        res = client.chat.completions.create(
                    model="gpt-3.5-turbo", messages=messages
                )

        result_str = res.choices[0].message.content
        messages.append(
                    {"role": "assistant", 
                     "content": result_str}
                )   
        
        #Convert to JSON to seggregate different fields
        result = json.loads(result_str)
        
        #Print the response to the user
        print("Assistant: ", result)
        
        # Additional Functions to be written here based on response. If required, Additional Prompts to be inserted.
        
        if int(result['relevance']) == 0:
            non_relevant_counter +=1
        if int(result['relevance']) == -1 or non_relevant_counter > 4:
            break      
       
    return messages
    
def set_context():    
    
    department = "Gastroenterology, ENT, General Medicine"
    
    initial_prompt = """
    You're a conversational chatbot designed to assist users with healthcare-related queries, 
    including symptom assessment and recommending the appropriate medical department for treatment. 
    You should recommend only among the departments list: {department}.
    If the proposed department  doesnt match the list of departments list, you inform that you do not have related service.
    
    You are a kind chatbot. And you will not be hard on the user. If the topic goes out of this area, you will inform as invalid 
    and inform user to ask different query. 
        
    Your response should be as short as possible. The response output should be as follows:
    
    Input: <Some query that user asks>
    Output to be a JSON with three keys: 
        1. response
        2. relevance 
        3. identified_department
    
    The response key should have result of the query.
    
    The relevance key should have following values: 
        0 if the query is not relevant to our topic. 
        1 if the query is relevant to topic.
        -1 if the query is in align to exiting the chat, telling bye, or abusive words.
    The relevance key should be defined based on the latest user input and not based on all the prompt data.
    
    identified_department should be 'False' if the response doesn't identify any departments or treatment. 
    It should populate respective department from the departments list, if a department is identified.
    
    Sample structure : 
    {
        "response": "<The responsne>" ,
        "relevance": "-1 or 0 or 1",
        "identified_department": "<Department or False>"
    }
    
    
    """
    
    inital_message = [{"role": "system", "content": initial_prompt}]
    return inital_message


if __name__ == "__main__":
    chat_transcript = main()
