from __future__ import annotations

__all__ = [
    "_AbstractStoichiometricModel",
    "_AbstractRateModel",
]

from abc import ABC, abstractmethod
from typing import Dict, List, Set, Union

import numpy as np
import pandas as pd

from ...core import (
    AlgebraicMixin,
    BaseModel,
    CompoundMixin,
    RateMixin,
    StoichiometricMixin,
)
from ...typing import Array, ArrayLike


class _AbstractStoichiometricModel(StoichiometricMixin, CompoundMixin, BaseModel, ABC):
    @abstractmethod
    def _get_rhs(self, t: Union[float, ArrayLike], y: List[Array]) -> Array:
        pass


class _AbstractRateModel(RateMixin, AlgebraicMixin, _AbstractStoichiometricModel):
    def _collect_used_parameters(self) -> Set[str]:
        used_parameters = set()
        for par in self.derived_parameters.values():
            used_parameters.update(par["parameters"])
        for module in self.algebraic_modules.values():
            used_parameters.update(module.parameters)
        for rate in self.rates.values():
            used_parameters.update(rate.parameters)
        return used_parameters

    def check_unused_parameters(self) -> Set[str]:
        used_parameters = self._collect_used_parameters()
        return set(self.parameters).difference(used_parameters)

    def check_missing_parameters(self) -> Set[str]:
        used_parameters = self._collect_used_parameters()
        return used_parameters.difference(self.parameters)

    def remove_unused_parameters(self) -> None:
        self.remove_parameters(self.check_unused_parameters())

    def _collect_used_compounds(self) -> Set[str]:
        return set((i for i in self.compounds if len(self.stoichiometries_by_compounds[i]) > 0))

    def check_unused_compounds(self) -> Set[str]:
        used_compounds = self._collect_used_compounds()
        return used_compounds.difference(self.compounds)

    def remove_unused_compounds(self) -> None:
        self.remove_compounds(self.check_unused_compounds())

    @abstractmethod
    def get_full_concentration_dict(
        self,
        y: Union[Dict[str, float], Dict[str, Array], ArrayLike, Array],
        t: Union[float, ArrayLike, Array] = 0.0,
    ) -> Dict[str, Array]:
        ...

    @abstractmethod
    def get_fluxes_dict(
        self,
        y: Union[
            Dict[str, float],
            Dict[str, ArrayLike],
            Dict[str, Array],
            Array,
            ArrayLike,
        ],
        t: Union[float, ArrayLike, Array] = 0.0,
    ) -> Dict[str, Array]:
        ...

    def get_fluxes_array(
        self,
        y: Union[
            Dict[str, float],
            Dict[str, ArrayLike],
            Dict[str, Array],
            Array,
            ArrayLike,
        ],
        t: Union[float, ArrayLike, Array] = 0.0,
    ) -> Array:
        """Calculate the fluxes at time point(s) t."""
        return np.array(list(self.get_fluxes_dict(y=y, t=t).values())).T

    def get_fluxes_df(
        self,
        y: Union[
            Dict[str, float],
            Dict[str, ArrayLike],
            Dict[str, Array],
            Array,
            ArrayLike,
        ],
        t: Union[float, ArrayLike, Array] = 0.0,
    ) -> pd.DataFrame:
        """Calculate the fluxes at time point(s) t."""
        if isinstance(t, (int, float)):
            t = [t]  # type: ignore
        return pd.DataFrame(data=self.get_fluxes_dict(y=y, t=t), index=t, columns=self.get_rate_names())

    def get_right_hand_side(
        self,
        y: Union[
            Dict[str, float],
            Dict[str, ArrayLike],
            Dict[str, Array],
            Array,
            ArrayLike,
        ],
        t: Union[float, ArrayLike, Array] = 0.0,
    ) -> Dict[str, float]:
        """Calculate the right hand side of the ODE system."""
        self._update_derived_parameters()
        fcd = self.get_full_concentration_dict(y=y, t=t)  # type: ignore
        fcd_array = [fcd[i] for i in self.get_compounds()]
        rhs = self._get_rhs(t=t, y=fcd_array)
        eqs = [f"d{cpd}dt" for cpd in self.get_compounds()]
        return dict(zip(eqs, rhs))
