def get_prompt(method, query, top_passages_str, **kwargs):
    """Return the appropriate user prompt based on the expansion method."""  
    user_prompts = {
    "thinkqe": f"""Given a question \"{query}\" and its possible answering passages (most of these passages are wrong) enumerated as:
{top_passages_str}

please write a correct answering passage. Use your own knowledge, not just the example passages!""",
    }

    return user_prompts[method]