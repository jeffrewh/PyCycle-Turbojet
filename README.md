# PyCycle-Turbojet

A Python-based parametric cycle analysis tool for gas turbine engines.

## Overview

This tool simulates the thermodynamics of a single-spool turbojet engine using standard Brayton Cycle analysis. It is designed to perform trade studies between **Compressor Pressure Ratio (OPR)** and **Turbine Inlet Temperature (TIT)** to optimize for:

- Specific Thrust
- Thermal Efficiency

## Features

- Isentropic compression and expansion modeling.
- Parametric sweeping capability (mimicking NPSS trade studies).
- Matplotlib visualization of the design space.

## Usage

1. Install dependencies: `pip install numpy matplotlib`
2. Run the analysis: `python main.py`

## Methodology

The script calculates state points (Stagnation Temperature/Pressure) through the intake, compressor, combustor, turbine, and nozzle using variable specific heat ratios.
