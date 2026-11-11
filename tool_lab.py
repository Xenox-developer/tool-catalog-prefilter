"""Implementation target for fixed INVARIANT acceptance."""
STOPWORDS=frozenset('a an the and or to of in on for with our by from at as is it this that use search find look up exact text return most results preserve quoted verbatim'.split())


def select_tools(request, tools, k=4):
    raise NotImplementedError


def score(response, expected, available_names=None):
    raise NotImplementedError
