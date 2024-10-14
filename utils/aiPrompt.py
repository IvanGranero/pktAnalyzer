import os
from openai import OpenAI
#import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY", default = ""),
)

#Open AI settings 
def get_completion(prompt, model="gpt-3.5-turbo", temperature=0):
  completion = client.chat.completions.create(
      messages=prompt,
      model= model,
      temperature=temperature,
  )
  return completion.choices[0].message.content


#Voice prompting
# def record_audio():
#     recognizer = sr.Recognizer()

#     with sr.Microphone() as source:
#         print("Please speak now...")
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)

#     print("Finish recording audio.")
#     return audio

#Definicion de una funcion para extraer el texto de la voz
# def extract_text(audio):
#     recognizer = sr.Recognizer()
#     try:
#         print("Recognizing audio...")
#         text = recognizer.recognize_google(audio, language="en-US")  # you could adjust for other languages e.g. es-MX
#         return text
#     except sr.UnknownValueError:
#         print("Audio is not recognizable")
#         return None
#     except sr.RequestError as e:
#         print(f"Error while sending request to Google Speech Recognition: {e}")
#         return None

#Prompt text internal definition
def prepare_prompt(data, prompt):
    # prompt_internal = f"""
    # You are a network expert specialized in Ethernet, Automotive Ethernet, DoIP, CAN, ISO-TP, UDS, and all automotive protocols. The network and log data are provided in JSON format. Your task is to answer queries using the data from the JSON file. The query or question you need to answer is delimited by angle brackets.
    # If a calculation is required from the data, such as determining the total number of CAN IDs in the log file, perform the calculation, verify the output, and provide only the final result. If you are unable to perform the calculation, respond with "I wasn't able to do the calculation, please repeat your question."
    # """
    prompt_internal = f"""
    You are an expert on Pandas, specializing in DataFrame query functions,
    with extensive knowledge of various examples demonstrating their use. The dataframe data is provided in a JSON file.
    The question you need to answer is delimited by angle brackets.
    Your task is to create an expression that can be used inside Dataframe.query() to answer the given question using the dataframe.
    For example if the question is show all the data the answer would be index==index
    """
    promptsys = f"{prompt_internal}"
    promptuser = f"{data}\n\nQuery or question: < {prompt} >"
    messages = [{"role": "system", "content": promptsys}, {"role": "user", "content": promptuser}]
    return messages

def first_words(text, limit=4000):
    words = text.split()
    if len(words) <= limit:
        return text
    else:        
        return ' '.join(words[:limit])

