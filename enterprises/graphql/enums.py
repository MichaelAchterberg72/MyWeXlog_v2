import graphene

# EnterpriseFCEnum = create_enum_from_choices(Enterprise.FC)
# BranchSizeEnum = create_enum_from_choices(Branch.SZE)

class EnterpriseFCEnum(graphene.Enum):
    P = 'Public'
    S = 'System'
    
class BranchSizeEnum(graphene.Enum):
    A = "1-10"
    B = "11-50"
    C = "51-150"
    D = "151-500"
    E = "501-1 000"
    F = "1 001-10 000"
    G = "10 001+"