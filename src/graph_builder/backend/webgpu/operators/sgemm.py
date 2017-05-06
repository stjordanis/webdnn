from typing import Type, Optional, Iterable

import numpy as np

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import AxisOrder


class Sgemm(Operator):
    attributes = {PostElementwise,
                  PostAxiswise,
                  HaveWeights}

    def __init__(self, name: Optional[str], M: int, N: int, K: int, out_shape: Iterable[int], out_order: Type[AxisOrder],
                 transpose_A: bool, transpose_B: bool):
        super().__init__(name)

        # NOTE: out_shapeをIterableではなくCollectionにすればこれは解決する
        #       しかしPyCharmでは issubclass(List[int], Collection[int]) がTrueにならない（バグ？）ため、
        #       やむを得ずこのようにしている
        #
        # noinspection PyTypeChecker
        assert len(out_shape) == out_order.ndim
        assert np.product(out_shape) == M * N

        self.parameters["M"] = M
        self.parameters["N"] = N
        self.parameters["K"] = K
        self.parameters["out_shape"] = out_shape
        self.parameters["out_order"] = out_order
        self.parameters["transpose_A"] = transpose_A
        self.parameters["transpose_B"] = transpose_B

    def __call__(self, A: Variable, B: Variable):
        assert A.size == self.M * self.K
        assert B.size == self.N * self.K

        self.append_input("A", A)
        self.append_input("B", B)

        C = Variable(
            self.parameters["out_shape"],
            self.parameters["out_order"]
        )
        self.append_output("C", C)

        return C,

    @property
    def M(self) -> int:
        return int(self.parameters["M"])

    @property
    def N(self) -> int:
        return int(self.parameters["N"])

    @property
    def K(self) -> int:
        return int(self.parameters["K"])

    @property
    def transpose_A(self) -> bool:
        return bool(self.parameters["transpose_A"])

    @property
    def transpose_B(self) -> bool:
        return bool(self.parameters["transpose_B"])
