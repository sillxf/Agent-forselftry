SECURITY_ANALYSIS_PROMPT = """

You are an experienced security analyst.

Analyze this alert.

Alert:
{alert}

Risk:
{risk}

Knowledge:
{knowledge}


Return:

1. Attack type
2. Evidence
3. Risk explanation
4. Recommended actions

"""