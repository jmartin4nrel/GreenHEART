import copy
from typing import Dict, Union, Optional, Tuple

import ProFAST
import pandas as pd
from attrs import define, Factory, field

import os
from pathlib import Path
import importlib
from hopp.utilities import load_yaml

# Get model locations loaded up to refer to
CD = Path(__file__).parent
model_locs_fp = CD / 'model_locations.yaml'
model_locs = load_yaml(model_locs_fp)

@define
class Feedstocks:
    #NOTE:
        # left iron_ore_pellet_unitcost and iron_ore_consumption as is, I believe these will likely be deleted as they are not feedstocks for iron ore mining
        # updated references of 'iron' to 'iron_ore' where applicable, however not all X_consumption attributes will be applicable to iron ore mining
        # thoughts on items to delete / not applicable for iron ore:
            # excess_oxygen
            # lime_unitcost
            # iron_ore_pellet_unitcost
            # oxygen_market_price
            # iron_ore_consumption
            # lime_consumption
            # carbon_consumption
            # hydrogen_consumption
            # slag_disposal_unitcost
            # slag_production
        # thoughts on items to add for iron ore:
            # oil/gas/diesel_consumption

    """
    Represents the consumption rates and costs of various feedstocks used in iron ore mining
    production.

    Attributes:
        natural_gas_prices (Dict[str, float]):
            Natural gas costs, indexed by year ($/GJ).
        excess_oxygen (float): Excess oxygen produced (kgO2), default = 395.
        lime_unitcost (float): Cost per metric tonne of lime ($/metric tonne).
        carbon_unitcost (float): Cost per metric tonne of carbon ($/metric tonne).
        electricity_cost (float):
            Electricity cost per metric tonne of iron ore production ($/metric tonne).
        iron_ore_pellet_unitcost (float):
            Cost per metric tonne of iron ore ($/metric tonne).
        oxygen_market_price (float):
            Market price per kg of oxygen ($/kgO2).
        raw_water_unitcost (float):
            Cost per metric tonne of raw water ($/metric tonne).
        iron_ore_consumption (float):
            Iron ore consumption per metric tonne of iron production (metric tonnes).
        raw_water_consumption (float):
            Raw water consumption per metric tonne of iron ore production (metric tonnes).
        lime_consumption (float):
            Lime consumption per metric tonne of iron ore production (metric tonnes).
        carbon_consumption (float):
            Carbon consumption per metric tonne of iron ore production (metric tonnes).
        hydrogen_consumption (float):
            Hydrogen consumption per metric tonne of iron ore production (metric tonnes).
        natural_gas_consumption (float):
            Natural gas consumption per metric tonne of iron ore production (GJ-LHV).
        electricity_consumption (float):
            Electricity consumption per metric tonne of iron ore production (MWh).
        slag_disposal_unitcost (float):
            Cost per metric tonne of slag disposal ($/metric tonne).
        slag_production (float):
            Slag production per metric tonne of iron production (metric tonnes).
        maintenance_materials_unitcost (float):
            Cost per metric tonne of annual iron ore slab production at real capacity
            factor ($/metric tonne).
    """

    natural_gas_prices: Dict[str, float]
    excess_oxygen: float = 395
    lime_unitcost: float = 122.1
    carbon_unitcost: float = 236.97
    electricity_cost: float = 48.92
    iron_ore_pellet_unitcost: float = 207.35
    oxygen_market_price: float = 0.03
    raw_water_unitcost: float = 0.59289
    iron_ore_consumption: float = 1.62927
    raw_water_consumption: float = 0.80367
    lime_consumption: float = 0.01812
    carbon_consumption: float = 0.0538
    hydrogen_consumption: float = 0.06596
    natural_gas_consumption: float = 0.71657
    electricity_consumption: float = 0.5502
    slag_disposal_unitcost: float = 37.63
    slag_production: float = 0.17433
    maintenance_materials_unitcost: float = 7.72


@define
class IronOreCostModelConfig:
    # NOTE: updated references of 'iron' to 'iron_ore', however unsure if all attributes will be applicable to iron ore
    """
    Configuration for the iron ore cost model, including operational parameters and
    feedstock costs.

    Attributes:
        operational_year (int): The year of operation for cost estimation.
        plant_capacity_mtpy (float): Plant capacity in metric tons per year.
        lcoh (float): Levelized cost of hydrogen ($/kg).
        feedstocks (Feedstocks):
            An instance of the Feedstocks class containing feedstock consumption
            rates and costs.
        o2_heat_integration (bool):
            Indicates whether oxygen and heat integration is used, affecting preheating
            CapEx, cooling CapEx, and oxygen sales. Default is True.
        co2_fuel_emissions (float):
            CO2 emissions from fuel per metric tonne of iron ore production.
        co2_carbon_emissions (float):
            CO2 emissions from carbon per metric tonne of iron ore production.
        surface_water_discharge (float):
            Surface water discharge per metric tonne of iron ore production.
    """

    operational_year: int
    plant_capacity_mtpy: float
    lcoh: float
    capex_misc: float
    feedstocks: Feedstocks
    o2_heat_integration: bool = True
    co2_fuel_emissions: float = 0.03929
    co2_carbon_emissions: float = 0.17466
    surface_water_discharge: float = 0.42113
    cost_model: Optional[dict] = field(default=None)


