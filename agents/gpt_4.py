from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os


llm = OpenAI(temperature=0.9, model_name=os.environ.get("OPENAI_MODEL", "gpt-4"))


def gpt_4_agent(issue):
    """Uses GPT-4 to accomplish an issue. Does not use any tools."""
    template = """
    You have been given this task:
    {task}

    ---
    Your Response:

    """

    prompt = PromptTemplate(
        input_variables=["task"],
        template=template,
    )

    from langchain.chains import LLMChain

    chain = LLMChain(llm=llm, prompt=prompt)
    # chain_run = chain.run({"task": issue, "summary": get_project_summary(issue)})
    chain_run = chain.run({"task": issue})
    return chain_run