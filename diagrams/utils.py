import contextvars

# Global contexts for a diagrams and a cluster.
#
# These global contexts are for letting the clusters and nodes know
# where context they are belong to. So the all clusters and nodes does
# not need to specify the current diagrams or cluster via parameters.
__diagram = contextvars.ContextVar("diagrams")
__cluster = contextvars.ContextVar("cluster")

def getdiagram():
    try:
        return __diagram.get()
    except LookupError:
        raise EnvironmentError("Global diagrams context not set up")


def setdiagram(diagram):
    __diagram.set(diagram)


def getcluster():
    try:
        return __cluster.get()
    except LookupError:
        return None


def setcluster(cluster):
    __cluster.set(cluster)

def new_init(cls, init):
    def reset_init(*args, **kwargs):
        cls.__init__ = init

    return reset_init
