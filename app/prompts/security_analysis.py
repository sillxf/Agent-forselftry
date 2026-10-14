SECURITY_ANALYSIS_PROMPT = """

You are a security analyst.

Analyze this alert.

Alert:
{alert}

Risk:
{risk}

Knowledge:
{knowledge}

Return ONLY JSON.

Format:

{{
"attack_type":"",
"confidence":0.0,
"evidence":[],
"recommendations":[]
}}

"""