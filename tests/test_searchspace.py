"""Tests for the searchspace module."""

import numpy as np
import pandas as pd
import pytest

from baybe.constraints import (
    ContinuousCardinalityConstraint,
    ContinuousLinearEqualityConstraint,
    ContinuousLinearInequalityConstraint,
    DiscreteSumConstraint,
    ThresholdCondition,
)
from baybe.exceptions import EmptySearchSpaceError
from baybe.parameters import (
    CategoricalParameter,
    NumericalContinuousParameter,
    NumericalDiscreteParameter,
)
from baybe.searchspace import (
    SearchSpace,
    SearchSpaceType,
    SubspaceContinuous,
    SubspaceDiscrete,
)


def test_empty_parameters():
    """Creation of a search space with no parameters raises an exception."""
    with pytest.raises(EmptySearchSpaceError):
        SearchSpace()


def test_bounds_order():
    """Asserts that the bounds are created in the correct order.

    The correct order is discrete parameters first, continuous next.
    """
    parameters = [
        NumericalDiscreteParameter(name="A_disc", values=[1.0, 2.0, 3.0]),
        NumericalContinuousParameter(name="A_cont", bounds=(4.0, 6.0)),
        NumericalDiscreteParameter(name="B_disc", values=[7.0, 8.0, 9.0]),
        NumericalContinuousParameter(name="B_cont", bounds=(10.0, 12.0)),
    ]
    searchspace = SearchSpace.from_product(parameters=parameters)
    expected = np.array([[1.0, 7.0, 4.0, 10.0], [3.0, 9.0, 6.0, 12.0]])
    assert np.array_equal(
        searchspace.param_bounds_comp,
        expected,
    )


def test_empty_parameter_bounds():
    """Asserts that the correct bounds are produced for empty search spaces.

    Also checks for the correct shapes.
    """
    parameters = []
    searchspace_discrete = SubspaceDiscrete.from_product(parameters=parameters)
    searchspace_continuous = SubspaceContinuous(parameters=parameters)
    expected = np.empty((2, 0))
    assert np.array_equal(searchspace_discrete.param_bounds_comp, expected)
    assert np.array_equal(searchspace_continuous.param_bounds_comp, expected)


def test_discrete_searchspace_creation_from_dataframe():
    """A purely discrete search space is created from an example dataframe."""
    num_specified = NumericalDiscreteParameter(name="num_specified", values=[1, 2, 3])
    num_unspecified = NumericalDiscreteParameter(
        name="num_unspecified", values=[4, 5, 6]
    )
    cat_specified = CategoricalParameter(name="cat_specified", values=["a", "b", "c"])
    cat_unspecified = CategoricalParameter(
        name="cat_unspecified", values=["d", "e", "f"]
    )

    all_params = (num_specified, num_unspecified, cat_specified, cat_unspecified)

    df = pd.DataFrame({param.name: param.values for param in all_params})
    searchspace = SearchSpace(
        SubspaceDiscrete.from_dataframe(df, parameters=[num_specified, cat_specified])
    )

    assert searchspace.type == SearchSpaceType.DISCRETE
    assert searchspace.parameters == all_params
    assert df.equals(searchspace.discrete.exp_rep)


def test_continuous_searchspace_creation_from_bounds():
    """A purely continuous search space is created from example bounds."""
    parameters = (
        NumericalContinuousParameter("param1", (0, 1)),
        NumericalContinuousParameter("param2", (-1, 1)),
    )
    bounds = pd.DataFrame({p.name: p.bounds.to_tuple() for p in parameters})
    searchspace = SearchSpace(continuous=SubspaceContinuous.from_bounds(bounds))

    assert searchspace.type == SearchSpaceType.CONTINUOUS
    assert searchspace.parameters == parameters


def test_hyperrectangle_searchspace_creation():
    """A purely continuous search space is created that spans a certain set of points.

    As the name suggests, this searchspace is hyperrectangle- shaped
    """
    points = pd.DataFrame(
        {
            "param1": [0, 1, 2],
            "param2": [-1, 0, 1],
        }
    )
    searchspace = SearchSpace(continuous=SubspaceContinuous.from_dataframe(points))

    parameters = (
        NumericalContinuousParameter("param1", (0, 2)),
        NumericalContinuousParameter("param2", (-1, 1)),
    )

    assert searchspace.type == SearchSpaceType.CONTINUOUS
    assert searchspace.parameters == parameters