@define
class IronOreCosts:
    # NOTE: 
        # updated references of 'iron' to 'iron_ore', however unsure if all attributes will be applicable to iron ore
        # thoughts on items to delete / not applicable to iron ore:
            # eaf_casting, shaft_furnace, h2_preheating, cooling_tower, piping
        # thoughts on items to add for iron ore:
            # capex for equipment / infrastructure related to mining
    """
    Base dataclass for calculated iron ore costs.

    Attributes:
        capex_eaf_casting (float):
            Capital expenditure for electric arc furnace and casting.
        capex_shaft_furnace (float): Capital expenditure for shaft furnace.
        capex_oxygen_supply (float): Capital expenditure for oxygen supply.
        capex_h2_preheating (float): Capital expenditure for hydrogen preheating.
        capex_cooling_tower (float): Capital expenditure for cooling tower.
        capex_piping (float): Capital expenditure for piping.
        capex_elec_instr (float):
            Capital expenditure for electrical and instrumentation.
        capex_buildings_storage_water (float):
            Capital expenditure for buildings, storage, and water service.
        capex_misc (float):
            Capital expenditure for miscellaneous items.
        labor_cost_annual_operation (float): Annual operating labor cost.
        labor_cost_maintenance (float): Maintenance labor cost.
        labor_cost_admin_support (float): Administrative and support labor cost.
        property_tax_insurance (float): Cost for property tax and insurance.
        land_cost (float): Cost of land.
        installation_cost (float): Cost of installation.

    Note:
        These represent the minimum set of required cost data for
        `run_iron_ore_finance_model`, as well as base data for `IronOreCostModelOutputs`.
    """

    capex_eaf_casting: float
    capex_shaft_furnace: float
    capex_oxygen_supply: float
    capex_h2_preheating: float
    capex_cooling_tower: float
    capex_piping: float
    capex_elec_instr: float
    capex_buildings_storage_water: float
    capex_misc: float
    labor_cost_annual_operation: float
    labor_cost_maintenance: float
    labor_cost_admin_support: float
    property_tax_insurance: float
    land_cost: float
    installation_cost: float


@define
class IronOreCostModelOutputs(IronOreCosts):
    """
    Outputs of the iron ore cost model, extending the IronOreCosts data with total
    cost calculations and specific cost components related to the operation and
    installation of a iron ore mining plant.

    Attributes:
        total_plant_cost (float):
            The total capital expenditure (CapEx) for the iron ore mining plant.
        total_fixed_operating_cost (float):
            The total annual operating expenditure (OpEx), including labor,
            maintenance, administrative support, and property tax/insurance.
        labor_cost_fivemonth (float):
            Cost of labor for the first five months of operation, often used in startup
            cost calculations.
        maintenance_materials_onemonth (float):
            Cost of maintenance materials for one month of operation.
        non_fuel_consumables_onemonth (float):
            Cost of non-fuel consumables for one month of operation.
        waste_disposal_onemonth (float):
            Cost of waste disposal for one month of operation.
        monthly_energy_cost (float):
            Cost of energy (electricity, natural gas, etc.) for one month of operation.
        spare_parts_cost (float):
            Cost of spare parts as part of the initial investment.
        misc_owners_costs (float):
            Miscellaneous costs incurred by the owner, including but not limited to,
            initial supply stock, safety equipment, and initial training programs.
    """

    total_plant_cost: float
    total_fixed_operating_cost: float
    labor_cost_fivemonth: float
    maintenance_materials_onemonth: float
    non_fuel_consumables_onemonth: float
    waste_disposal_onemonth: float
    monthly_energy_cost: float
    spare_parts_cost: float
    misc_owners_costs: float

@define
class IronOreCapacityModelConfig:
    # NOTE: updated references of 'iron' to 'iron_ore', however unsure if all attributes will be applicable to iron ore
    """
    Configuration inputs for the iron ore capacity sizing model, including plant capacity and
    feedstock details.

    Attributes:
        hydrogen_amount_kgpy Optional (float): The amount of hydrogen available in kilograms 
            per year to make iron ore.
        desired_iron_ore_mtpy Optional (float): The amount of desired iron ore production in
            metric tonnes per year.
        input_capacity_factor_estimate (float): The estimated iron ore plant capacity factor.
        feedstocks (Feedstocks): An instance of the `Feedstocks` class detailing the
            costs and consumption rates of resources used in production.
    """
    input_capacity_factor_estimate: float
    feedstocks: Feedstocks
    hydrogen_amount_kgpy: Optional[float] = field(default=None)
    desired_iron_ore_mtpy: Optional[float] = field(default=None)
    performance_model: Optional[dict] = field(default=None)


    def __attrs_post_init__(self):
        if self.hydrogen_amount_kgpy is None and self.desired_iron_ore_mtpy is None:
            raise ValueError("`hydrogen_amount_kgpy` or `desired_iron_ore_mtpy` is a required input.")

        if self.hydrogen_amount_kgpy and self.desired_iron_ore_mtpy:
            raise ValueError("can only select one input: `hydrogen_amount_kgpy` or `desired_iron_ore_mtpy`.")

