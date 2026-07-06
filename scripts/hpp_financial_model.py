#!/usr/bin/env python3
"""Preliminary hydropower financial screening model.

The model is intentionally simple so it can be adapted quickly during FS,
market-sounding, and bid-strategy work.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class HPPInputs:
    capacity_mw: float
    generation_gwh: float
    capex_usd: float
    opex_pct: float
    construction_years: int
    operation_years: int
    discount_rate: float
    debt_ratio: float
    debt_rate: float
    debt_tenor: int
    tax_rate: float
    energy_tariff_usd_mwh: float
    capacity_tariff_kzt_mw_month: float
    kzt_usd: float


def pmt(rate: float, nper: int, pv: float) -> float:
    if rate == 0:
        return -(pv / nper)
    return -(rate * pv) / (1 - (1 + rate) ** -nper)


def npv(rate: float, values: pd.Series) -> float:
    return sum(value / ((1 + rate) ** idx) for idx, value in enumerate(values, start=1))


def irr(values: pd.Series) -> float:
    cashflows = list(values)

    def f(rate: float) -> float:
        return sum(cf / ((1 + rate) ** idx) for idx, cf in enumerate(cashflows, start=1))

    low, high = -0.95, 1.0
    f_low, f_high = f(low), f(high)
    while f_low * f_high > 0 and high < 10:
        high *= 2
        f_high = f(high)
    if f_low * f_high > 0:
        return float("nan")
    for _ in range(200):
        mid = (low + high) / 2
        f_mid = f(mid)
        if abs(f_mid) < 1e-7:
            return mid
        if f_low * f_mid <= 0:
            high, f_high = mid, f_mid
        else:
            low, f_low = mid, f_mid
    return (low + high) / 2


def build_model(inputs: HPPInputs) -> tuple[pd.DataFrame, dict[str, float]]:
    generation_mwh = inputs.generation_gwh * 1000.0
    annual_energy_revenue = generation_mwh * inputs.energy_tariff_usd_mwh
    annual_capacity_revenue = (
        inputs.capacity_tariff_kzt_mw_month * inputs.capacity_mw * 12.0 / inputs.kzt_usd
    )
    annual_opex = inputs.capex_usd * inputs.opex_pct

    capex_shape = np.ones(inputs.construction_years) / inputs.construction_years
    capex_draws = capex_shape * inputs.capex_usd
    debt_amount = inputs.capex_usd * inputs.debt_ratio
    annual_debt_service = -pmt(inputs.debt_rate, inputs.debt_tenor, debt_amount)

    rows = []
    for year in range(1, inputs.construction_years + inputs.operation_years + 1):
        if year <= inputs.construction_years:
            capex = capex_draws[year - 1]
            project_cf = -capex
            equity_cf = -capex * (1.0 - inputs.debt_ratio)
            revenue = ebitda = debt_service = tax = 0.0
            dscr = np.nan
        else:
            op_year = year - inputs.construction_years
            capex = 0.0
            revenue = annual_energy_revenue + annual_capacity_revenue
            ebitda = revenue - annual_opex
            debt_service = annual_debt_service if op_year <= inputs.debt_tenor else 0.0
            taxable_cash = ebitda - debt_service
            tax = max(taxable_cash * inputs.tax_rate, 0.0)
            project_cf = ebitda - tax
            equity_cf = ebitda - debt_service - tax
            dscr = ebitda / debt_service if debt_service else np.nan

        rows.append(
            {
                "year": year,
                "capex_usd": capex,
                "revenue_usd": revenue,
                "ebitda_usd": ebitda,
                "debt_service_usd": debt_service,
                "tax_usd": tax,
                "project_cf_usd": project_cf,
                "equity_cf_usd": equity_cf,
                "dscr": dscr,
            }
        )

    df = pd.DataFrame(rows)
    discounted_generation = sum(
        generation_mwh / ((1 + inputs.discount_rate) ** y)
        for y in range(inputs.construction_years + 1, inputs.construction_years + inputs.operation_years + 1)
    )
    discounted_cost = sum(
        (max(-cf, 0.0) + annual_opex * (1 if y > inputs.construction_years else 0))
        / ((1 + inputs.discount_rate) ** y)
        for y, cf in zip(df["year"], df["project_cf_usd"])
    )

    metrics = {
        "capacity_factor": generation_mwh / (inputs.capacity_mw * 8760.0),
        "annual_energy_revenue_usd": annual_energy_revenue,
        "annual_capacity_revenue_usd": annual_capacity_revenue,
        "project_npv_usd": npv(inputs.discount_rate, df["project_cf_usd"]),
        "project_irr": irr(df["project_cf_usd"]),
        "equity_irr": irr(df["equity_cf_usd"]),
        "min_dscr": df["dscr"].dropna().min(),
        "lcoe_usd_mwh": discounted_cost / discounted_generation,
    }
    return df, metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a preliminary HPP financial model.")
    parser.add_argument("--capacity-mw", type=float, required=True)
    parser.add_argument("--generation-gwh", type=float, required=True)
    parser.add_argument("--capex-usd", type=float, required=True)
    parser.add_argument("--capacity-tariff-kzt-mw-month", type=float, default=15_000_000)
    parser.add_argument("--energy-tariff-usd-mwh", type=float, default=35.0)
    parser.add_argument("--kzt-usd", type=float, default=520.0)
    parser.add_argument("--opex-pct", type=float, default=0.018)
    parser.add_argument("--construction-years", type=int, default=5)
    parser.add_argument("--operation-years", type=int, default=35)
    parser.add_argument("--discount-rate", type=float, default=0.10)
    parser.add_argument("--debt-ratio", type=float, default=0.70)
    parser.add_argument("--debt-rate", type=float, default=0.08)
    parser.add_argument("--debt-tenor", type=int, default=15)
    parser.add_argument("--tax-rate", type=float, default=0.20)
    parser.add_argument("--csv-out", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_kwargs = vars(args).copy()
    csv_out = input_kwargs.pop("csv_out")
    inputs = HPPInputs(**input_kwargs)
    df, metrics = build_model(inputs)

    for key, value in metrics.items():
        print(f"{key}: {value:,.4f}")

    if csv_out:
        df.to_csv(csv_out, index=False)
        print(f"saved_csv: {csv_out}")


if __name__ == "__main__":
    main()
