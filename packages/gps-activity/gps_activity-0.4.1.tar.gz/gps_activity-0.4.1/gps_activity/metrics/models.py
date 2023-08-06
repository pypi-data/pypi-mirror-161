from typing import Literal
from pydantic import BaseModel


class Metrics(BaseModel):
    recall: float
    precision: float
    beta: float
    fbeta_score: float
    status: Literal["success", "fail"] = "success"
    status_details: str = ""

    @classmethod
    def factory_failure_metrics(cls, beta: str, status_details: str):
        return cls(
            recall=-1,
            precision=-1,
            beta=beta,
            fbeta_score=-1,
            status="fail",
            status_details=status_details,
        )