@define
class IronOreCapacityModelOutputs:
    # NOTE: updated references of 'iron' to 'iron_ore', however unsure if all attributes will be applicable to iron ore
    """
    Outputs from the iron ore size model.

    Attributes:
        iron_ore_plant_size_mtpy (float): If amount of hydrogen in kilograms per year is input, 
            the size of the iron ore mining plant in metric tonnes per year is output.
        hydrogen_amount_kgpy (float): If amount of iron ore production in metric tonnes per year is input, 
            the amount of necessary hydrogen feedstock in kilograms per year is output.
    """
    iron_ore_plant_capacity_mtpy: float
    hydrogen_amount_kgpy: float


def run_size_iron_ore_plant_capacity(config: IronOreCapacityModelConfig) -> IronOreCapacityModelOutputs:
    # NOTE: updated references of 'iron' to 'iron_ore', however unsure if all attributes will be applicable to iron ore
    """
    Calculates either the annual iron ore production in metric tons based on plant capacity and
    available hydrogen or the amount of required hydrogen based on a desired iron ore production.

    Args:
        config (IronOreCapacityModelConfig):
            Configuration object containing all necessary parameters for the capacity sizing,
            including capacity factor estimate and feedstock costs.

    Returns:
        IronOreCapacityModelOutputs: An object containing iron ore mining plant capacity in metric tons
        per year and amount of hydrogen required in kilograms per year.

    """

    # If performance model name is "placeholder", use the code that was copied over from Green Steel
    if config.performance_model['name'] == 'placeholder':

        if config.hydrogen_amount_kgpy:
            iron_ore_plant_capacity_mtpy = (config.hydrogen_amount_kgpy 
                / 1000
                / config.feedstocks.hydrogen_consumption 
                * config.input_capacity_factor_estimate
            )
            hydrogen_amount_kgpy = config.hydrogen_amount_kgpy

        if config.desired_iron_ore_mtpy:
            hydrogen_amount_kgpy = (config.desired_iron_ore_mtpy 
                * 1000
                * config.feedstocks.hydrogen_consumption
                / config.input_capacity_factor_estimate
            )
            iron_ore_plant_capacity_mtpy = (config.desired_iron_ore_mtpy 
                / config.input_capacity_factor_estimate
            )

        return IronOreCapacityModelOutputs(
            iron_ore_plant_capacity_mtpy=iron_ore_plant_capacity_mtpy,
            hydrogen_amount_kgpy=hydrogen_amount_kgpy
        )
    # Otherwise, import model from filepaths - paths either from model_locs or config
    else:
        perf_model = config.performance_model['name']
        if config.performance_model['model_fp'] == '':
            config.performance_model['model_fp'] = model_locs['performance'][perf_model]['model']
        if config.performance_model['inputs_fp'] == '':
            config.performance_model['inputs_fp'] = model_locs['performance'][perf_model]['inputs']
        if config.performance_model['coeffs_fp'] == '':
            config.performance_model['coeffs_fp'] = model_locs['performance'][perf_model]['coeffs']
        model = importlib.import_module(config.performance_model['model_fp'])
        model_outputs = model.main(config)
        # MODEL NOT ACTUALLY IMPLEMENTED - putting out placeholders
        iron_ore_plant_capacity_mtpy, hydrogen_amount_kgpy = model_outputs
        return IronOreCapacityModelOutputs(
            iron_ore_plant_capacity_mtpy=iron_ore_plant_capacity_mtpy,
            hydrogen_amount_kgpy=hydrogen_amount_kgpy
        )

def run_iron_ore_model(plant_capacity_mtpy: float, plant_capacity_factor: float) -> float:
    """
    Calculates the annual iron ore production in metric tons based on plant capacity and
    capacity factor.

    Args:
        plant_capacity_mtpy (float):
            The plant's annual capacity in metric tons per year.
        plant_capacity_factor (float):
            The capacity factor of the plant.

    Returns:
        float: The calculated annual iron ore production in metric tons per year.
    """
    iron_ore_production_mtpy = plant_capacity_mtpy * plant_capacity_factor

    return iron_ore_production_mtpy


