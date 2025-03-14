from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


def plot_wind_results(wind_data, site_name, latlon, results_dir, plot_wind):
    if plot_wind:
        wind_speed = [W[2] for W in wind_data]
        plt.figure(figsize=(9, 6))
        plt.plot(wind_speed)
        title = (
            f"Wind Speed (m/s) for selected location\n{site_name}\nlat, lon: {latlon}"
            f"\nAverage Wind Speed (m/s) {np.average(wind_speed)}"
        )
        plt.title(title)
        plt.savefig(
            Path(results_dir) / f"Average Wind Speed_{site_name}",
            bbox_inches="tight",
        )


def plot_pie(site_df, site_name, turbine_name, results_dir):
    group_names = ["BOS", "Soft", "Turbine"]
    group_size = [site_df["BOS"], site_df["Soft"], site_df["Turbine CapEx"]]
    subgroup_names = [
        "Array System",
        "Export System",
        "Substructure",
        "Mooring System",
        "Offshore Substation",
        "Scour Protection",
        "Array System Installation",
        "Export System Installation",
        "Offshore Substation Installation",
        "Scour Protection Installation",
        "Substructure Installation",
        "Turbine Installation",
        "Mooring System Installation",
        "construction_insurance_capex",
        "decomissioning_costs",
        "construction_financing",
        "procurement_contingency_costs",
        "install_contingency_costs",
        "project_completion_capex",
        "Turbine CapEx",
    ]

    subgroup_vals = site_df[subgroup_names]
    subgroup_size = subgroup_vals

    bos_names = [f"BOS: {name}" for name in subgroup_names[:13]]
    soft_names = [f"Soft Cost: {name}" for name in subgroup_names[13:-1]]
    turbine_names = [f"Turbine: {name}" for name in subgroup_names[19:]]
    all_names = bos_names + soft_names + turbine_names
    subgroup_names_legs = all_names

    # Create colors
    a, b, c = [plt.cm.Blues, plt.cm.Reds, plt.cm.Greens]

    # First Ring (Inside)
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.axis("equal")
    mypie, _ = ax.pie(
        group_size,
        radius=1,
        labels=group_names,
        labeldistance=0.6,
        colors=[a(0.6), b(0.6), c(0.6)],
    )
    plt.setp(mypie, width=0.3, edgecolor="white")

    # Second Ring (Outside)
    mypie2, _ = ax.pie(
        subgroup_size,
        radius=1.0 + 0.4,
        labels=subgroup_names,
        labeldistance=1,
        rotatelabels=True,
        colors=[
            a(0.1),
            a(0.2),
            a(0.3),
            a(0.4),
            a(0.5),
            a(0.6),
            a(0.7),
            a(0.8),
            a(0.9),
            a(1),
            a(1.1),
            a(1.2),
            a(1.3),
            b(0.16),
            b(0.32),
            b(0.48),
            b(0.64),
            b(0.8),
            b(0.9),
            c(0.4),
        ],
    )
    plt.setp(mypie2, width=0.4, edgecolor="white")
    plt.margins(0, 0)

    plt.legend(loc=(0.9, 0.1))
    handles, labels = ax.get_legend_handles_labels()

    ax.legend(handles[3:], subgroup_names_legs, loc=(0.4, 0.3))

    plt.legend(subgroup_names_legs, loc="best")
    # plt.title('ORBIT Cost Contributions for {}'.format(site_name))
    print(f"ORBIT Cost Contributions for {site_name}")
    plt.savefig(
        Path(results_dir) / f"BOS Cost Figure {site_name}_{turbine_name}.jpg",
        bbox_inches="tight",
    )
    # plt.show()


def plot_HOPP(
    combined_hybrid_power_production_hopp,
    energy_shortfall_hopp,
    combined_hybrid_curtailment_hopp,
    load,
    results_dir,
    site_name,
    atb_year,
    turbine_model,
    hybrid_plant,
    plot_power_production,
):
    if plot_power_production:
        plt.figure(figsize=(4, 4))
        plt.title("HOPP power production")
        plt.plot(combined_hybrid_power_production_hopp[200:300], label="wind + pv")
        plt.plot(energy_shortfall_hopp[200:300], label="shortfall")
        plt.plot(combined_hybrid_curtailment_hopp[200:300], label="curtailment")
        plt.plot(load[200:300], label="electrolyzer rating")
        plt.xlabel("Time (hour)")
        plt.ylabel("Power Production (kW)")
        # plt.ylim(0,250000)
        plt.legend()
        plt.tight_layout()
        plt.savefig(
            Path(results_dir) / f"HOPP Power Production_{site_name}_{atb_year}_{turbine_model}",
            bbox_inches="tight",
        )
        # plt.show()

    msg = (
        f"Turbine Power Output (to identify powercurve impact):"
        " {hybrid_plant.wind.annual_energy_kw:,.0f} kW"
        f"\nWind Plant CF: {hybrid_plant.wind.capacity_factor}"
        f"\nLCOE: {hybrid_plant.lcoe_real.hybrid}"
    )
    print(msg)
    # print("LCOE: {}"].format(hybrid_plant.lcoe_real.hybrid))


