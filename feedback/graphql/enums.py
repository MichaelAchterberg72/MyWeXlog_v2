import graphene

class OPTSEnum(graphene.Enum):
    X = 'Select'
    B = 'Bug'
    T = 'Comment'
    S = 'Suggestion'
    F = 'Request Feature'
    C = 'Complaint'
    M = 'Compliance'
    M = 'I Got A Job'