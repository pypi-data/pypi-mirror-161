from yams.buildobjs import EntityType, RelationDefinition, Boolean, String


class Agent(EntityType):
    name = String(unique=True)


class AgentKind(EntityType):
    name = String(required=True, vocabulary=["person", "family", "authority"])


class kind(RelationDefinition):
    subject = "Agent"
    object = "AgentKind"
    cardinality = "1*"
    inlined = True


class Activity(EntityType):
    name = String(required=True)


class associated_with(RelationDefinition):
    subject = "Activity"
    object = "Agent"
    cardinality = "?*"


class Thing(EntityType):
    identifier = String(unique=True)
    deleted = Boolean(required=True, default=False)