def plot_battery_results(
    combined_hybrid_curtailment_hopp,
    energy_shortfall_hopp,
    combined_pv_wind_storage_power_production_hopp,
    combined_hybrid_power_production_hopp,
    battery_SOC,
    battery_used,
    results_dir,
    site_name,
    atb_year,
    turbine_model,
    load,
    plot_battery,
):
    if plot_battery:
        plt.figure(figsize=(9, 6))
        plt.subplot(311)
        plt.plot(combined_hybrid_curtailment_hopp[200:300], label="curtailment")
        plt.plot(energy_shortfall_hopp[200:300], label="shortfall")
        plt.title("Energy Curtailment and Shortfall")
        plt.legend()

        plt.subplot(312)
        plt.plot(
            combined_pv_wind_storage_power_production_hopp[200:300],
            label="wind+pv+storage",
        )
        plt.plot(combined_hybrid_power_production_hopp[200:300], "--", label="wind+pv")
        plt.plot(load[200:300], "--", label="electrolyzer rating")
        plt.legend()
        plt.title("Hybrid Plant Power Flows with and without storage")
        plt.tight_layout()

        plt.subplot(313)
        plt.plot(battery_SOC[200:300], label="state of charge")
        plt.plot(battery_used[200:300], "--", label="battery used")
        plt.title("Battery State")
        plt.legend()
        plt.savefig(
            Path(results_dir) / f"HOPP Full Power Flows_{site_name}_{atb_year}_{turbine_model}",
            bbox_inches="tight",
        )
        # plt.show()


def plot_h2_results(
    H2_Results,
    electrical_generation_timeseries,
    results_dir,
    site_name,
    atb_year,
    turbine_model,
    load,
    plot_h2,
):
    if plot_h2:
        hydrogen_hourly_production = H2_Results["hydrogen_hourly_production"]
        plt.figure(figsize=(8, 8))
        plt.subplot(411)
        plt.plot(electrical_generation_timeseries[200:300])
        plt.ylim(0, max(electrical_generation_timeseries[200:300]) * 1.2)
        plt.plot(load[200:300], label="electrolyzer rating")
        plt.legend()
        plt.title("Energy to electrolyzer (kW)")

        plt.subplot(412)
        plt.plot(hydrogen_hourly_production[200:300])
        plt.ylim(0, max(hydrogen_hourly_production[200:300]) * 1.2)
        plt.title("Hydrogen production rate (kg/hr)")

        plt.subplot(413)
        plt.plot(H2_Results["electrolyzer_total_efficiency"][200:300])
        plt.ylim(0, 1)
        plt.title("Electrolyzer Total Efficiency (%)")

        plt.subplot(414)
        plt.plot(H2_Results["water_hourly_usage"][200:300], "--", label="Hourly Water Usage")
        plt.legend()
        title = (
            f"Hourly Water Usage (kg/hr)\nTotal Annual Water Usage:"
            f" {H2_Results["water_annual_usage"]:,.0f} kg"
        )
        plt.title(title)
        plt.tight_layout()
        plt.xlabel("Time (hours)")
        plt.savefig(
            Path(results_dir) / f"Electrolyzer Flows_{site_name}_{atb_year}_{turbine_model}",
            bbox_inches="tight",
        )
        # plt.show()


def plot_desal_results(
    fresh_water_flowrate,
    feed_water_flowrate,
    operational_flags,
    results_dir,
    site_name,
    atb_year,
    turbine_model,
    plot_desal,
):
    if plot_desal:
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.plot(fresh_water_flowrate[200:300], "--", label="Freshwater flowrate from desal")
        plt.plot(feed_water_flowrate[200:300], "--", label="Feedwater flowrate to desal")
        plt.legend()
        plt.title("Freshwater flowrate (m^3/hr) from desal  (Snapshot)")
        # plt.show()

        plt.subplot(1, 2, 2)
        plt.plot(operational_flags[200:300], "--", label="Operational Flag")
        plt.legend()
        title = (
            "Desal Equipment Operational Status (Snapshot)"
            "\n0 = Not enough power to operate"
            "\n1 = Operating at reduced capacity"
            "\n2 = Operating at full capacity"
        )
        plt.title(title)
        plt.savefig(
            Path(results_dir) / f"Desal Flows_{site_name}_{atb_year}_{turbine_model}",
            bbox_inches="tight",
        )
        # plt.show()


def plot_hvdcpipe(
    total_export_system_cost,
    total_h2export_system_cost,
    site_name,
    atb_year,
    dist_to_port_value,
    results_dir,
):
    # create data
    if plot_hvdcpipe:
        barx = ["HVDC", "Pipeline"]
        # cost_comparison_hvdc_pipeline = [capex_pipeline,total_export_system_cost]
        cost_comparison_hvdc_pipeline = [
            total_export_system_cost,
            total_h2export_system_cost,
        ]
        plt.figure(figsize=(9, 6))
        plt.bar(barx, cost_comparison_hvdc_pipeline)

        plt.ylabel("$USD")
        plt.legend(["Total CAPEX"])
        # plt.title(f"H2 Pipeline vs HVDC cost\n {site_name}\n Model:{in_dict['pipeline_model']}"
        plt.title(f"H2 Pipeline vs HVDC cost\n {site_name}\n Model: ASME Pipeline")
        plt.savefig(
            Path(results_dir) / f"Pipeline Vs HVDC Cost_{site_name}_{atb_year}_{dist_to_port_value}"
        )
        # plt.show()