def run_iron_ore_cost_model(config: IronOreCostModelConfig) -> IronOreCostModelOutputs:
    # NOTE: updated references of 'iron' to 'iron_ore', left iron_ore_consumption and iron_ore_pellet_unitcost assuming these will be deleted
    """
    Calculates the capital expenditure (CapEx) and operating expenditure (OpEx) for
    a iron ore manufacturing plant based on the provided configuration.

    Args:
        config (IronOreCostModelConfig):
            Configuration object containing all necessary parameters for the cost
            model, including plant capacity, feedstock costs, and integration options
            for oxygen and heat.

    Returns:
        IronOreCostModelOutputs: An object containing detailed breakdowns of capital and
        operating costs, as well as total plant cost and other financial metrics.

    Note:
        The calculation includes various cost components such as electric arc furnace
        (EAF) casting, shaft furnace, oxygen supply, hydrogen preheating, cooling tower,
        and more, adjusted based on the Chemical Engineering Plant Cost Index (CEPCI).
    """
    # If cost model name is "placeholder", use the code that was copied over from Green Steel
    if config.cost_model['name'] == 'placeholder':
        
        feedstocks = config.feedstocks

    
        model_year_CEPCI = 596.2
        equation_year_CEPCI = 708.8

        capex_eaf_casting = (
            model_year_CEPCI
            / equation_year_CEPCI
            * 352191.5237
            * config.plant_capacity_mtpy**0.456
        )
        capex_shaft_furnace = (
            model_year_CEPCI
            / equation_year_CEPCI
            * 489.68061
            * config.plant_capacity_mtpy**0.88741
        )
        capex_oxygen_supply = (
            model_year_CEPCI
            / equation_year_CEPCI
            * 1715.21508
            * config.plant_capacity_mtpy**0.64574
        )
        if config.o2_heat_integration:
            capex_h2_preheating = (
                model_year_CEPCI
                / equation_year_CEPCI
                * (1 - 0.4)
                * (45.69123 * config.plant_capacity_mtpy**0.86564)
            )  # Optimistic ballpark estimate of 60% reduction in preheating
            capex_cooling_tower = (
                model_year_CEPCI
                / equation_year_CEPCI
                * (1 - 0.3)
                * (2513.08314 * config.plant_capacity_mtpy**0.63325)
            )  # Optimistic ballpark estimate of 30% reduction in cooling
        else:
            capex_h2_preheating = (
                model_year_CEPCI
                / equation_year_CEPCI
                * 45.69123
                * config.plant_capacity_mtpy**0.86564
            )
            capex_cooling_tower = (
                model_year_CEPCI
                / equation_year_CEPCI
                * 2513.08314
                * config.plant_capacity_mtpy**0.63325
            )
        capex_piping = (
            model_year_CEPCI
            / equation_year_CEPCI
            * 11815.72718
            * config.plant_capacity_mtpy**0.59983
        )
        capex_elec_instr = (
            model_year_CEPCI
            / equation_year_CEPCI
            * 7877.15146
            * config.plant_capacity_mtpy**0.59983
        )
        capex_buildings_storage_water = (
            model_year_CEPCI
            / equation_year_CEPCI
            * 1097.81876
            * config.plant_capacity_mtpy**0.8
        )
        # capex_misc = (
        #     model_year_CEPCI
        #     / equation_year_CEPCI
        #     * 7877.1546
        #     * config.plant_capacity_mtpy**0.59983
        # )
        capex_misc = config.capex_misc

        total_plant_cost = (
            capex_eaf_casting
            + capex_shaft_furnace
            + capex_oxygen_supply
            + capex_h2_preheating
            + capex_cooling_tower
            + capex_piping
            + capex_elec_instr
            + capex_buildings_storage_water
            + capex_misc
        )

        # -------------------------------Fixed O&M Costs------------------------------

        labor_cost_annual_operation = (
            69375996.9
            * ((config.plant_capacity_mtpy / 365 * 1000) ** 0.25242)
            / ((1162077 / 365 * 1000) ** 0.25242)
        )
        labor_cost_maintenance = 0.00863 * total_plant_cost
        labor_cost_admin_support = 0.25 * (
            labor_cost_annual_operation + labor_cost_maintenance
        )

        property_tax_insurance = 0.02 * total_plant_cost

        total_fixed_operating_cost = (
            labor_cost_annual_operation
            + labor_cost_maintenance
            + labor_cost_admin_support
            + property_tax_insurance
        )

        # ---------------------- Owner's (Installation) Costs --------------------------
        labor_cost_fivemonth = (
            5
            / 12
            * (
                labor_cost_annual_operation
                + labor_cost_maintenance
                + labor_cost_admin_support
            )
        )

        maintenance_materials_onemonth = (
            feedstocks.maintenance_materials_unitcost * config.plant_capacity_mtpy / 12
        )
        non_fuel_consumables_onemonth = (
            config.plant_capacity_mtpy
            * (
                feedstocks.raw_water_consumption * feedstocks.raw_water_unitcost
                + feedstocks.lime_consumption * feedstocks.lime_unitcost
                + feedstocks.carbon_consumption * feedstocks.carbon_unitcost
                + feedstocks.iron_ore_consumption * feedstocks.iron_ore_pellet_unitcost
            )
            / 12
        )

        waste_disposal_onemonth = (
            config.plant_capacity_mtpy
            * feedstocks.slag_disposal_unitcost
            * feedstocks.slag_production
            / 12
        )

        monthly_energy_cost = (
            config.plant_capacity_mtpy
            * (
                feedstocks.hydrogen_consumption * config.lcoh * 1000
                + feedstocks.natural_gas_consumption
                * feedstocks.natural_gas_prices[str(config.operational_year)]
                + feedstocks.electricity_consumption * feedstocks.electricity_cost
            )
            / 12
        )
        two_percent_tpc = 0.02 * total_plant_cost

        fuel_consumables_60day_supply_cost = (
            config.plant_capacity_mtpy
            * (
                feedstocks.raw_water_consumption * feedstocks.raw_water_unitcost
                + feedstocks.lime_consumption * feedstocks.lime_unitcost
                + feedstocks.carbon_consumption * feedstocks.carbon_unitcost
                + feedstocks.iron_ore_consumption * feedstocks.iron_ore_pellet_unitcost
            )
            / 365
            * 60
        )

        spare_parts_cost = 0.005 * total_plant_cost
        land_cost = 0.775 * config.plant_capacity_mtpy
        misc_owners_costs = 0.15 * total_plant_cost

        installation_cost = (
            labor_cost_fivemonth
            + two_percent_tpc
            + fuel_consumables_60day_supply_cost
            + spare_parts_cost
            + misc_owners_costs
        )

        return IronOreCostModelOutputs(
            # CapEx
            capex_eaf_casting=capex_eaf_casting,
            capex_shaft_furnace=capex_shaft_furnace,
            capex_oxygen_supply=capex_oxygen_supply,
            capex_h2_preheating=capex_h2_preheating,
            capex_cooling_tower=capex_cooling_tower,
            capex_piping=capex_piping,
            capex_elec_instr=capex_elec_instr,
            capex_buildings_storage_water=capex_buildings_storage_water,
            capex_misc=capex_misc,
            total_plant_cost=total_plant_cost,
            # Fixed OpEx
            labor_cost_annual_operation=labor_cost_annual_operation,
            labor_cost_maintenance=labor_cost_maintenance,
            labor_cost_admin_support=labor_cost_admin_support,
            property_tax_insurance=property_tax_insurance,
            total_fixed_operating_cost=total_fixed_operating_cost,
            # Owner's Installation costs
            labor_cost_fivemonth=labor_cost_fivemonth,
            maintenance_materials_onemonth=maintenance_materials_onemonth,
            non_fuel_consumables_onemonth=non_fuel_consumables_onemonth,
            waste_disposal_onemonth=waste_disposal_onemonth,
            monthly_energy_cost=monthly_energy_cost,
            spare_parts_cost=spare_parts_cost,
            land_cost=land_cost,
            misc_owners_costs=misc_owners_costs,
            installation_cost=installation_cost,
        )
    
    # If cost model is NOT 'placeholder', import the new cost model
    else:
        cost_model = config.cost_model['name']
        if config.cost_model['model_fp'] == '':
            config.cost_model['model_fp'] = model_locs['cost'][cost_model]['model']
        if config.cost_model['inputs_fp'] == '':
            config.cost_model['inputs_fp'] = model_locs['cost'][cost_model]['inputs']
        if config.cost_model['coeffs_fp'] == '':
            config.cost_model['coeffs_fp'] = model_locs['cost'][cost_model]['coeffs']
        model = importlib.import_module(config.cost_model['model_fp'])
        model_outputs = model.main(config)
        # MODEL NOT ACTUALLY IMPLEMENTED - putting out placeholders'

        capex_eaf_casting,capex_shaft_furnace,capex_oxygen_supply,capex_h2_preheating,\
            capex_cooling_tower,capex_piping,capex_elec_instr,capex_buildings_storage_water,\
            capex_misc,total_plant_cost,labor_cost_annual_operation,labor_cost_maintenance,\
            labor_cost_admin_support,property_tax_insurance,total_fixed_operating_cost,\
            labor_cost_fivemonth,maintenance_materials_onemonth,non_fuel_consumables_onemonth,\
            waste_disposal_onemonth,monthly_energy_cost,spare_parts_cost,land_cost,\
            misc_owners_costs,installation_cost = model_outputs

        return IronOreCostModelOutputs(
            # CapEx
            capex_eaf_casting=capex_eaf_casting,
            capex_shaft_furnace=capex_shaft_furnace,
            capex_oxygen_supply=capex_oxygen_supply,
            capex_h2_preheating=capex_h2_preheating,
            capex_cooling_tower=capex_cooling_tower,
            capex_piping=capex_piping,
            capex_elec_instr=capex_elec_instr,
            capex_buildings_storage_water=capex_buildings_storage_water,
            capex_misc=capex_misc,
            total_plant_cost=total_plant_cost,
            # Fixed OpEx
            labor_cost_annual_operation=labor_cost_annual_operation,
            labor_cost_maintenance=labor_cost_maintenance,
            labor_cost_admin_support=labor_cost_admin_support,
            property_tax_insurance=property_tax_insurance,
            total_fixed_operating_cost=total_fixed_operating_cost,
            # Owner's Installation costs
            labor_cost_fivemonth=labor_cost_fivemonth,
            maintenance_materials_onemonth=maintenance_materials_onemonth,
            non_fuel_consumables_onemonth=non_fuel_consumables_onemonth,
            waste_disposal_onemonth=waste_disposal_onemonth,
            monthly_energy_cost=monthly_energy_cost,
            spare_parts_cost=spare_parts_cost,
            land_cost=land_cost,
            misc_owners_costs=misc_owners_costs,
            installation_cost=installation_cost,
        )

