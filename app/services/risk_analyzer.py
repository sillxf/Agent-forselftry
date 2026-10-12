from app.schemas.alert import Alert


SEVERITY_SCORE = {

    "low":10,

    "medium":30,

    "high":70,

    "critical":90
}



def calculate_risk_score(
    alert: Alert
)->int:


    score = SEVERITY_SCORE[
        alert.severity
    ]


    if (
        "authentication"
        in alert.tags
    ):
        score +=10


    if (
        "suspicious"
        in alert.title.lower()
    ):
        score +=10


    return min(score,100)

def analyze_alert(
    alert:Alert
):

    return {

        "alert_id":alert.id,

        "risk_score":
            calculate_risk_score(alert),

        "priority":
            (
            "urgent"
            if calculate_risk_score(alert)>80
            else "normal"
            )

    }