def test_invalid_constraint_parameter_combos():
    """Testing invalid constraint-parameter combinations."""
    parameters = [
        NumericalDiscreteParameter("d1", values=[1, 2, 3]),
        NumericalDiscreteParameter("d2", values=[0, 1, 2]),
        NumericalContinuousParameter("c1", (0, 2)),
        NumericalContinuousParameter("c2", (-1, 1)),
    ]

    # Attempting continuous constraint over hybrid parameter set
    with pytest.raises(ValueError):
        SearchSpace.from_product(
            parameters=parameters,
            constraints=[
                ContinuousLinearEqualityConstraint(
                    parameters=["c1", "c2", "d1"],
                )
            ],
        )

    # Attempting continuous constraint over hybrid parameter set
    with pytest.raises(ValueError):
        SearchSpace.from_product(
            parameters=parameters,
            constraints=[
                ContinuousLinearInequalityConstraint(
                    parameters=["c1", "c2", "d1"],
                )
            ],
        )

    # Attempting discrete constraint over hybrid parameter set
    with pytest.raises(ValueError):
        SearchSpace.from_product(
            parameters=parameters,
            constraints=[
                DiscreteSumConstraint(
                    parameters=["d1", "d2", "c1"],
                    condition=ThresholdCondition(threshold=1.0, operator=">"),
                )
            ],
        )

    # Attempting constraints over parameter set where a parameter does not exist
    with pytest.raises(ValueError):
        SearchSpace.from_product(
            parameters=parameters,
            constraints=[
                DiscreteSumConstraint(
                    parameters=["d1", "e7", "c1"],
                    condition=ThresholdCondition(threshold=1.0, operator=">"),
                )
            ],
        )

    # Attempting constraints over parameter set where a parameter does not exist
    with pytest.raises(ValueError):
        SearchSpace.from_product(
            parameters=parameters,
            constraints=[
                ContinuousLinearInequalityConstraint(
                    parameters=["c1", "e7", "d1"],
                )
            ],
        )


@pytest.mark.parametrize(
    "parameter_names",
    [
        [
            "Categorical_1",
            "Categorical_2",
            "Frame_A",
            "Some_Setting",
            "Num_disc_1",
            "Fraction_1",
            "Solvent_1",
            "Custom_1",
        ]
    ],
)
def test_searchspace_memory_estimate(searchspace: SearchSpace):
    """The memory estimate doesn't differ by more than 5% from the actual memory."""
    estimate = searchspace.estimate_product_space_size(searchspace.parameters)
    estimate_exp = estimate.exp_rep_bytes
    estimate_comp = estimate.comp_rep_bytes

    actual_exp = searchspace.discrete.exp_rep.memory_usage(deep=True, index=False).sum()
    actual_comp = searchspace.discrete.comp_rep.memory_usage(
        deep=True, index=False
    ).sum()

    assert 0.95 <= estimate_exp / actual_exp <= 1.05, (
        "Exp: ",
        estimate_exp,
        actual_exp,
    )
    assert 0.95 <= estimate_comp / actual_comp <= 1.05, (
        "Comp: ",
        estimate_comp,
        actual_comp,
    )


def test_invalid_continuous_cardinality_constraints_combos():
    """Testing invalid combinations of cardinality constraints.

    Any cardinality constraints share the same parameters.
    """
    parameters = [
        NumericalContinuousParameter("c1", (0, 2)),
        NumericalContinuousParameter("c2", (-1, 1)),
        NumericalContinuousParameter("c3", (-1, 1)),
        NumericalContinuousParameter("c4", (-1, 1)),
    ]

    # Attempting cardinality constraints sharing the same parameter
    with pytest.raises(ValueError):
        SearchSpace.from_product(
            parameters=parameters,
            constraints=[
                ContinuousCardinalityConstraint(
                    parameters=["c1", "c2", "c3"],
                    max_cardinality=1,
                ),
                ContinuousCardinalityConstraint(
                    parameters=["c3", "c4"],
                    max_cardinality=1,
                ),
            ],
        )
