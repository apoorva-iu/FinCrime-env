from typing import Any, Literal, Optional, List, Dict, Union
from pydantic import BaseModel, Field, ConfigDict

class Transaction(BaseModel):
    tx_id: str
    amount: float
    merchant: Optional[str] = None
    location: Optional[str] = None
    time: Optional[str] = None
    note: Optional[str] = None
    from_account: Optional[str] = Field(None, alias="from")
    to_account: Optional[str] = Field(None, alias="to")
    model_config = ConfigDict(populate_by_name=True)

class Account(BaseModel):
    account_id: str
    holder: Optional[str] = None
    account_type: Optional[str] = None
    type: Optional[str] = None
    balance: Optional[float] = 0.0

class TransferHop(BaseModel):
    from_account: Optional[str] = Field(None, alias="from")
    to_account: Optional[str] = Field(None, alias="to")
    amount: Optional[float] = None
    note: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)

class Email(BaseModel):
    from_addr: Optional[str] = Field(None, alias="from")
    to: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)

class SupportingDoc(BaseModel):
    type: str
    verified: bool = False
    doc_id: Optional[str] = None
    content: Optional[str] = None

class Observation(BaseModel):
    case_id: str
    task_id: str
    description: str
    instruction: Optional[str] = "Investigate the provided evidence and take action."
    step: int
    max_steps: int
    transactions: List[Transaction] = []
    accounts: List[Account] = []
    transfer_chain: List[TransferHop] = []
    emails: List[Email] = []
    supporting_docs: List[SupportingDoc] = []
    suspect: Optional[Dict[str, Any]] = None
    base_risk: float = 0.0

class FlagTransactionsAction(BaseModel):
    type: Literal["flag_transactions"] = "flag_transactions"
    tx_ids: List[str]
    risk_level: str

class IdentifyNetworkAction(BaseModel):
    type: Literal["identify_network"] = "identify_network"
    shell_accounts: List[str]
    source: str
    beneficiary: str

class InvestigateAction(BaseModel):
    type: Literal["investigate"] = "investigate"
    notes: str

class DeliverVerdictAction(BaseModel):
    type: Literal["deliver_verdict"] = "deliver_verdict"
    verdict: str
    crimes: List[str] = []
    evidence: List[str] = []
    reasoning: str

Action = Union[FlagTransactionsAction, IdentifyNetworkAction, InvestigateAction, DeliverVerdictAction]

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = {}

class StateResponse(BaseModel):
    observation: Observation
    reward: float = 0.0
    done: bool
    info: Dict[str, Any] = {}
