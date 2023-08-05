from .compositions import or_contract
from ..interface import Contract, ContractNotRespected, describe_type
from ..pyparsing_utils import myOperatorPrecedence
from ..syntax import (
    add_contract,
    alphanums,
    W,
    contract_expression,
    O,
    S,
    rvalue,
    simple_contract,
    ZeroOrMore,
    Literal,
    MatchFirst,
    opAssoc,
    FollowedBy,
    NotAny,
    Keyword,
    add_keyword,
    Word,
)
from .compositions import And, OR
from .suggester import create_suggester
from numpy import ndarray, dtype
import numpy
import jax
import types
from jaxlib.xla_extension import DeviceArray
from pyparsing import infixNotation as operatorPrecedence, Or


class Method(Contract):
    def __init__(self, method_str: str, inner_contract: Contract, where=None):
        Contract.__init__(self, where)
        self.method_str = method_str
        self.inner_contract = inner_contract

    def check_contract(self, context, value, silent):
        if not isinstance(self.inner_contract, Contract):
            raise ValueError(
                f"bad contract {self.inner_contract} for method/var {self.method_str}"
            )
        if not hasattr(value, self.method_str):
            error = f"Expected member method or variable {self.method_str} for {describe_type(value)}"
            raise ContractNotRespected(
                contract=self, error=error, value=value, context=context
            )
        _value = value
        # TODO: pass options for handling jax.
        if isinstance(value, DeviceArray):
            _value = value.to_py()

        if isinstance(
            getattr(_value, self.method_str),
            (types.BuiltinMethodType, types.MethodType),
        ):
            # TODO: support currying.
            self.inner_contract._check_contract(
                context, getattr(_value, self.method_str)(), silent
            )
        else:
            self.inner_contract._check_contract(
                context, getattr(_value, self.method_str), silent
            )

    def __str__(self):
        s = f"prop[{self.method_str}]({self.inner_contract})"
        return s

    def __repr__(self):
        s = f"Method({self.method_str},{self.inner_contract.__repr__()})"
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        method_str = tokens.get("method_str")[0]
        inner_contract = tokens.get("inner_contract")

        assert isinstance(method_str, str)
        assert isinstance(inner_contract, Contract)
        return Method(method_str, inner_contract, where=where)


method_str = (S("[") - Word(alphanums + "_") - S("]"))("method_str")
inner_contract = ((S("(") - contract_expression - S(")")) | or_contract)(
    "inner_contract"
)

name = Keyword("meth") | Keyword("prop")
method_contract = name - method_str - inner_contract
method_contract.set_name("method contract")
add_contract(method_contract.setParseAction(Method.parse_action))

add_keyword("meth")
add_keyword("prop")
