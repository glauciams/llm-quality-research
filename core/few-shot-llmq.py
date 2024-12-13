import os
from dotenv import load_dotenv
#import gradio as gr
from langchain_openai import ChatOpenAI
import pandas as pd

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(temperature=0, api_key=api_key)

# Define a few-shot prompt with examples
few_shot_prompt = """
Here are some examples of how to solve problems:

Add here some questions

Now solve this problem:
{question}
"""

def call_llm_with_few_shot(text):
    # Append the user's input to the few-shot prompt
    prompt = few_shot_prompt.format(question=text)
    response_llm = llm.invoke(prompt)

    print(response_llm)
    return response_llm

# Load the dataset
df = pd.read_csv("./data/glaucia.csv")

# Apply the few-shot prompt to each question
df['llm_answer'] = df['question'].apply(call_llm_with_few_shot)

# Save the results
df.to_csv("./data/questions_answered_few_shot.csv")