@define
class IronOreFinanceModelConfig:
    # NOTE: updated references of 'iron' to 'iron_ore', however unsure if all attributes will be applicable to iron ore
    """
    Configuration for the iron ore finance model, including plant characteristics, financial assumptions, and cost inputs.

    Attributes:
        plant_life (int): The operational lifetime of the plant in years.
        plant_capacity_mtpy (float): Plant capacity in metric tons per year.
        plant_capacity_factor (float):
            The fraction of the year the plant operates at full capacity.
        iron_ore_production_mtpy (float): Annual iron ore production in metric tons.
        lcoh (float): Levelized cost of hydrogen.
        grid_prices (Dict[str, float]): Electricity prices per unit.
        feedstocks (Feedstocks):
            The feedstocks required for iron ore production, including types and costs.
        costs (Union[IronOreCosts, IronOreCostModelOutputs]):
            Calculated CapEx and OpEx costs.
        o2_heat_integration (bool): Indicates if oxygen and heat integration is used.
        financial_assumptions (Dict[str, float]):
            Financial assumptions for model calculations.
        install_years (int): The number of years over which the plant is installed.
        gen_inflation (float): General inflation rate.
        save_plots (bool): select whether or not to save output plots
        show_plots (bool): select whether or not to show output plots during run
        output_dir (str): where to store any saved plots or data
        design_scenario_id (int): what design scenario the plots correspond to
    """

    plant_life: int
    plant_capacity_mtpy: float
    plant_capacity_factor: float
    iron_ore_production_mtpy: float
    lcoh: float
    grid_prices: Dict[str, float]
    feedstocks: Feedstocks
    costs: Union[IronOreCosts, IronOreCostModelOutputs]
    o2_heat_integration: bool = True
    financial_assumptions: Dict[str, float] = Factory(dict)
    install_years: int = 3
    gen_inflation: float = 0.00
    save_plots: bool = False
    show_plots: bool = False
    output_dir: str = "./output/"
    design_scenario_id: int = 0

