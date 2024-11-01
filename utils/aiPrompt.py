from os import getenv
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
  api_key = getenv("OPENAI_API_KEY", default = ""),
)

#Open AI settings 
def get_completion(prompt, model="gpt-3.5-turbo", temperature=0):
  completion = client.chat.completions.create(
      messages=prompt,
      model= model,
      temperature=temperature,
  )
  return completion.choices[0].message.content

#Dataframe expert AI prompt
def prepare_eval_prompt(data, prompt):
    prompt_internal = f"""
    You are a Pandas DataFrame expert. You will receive a DataFrame in JSON format named 'df'.
    Your task is to create an expression to be used with eval() to answer the question enclosed in angle brackets. 
    For example, for the question: <show all rows where 'identifier' is '310'>, provide: df[df['identifier'] == '310'].
    """
    promptsys = f"{prompt_internal}"
    promptuser = f"{data}\n\nQuery or question: < {prompt} >"
    messages = [{"role": "system", "content": promptsys}, {"role": "user", "content": promptuser}]
    return messages

#Regular expressions AI prompt
def prepare_regex_prompt(prompt):
    prompt_internal = f"""
    You are an AI assistant proficient in creating regular expressions (regex).
    Your task is to help generate regex patterns that can be used in re.search based on user-provided search prompts.
    Provide only the regular expression pattern without any additional explanation.
    """
    promptsys = f"{prompt_internal}"
    promptuser = f"Please generate a regular expression for the following search prompt: {prompt}"
    messages = [{"role": "system", "content": promptsys}, {"role": "user", "content": promptuser}]
    return messages

#Scapy packets AI prompt
def prepare_scapy_prompt(prompt):
    prompt_internal = f"""
    You are an AI assistant helping to expand a list of important fields for various network protocol layers.
    Provide concise, accurate information.
    """
    promptsys = f"{prompt_internal}"
    promptuser = f"Please list the important fields for the {prompt} layer in Scapy, separated by commas."
    messages = [{"role": "system", "content": promptsys}, {"role": "user", "content": promptuser}]
    return messages

  ## Add another prep prompt to analyze just the payloads
    # prompt_internal = f"""
    # You are a network expert specialized in Ethernet, Automotive Ethernet, DoIP, CAN, ISO-TP, UDS, and all automotive protocols. The network and log data are provided in JSON format. Your task is to answer queries using the data from the JSON file. The query or question you need to answer is delimited by angle brackets.
    # If a calculation is required from the data, such as determining the total number of CAN IDs in the log file, perform the calculation, verify the output, and provide only the final result. If you are unable to perform the calculation, respond with "I wasn't able to do the calculation, please repeat your question."
    # """