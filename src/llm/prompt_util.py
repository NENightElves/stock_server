from langchain.prompts import PromptTemplate


def prompt_once_stock(llm, stock_code, stock_data='', stream=False):
    pstr = """
这是股票{stock_code}的代码。
这是这支股票的交易数据：
{stock_data}
请对这支股票进行简洁的分析，然后告知我交易策略，包括如何买进卖出以及当前的策略。
    """
    fdict = {
        "stock_code": stock_code,
        "stock_data": stock_data
    }
    prompt_template = PromptTemplate.from_template(pstr)
    chain = prompt_template | llm
    if stream:
        return chain.stream(fdict)
    else:
        return chain.invoke(fdict).content
