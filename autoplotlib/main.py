# main module of autoplotlib

import langchain.chat_models
import langchain.schema
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def plot(
    prompt: str,
    data: object,
    openai_api_key: str = None,
    fig_args: dict = {},
    verbose: bool = False,
) -> None:
    """Plot data using matplotlib

    Args:
        prompt (str): prompt that explains the desired plot.
            Example: "plot the data as a line graph"
        data (object): Data to be plotted. Can be any object
            that matplotlib can plot. Example: a list of numbers,
            a numpy array, a pandas dataframe, etc.
        openai_api_key (str, optional): OpenAI API key. Defaults to None.
        fig_args (dict, optional): Arguments to pass to `plt.figure`.
    """

    if openai_api_key is None:
        try:
            openai_api_key = os.environ.get('OPEN_AI_KEY')
        except KeyError:
            raise ValueError(
                "You must provide an OpenAI API key. "
                "Either pass it as an argument to `plot` or set it as an environment variable. "
                "You can get one at https://beta.openai.com/."
            )

    if isinstance(data, pd.DataFrame):
        data_description = generate_df_description(data)
    elif isinstance(data, np.ndarray):
        data_description = f"The `data` variable is of type {type(data)} and has dimensions {data.shape}. The first 5 rows are: {data[:5]}."
    else:
        data_description = f"The `data` variable is of type {type(data)}."

    full_prompt = f"You are a Python programmer. Your job is to write Python code. Given a data set named `data`, please write Python code below to create a plot with matplotlib that satifies the following description: '{prompt}'. \n\n Note: you can assume that `data` is an existing variable that can be used. {data_description}. Remember to assume that `data` is an existing variable that can be used, do reset the `data` variable. \n\n Python code (as markdown Python code block):"

    # setup LLM API access
    llm = langchain.chat_models.ChatOpenAI(
        model_name="gpt-3.5-turbo", openai_api_key=openai_api_key
    )

    # if verbose:
    #     print(f"Prompting LLM with following prompt: {full_prompt}")

    # get plotting code from LLM
    # print("Prompting LLM for code... (this may take a few seconds)")
    llm_response = llm([langchain.schema.HumanMessage(content=full_prompt)]).content

    # extract the first code snippet from the LLM response
    # by matching the first instance of "```python" and the next instance of "```
    try:
        code = llm_response.split("```python")[1].split("```")[0]
    except IndexError:
        raise ValueError(
            "The LLM did not return any code. "
            "Please try again (maybe with a different prompt)."
            f"LLM response: {llm_response}"
        )

    # safety_user_input_str = f"Code generated by LLM: \n{code} \n\n Press y and enter to confirm that the code is safe and to run the code. Press any other key and enter to abort. Your input: "
    # if input(safety_user_input_str) != "y":
    #     raise ValueError("Code not confirmed as safe. Aborting.")

    if verbose:
        print(f"Code generated by LLM: {code}")

    fig = plt.figure(**fig_args)
    # run the code
    # for printing code
    # print(code) 
    exec(code, {"data": data, "fig": fig})

    # return code, fig, llm_response


def generate_df_description(df: pd.DataFrame) -> str:
    """Generate a description of a pandas dataframe.

    Args:
        df (pd.DataFrame): Pandas dataframe to describe.

    Returns:
        str: Description of the dataframe.
    """

    description = f"The dataframe has {df.shape[0]} rows and {df.shape[1]} columns. "
    description += f"The columns are named {list(df.columns)}. "
    description += f"The first 5 rows are: \n{df.head()}. "

    return description