@define
class IronOreFinanceModelOutputs:
    """
    Represents the outputs of the iron ore finance model, encapsulating the results of financial analysis for iron ore production.

    Attributes:
        sol (dict):
            A dictionary containing the solution to the financial model, including key
            financial indicators such as NPV (Net Present Value), IRR (Internal Rate of
            Return), and breakeven price.
        summary (dict):
            A summary of key results from the financial analysis, providing a
            high-level overview of financial metrics and performance indicators.
        price_breakdown (pd.DataFrame):
            A Pandas DataFrame detailing the cost breakdown for producing iron ore,
            including both capital and operating expenses, as well as the impact of
            various cost factors on the overall price of iron ore.
    """

    sol: dict
    summary: dict
    price_breakdown: pd.DataFrame


def run_iron_ore_finance_model(
    # NOTE: updated references of 'iron' to 'iron_ore', however unsure if all attributes will be applicable to iron ore
    # TODO: verify desired key value pair "name":"iron ore" (iron ore -> raw iron ore?)
    config: IronOreFinanceModelConfig,
) -> IronOreFinanceModelOutputs:
    """
    Executes the financial model for iron ore production, calculating the breakeven price
    of iron ore and other financial metrics based on the provided configuration and cost
    models.

    This function integrates various cost components, including capital expenditures
    (CapEx), operating expenses (OpEx), and owner's costs. It leverages the ProFAST
    financial analysis software framework.

    Args:
        config (IronOreFinanceModelConfig):
            Configuration object containing all necessary parameters and assumptions
            for the financial model, including plant characteristics, cost inputs,
            financial assumptions, and grid prices.

    Returns:
        IronOreFinanceModelOutputs:
            Object containing detailed financial analysis results, including solution
            metrics, summary values, price breakdown, and iron ore price breakdown per
            tonne. This output is instrumental in assessing the financial performance
            and breakeven price for the iron ore production facility.
    """

    feedstocks = config.feedstocks
    costs = config.costs

    # Set up ProFAST
    pf = ProFAST.ProFAST("blank")

    # apply all params passed through from config
    for param, val in config.financial_assumptions.items():
        pf.set_params(param, val)

    analysis_start = int(list(config.grid_prices.keys())[0]) - config.install_years

    # Fill these in - can have most of them as 0 also
    pf.set_params(
        "commodity",
        {
            "name": "iron ore",
            "unit": "metric tonnes",
            "initial price": 1000,
            "escalation": config.gen_inflation,
        },
    )
    pf.set_params("capacity", config.plant_capacity_mtpy / 365)  # units/day
    pf.set_params("maintenance", {"value": 0, "escalation": config.gen_inflation})
    pf.set_params("analysis start year", analysis_start)
    pf.set_params("operating life", config.plant_life)
    pf.set_params("installation months", 12 * config.install_years)
    pf.set_params(
        "installation cost",
        {
            "value": costs.installation_cost,
            "depr type": "Straight line",
            "depr period": 4,
            "depreciable": False,
        },
    )
    pf.set_params("non depr assets", costs.land_cost)
    pf.set_params(
        "end of proj sale non depr assets",
        costs.land_cost * (1 + config.gen_inflation) ** config.plant_life,
    )
    pf.set_params("demand rampup", 5.3)
    pf.set_params("long term utilization", config.plant_capacity_factor)
    pf.set_params("credit card fees", 0)
    pf.set_params("sales tax", 0)
    pf.set_params(
        "license and permit", {"value": 00, "escalation": config.gen_inflation}
    )
    pf.set_params("rent", {"value": 0, "escalation": config.gen_inflation})
    pf.set_params("property tax and insurance", 0)
    pf.set_params("admin expense", 0)
    pf.set_params("sell undepreciated cap", True)
    pf.set_params("tax losses monetized", True)
    pf.set_params("general inflation rate", config.gen_inflation)
    pf.set_params("debt type", "Revolving debt")
    pf.set_params("cash onhand", 1)

    # ----------------------------------- Add capital items to ProFAST ----------------
    pf.add_capital_item(
        name="EAF & Casting",
        cost=costs.capex_eaf_casting,
        depr_type="MACRS",
        depr_period=7,
        refurb=[0],
    )
    pf.add_capital_item(
        name="Shaft Furnace",
        cost=costs.capex_shaft_furnace,
        depr_type="MACRS",
        depr_period=7,
        refurb=[0],
    )
    pf.add_capital_item(
        name="Oxygen Supply",
        cost=costs.capex_oxygen_supply,
        depr_type="MACRS",
        depr_period=7,
        refurb=[0],
    )
    pf.add_capital_item(
        name="H2 Pre-heating",
        cost=costs.capex_h2_preheating,
        depr_type="MACRS",
        depr_period=7,
        refurb=[0],
    )
    pf.add_capital_item(
        name="Cooling Tower",
        cost=costs.capex_cooling_tower,
        depr_type="MACRS",
        depr_period=7,
        refurb=[0],
    )
    pf.add_capital_item(
        name="Piping",
        cost=costs.capex_piping,
        depr_type="MACRS",
        depr_period=7,
        refurb=[0],
    )
    pf.add_capital_item(
        name="Electrical & Instrumentation",
        cost=costs.capex_elec_instr,
        depr_type="MACRS",
        depr_period=7,
        refurb=[0],
    )
    pf.add_capital_item(
        name="Buildings, Storage, Water Service",
        cost=costs.capex_buildings_storage_water,
        depr_type="MACRS",
        depr_period=7,
        refurb=[0],
    )
    pf.add_capital_item(
        name="Other Miscellaneous Costs",
        cost=costs.capex_misc,
        depr_type="MACRS",
        depr_period=7,
        refurb=[0],
    )

    # -------------------------------------- Add fixed costs--------------------------------
    pf.add_fixed_cost(
        name="Annual Operating Labor Cost",
        usage=1,
        unit="$/year",
        cost=costs.labor_cost_annual_operation,
        escalation=config.gen_inflation,
    )
    pf.add_fixed_cost(
        name="Maintenance Labor Cost",
        usage=1,
        unit="$/year",
        cost=costs.labor_cost_maintenance,
        escalation=config.gen_inflation,
    )
    pf.add_fixed_cost(
        name="Administrative & Support Labor Cost",
        usage=1,
        unit="$/year",
        cost=costs.labor_cost_admin_support,
        escalation=config.gen_inflation,
    )
    pf.add_fixed_cost(
        name="Property tax and insurance",
        usage=1,
        unit="$/year",
        cost=costs.property_tax_insurance,
        escalation=0.0,
    )
    # Putting property tax and insurance here to zero out depcreciation/escalation. Could instead put it in set_params if
    # we think that is more accurate

    # ---------------------- Add feedstocks, note the various cost options-------------------
    pf.add_feedstock(
        name="Maintenance Materials",
        usage=1.0,
        unit="Units per metric tonne of iron ore",
        cost=feedstocks.maintenance_materials_unitcost,
        escalation=config.gen_inflation,
    )
    pf.add_feedstock(
        name="Raw Water Withdrawal",
        usage=feedstocks.raw_water_consumption,
        unit="metric tonnes of water per metric tonne of iron ore",
        cost=feedstocks.raw_water_unitcost,
        escalation=config.gen_inflation,
    )
    pf.add_feedstock(
        name="Lime",
        usage=feedstocks.lime_consumption,
        unit="metric tonnes of lime per metric tonne of iron ore",
        cost=feedstocks.lime_unitcost,
        escalation=config.gen_inflation,
    )
    pf.add_feedstock(
        name="Carbon",
        usage=feedstocks.carbon_consumption,
        unit="metric tonnes of carbon per metric tonne of iron ore",
        cost=feedstocks.carbon_unitcost,
        escalation=config.gen_inflation,
    )
    pf.add_feedstock(
        #NOTE: leaving this as is, noting this will probably be deleted (ore is not a feedstock for mining ore?)
        name="Iron Ore",
        usage=feedstocks.iron_ore_consumption,
        unit="metric tonnes of iron ore per metric tonne of iron",
        cost=feedstocks.iron_ore_pellet_unitcost,
        escalation=config.gen_inflation,
    )
    pf.add_feedstock(
        name="Hydrogen",
        usage=feedstocks.hydrogen_consumption,
        unit="metric tonnes of hydrogen per metric tonne of iron ore",
        cost=config.lcoh * 1000,
        escalation=config.gen_inflation,
    )
    pf.add_feedstock(
        name="Natural Gas",
        usage=feedstocks.natural_gas_consumption,
        unit="GJ-LHV per metric tonne of iron ore",
        cost=feedstocks.natural_gas_prices,
        escalation=config.gen_inflation,
    )
    pf.add_feedstock(
        name="Electricity",
        usage=feedstocks.electricity_consumption,
        unit="MWh per metric tonne of iron ore",
        cost=config.grid_prices,
        escalation=config.gen_inflation,
    )
    pf.add_feedstock(
        name="Slag Disposal",
        usage=feedstocks.slag_production,
        unit="metric tonnes of slag per metric tonne of iron ore",
        cost=feedstocks.slag_disposal_unitcost,
        escalation=config.gen_inflation,
    )

    pf.add_coproduct(
        name="Oxygen sales",
        usage=feedstocks.excess_oxygen,
        unit="kg O2 per metric tonne of iron ore",
        cost=feedstocks.oxygen_market_price,
        escalation=config.gen_inflation,
    )

    # ------------------------------ Set up outputs ---------------------------

    sol = pf.solve_price()
    summary = pf.get_summary_vals()
    price_breakdown = pf.get_cost_breakdown()

    if config.save_plots or config.show_plots:
        savepaths = [
            config.output_dir + "figures/capex/",
            config.output_dir + "figures/annual_cash_flow/",
            config.output_dir + "figures/lcos_breakdown/",
            config.output_dir + "data/",
        ]
        for savepath in savepaths:
            if not os.path.exists(savepath):
                os.makedirs(savepath)

        pf.plot_capital_expenses(
            fileout=savepaths[0] + "iron_ore_capital_expense_%i.pdf" % (config.design_scenario_id),
            show_plot=config.show_plots,
        )
        pf.plot_cashflow(
            fileout=savepaths[1] + "iron_ore_cash_flow_%i.png"
            % (config.design_scenario_id),
            show_plot=config.show_plots,
        )

        pd.DataFrame.from_dict(data=pf.cash_flow_out).to_csv(
            savepaths[3] + "iron_ore_cash_flow_%i.csv" % (config.design_scenario_id)
        )

        pf.plot_costs(
            savepaths[2] + "lcos_%i" % (config.design_scenario_id),
            show_plot=config.show_plots,
        )

    return IronOreFinanceModelOutputs(
        sol=sol,
        summary=summary,
        price_breakdown=price_breakdown,
    )


