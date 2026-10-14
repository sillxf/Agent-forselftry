import json

from app.schemas.analysis import SecurityAnalysis


def parse_analysis(
    text:str
):

    data=json.loads(text)
    
    return SecurityAnalysis(
        **data
    )