def run_iron_ore_full_model(greenheart_config: dict, save_plots=False, show_plots=False, output_dir="./output/", design_scenario_id=0) -> Tuple[IronOreCapacityModelOutputs, IronOreCostModelOutputs, IronOreFinanceModelOutputs]:
    # NOTE: updated references of 'iron' to 'iron_ore', however unsure if all portions of below code are applicable to iron ore
    # TODO: update calls to greenheart_config yaml with appropriate nesting to pull ore config (or another yaml?)
    """
    Runs the full iron ore model, including capacity, cost, and finance models.

    Args:
        greenheart_config (dict): The configuration for the greenheart model.

    Returns:
        Tuple[IronOreCapacityModelOutputs, IronOreCostModelOutputs, IronOreFinanceModelOutputs]:
            A tuple containing the outputs of the iron ore capacity, cost, and finance models.
    """
    # this is likely to change as we refactor to use config dataclasses, but for now
    # we'll just copy the config and modify it as needed
    iron_ore_config = copy.deepcopy(greenheart_config['iron'])

    if iron_ore_config["costs"]["lcoh"] != iron_ore_config["finances"]["lcoh"]:
        raise(ValueError(
            "iron ore cost LCOH and iron ore finance LCOH are not equal. You must specify both values or neither. \
                If neither is specified, LCOH will be calculated."
            )
        )

    iron_ore_costs = iron_ore_config["costs"]
    iron_ore_capacity = iron_ore_config["capacity"]
    feedstocks = Feedstocks(**iron_ore_costs["feedstocks"])

    # run iron ore capacity model to get iron ore plant size
    # uses hydrogen amount from electrolyzer physics model
    capacity_config = IronOreCapacityModelConfig(
        feedstocks=feedstocks,
        **iron_ore_capacity
    )
    capacity_config.performance_model = iron_ore_config["performance_model"]
    iron_ore_capacity = run_size_iron_ore_plant_capacity(capacity_config)

    # run iron ore cost model
    iron_ore_costs["feedstocks"] = feedstocks
    iron_ore_cost_config = IronOreCostModelConfig(
        plant_capacity_mtpy=iron_ore_capacity.iron_ore_plant_capacity_mtpy,
        **iron_ore_costs
    )
    iron_ore_cost_config.plant_capacity_mtpy = iron_ore_capacity.iron_ore_plant_capacity_mtpy
    iron_ore_cost_config.cost_model = iron_ore_config["cost_model"]
    iron_ore_costs = run_iron_ore_cost_model(iron_ore_cost_config)

    # run iron ore finance model
    iron_ore_finance = iron_ore_config["finances"]
    iron_ore_finance["feedstocks"] = feedstocks

    iron_ore_finance_config = IronOreFinanceModelConfig(
        plant_capacity_mtpy=iron_ore_capacity.iron_ore_plant_capacity_mtpy,
        plant_capacity_factor=capacity_config.input_capacity_factor_estimate,
        iron_ore_production_mtpy=run_iron_ore_model(
            iron_ore_capacity.iron_ore_plant_capacity_mtpy,
            capacity_config.input_capacity_factor_estimate,
        ),
        costs=iron_ore_costs,
        show_plots=show_plots, 
        save_plots=save_plots,
        output_dir=output_dir,
        design_scenario_id=design_scenario_id,
        **iron_ore_finance
    )
    iron_ore_finance = run_iron_ore_finance_model(iron_ore_finance_config)

    return (
        iron_ore_capacity,
        iron_ore_costs,
        iron_ore_finance
    )