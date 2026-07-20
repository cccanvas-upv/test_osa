from utils import plot_trace, save_trace
from lab_devices import Yeni, Opm, Smu, YAMLDOCUMENT

import os, datetime, time
from os.path import isfile, expanduser
import numpy as np
from matplotlib import pyplot as plt
timestamp = datetime.datetime.fromtimestamp(time.time())
formatted = timestamp.strftime("%Y_%m_%d_%H_%M_%S")
UNDEFINED = "UNDEFINED"

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..')))

def main():
    print("Hello from test-osa!")

    # Connect to the OSA
    try:
        osa = Yeni(
            resource_address = 'TCPIP0::192.168.54.1::5025::SOCKET',
        )
    except Exception as e:
        raise ConnectionError(f"Could not connect to OSA:\n {e}")

    # Connect to the OPM
    try:
        opm = Opm(
            resource_address = 'USB0::0x1313::0x8078::P0030943::INSTR',
        )
    except Exception as e:
        raise ConnectionError(f"Could not connect to OPM:\n {e}")
    
    resource_address="GPIB1::24::INSTR"
    try:
        smu = Smu(
                            resource_address=resource_address,
        )
    except Exception as e:
        raise ConnectionError(f"Could not connect to SMU:\n {e}")

    # Configure the YAML document
    doc = YAMLDOCUMENT()
    doc.datetime = formatted
    doc.operator = 'Camilo Cano'
    doc.setup = 'P2.S1'
    doc.project = project = "ENLACE"
    doc.wafer = wafer = "17940-W16"
    doc.reticle = reticle = "11"
    doc.die = die_name = "6"
    doc.dut = dut = "mz-coupler" # Query - Localizar
    doc.polarization = polarization = 'nana'
    doc.die_temperature = "na" #kOhm Tacc
    doc.coupling_type = 'lat-lensed'
    doc.coupling_angle = angle = 49 # degrees
    doc.idsource = "ASE1"#'FiberLabs ASE-FL7015 1530-1610nm' # Validacion
    doc.idosa = 'OSA20' # "EXFO OSA20" # Validacion
    doc.operator_notes = """NA""" # Validacion / Procesar
    #doc.opm_power = -6 #dBm # Añadir unidades en Procesar
    doc.splitter = "2x2s90/10-1"  
    
    # Saving data
    folder_lab = os.path.expandvars("./data")
    save_date = datetime.datetime.now().strftime("%Y%m%d")
    circuit = die_name
    folder_measurements = "/".join([folder_lab, project, wafer, save_date])


    # Work with the OSA
    with osa: 
        osa_idn = osa.id
        opm_idn = opm.id
        smu_idn = smu.id
        # osa.wait_for()
        print("Instrument ID:", osa_idn)
        print("Instrument ID:", opm_idn)
        print("Instrument ID:", smu_idn)
        # SMU Settings
        smu.write("*RST")
        smu.apply_current()                # Sets up to source current
        smu.source_current_range = 100e-3   # Sets the source current range to 10 mA
        smu.compliance_voltage = 51        # Sets the compliance voltage to 10 V
        smu.source_current = 0             # Sets the source current to 0 mA
        smu.enable_source()                # Enables the source output
        smu.measure_voltage()              # Sets up to measure voltage
        voltages = []
        powers = []
        currents = np.linspace(0, 30e-3, 61) 
        spectrum = 0
        doc.opm_power = opm.measure_power() #dBm # Añadir unidades en Procesar
        for j, current in enumerate(currents):
                doc.opm_power = opm.measure_power() #dBm # Añadir unidades en Procesar
                file_name = f"R{reticle}-C{circuit}-{dut}-{current}"
                smu.ramp_to_current(current)          # Ramps the current to X mA
                time.sleep(1)
                print(smu.voltage)                       
                voltages.append(smu.voltage)
                powers.append(opm.measure_power())
                if(spectrum): 
                    # OSA settings
                    tracename = 1
                    averages = 3
                    osa.setup_sweep(
                        center_wavelength = 1565e-9,
                        span = 80e-9,
                        sweep_mode = 'SINGLE',
                        sensitivity = -60,
                        resolution = 200e-12,
                    )
                    osa.run_sweep(tracename, averages=averages)
                    trace = osa.get_trace(tracename)
                    print(f"Power measured by OPM: {opm.measure_power()} dBm")
                    save_trace(folder_measurements=folder_measurements,
                        file_name=file_name,
                        yaml=doc,osa=osa,data=trace)
        smu.shutdown() 
        plt.plot(currents, powers, label='Voltage vs Current')
        plt.show()
        np.savez(f"R{reticle}-C{circuit}-heater-lvi.npz", x_axis=currents, y_axis=powers)
        np.savez(f"R{reticle}-C{circuit}-heater.vi.npz", x_axis=voltages, y_axis=currents)

        ## Editing the yaml document
        doc.osa_idn = osa_idn
        doc.osa_resolution = osa.resolution_bandwidth
        doc.osa_sensitivity = osa.sensitivity_level
        doc.osa_start_wavelength = osa.wavelength_center-osa.wavelength_span/2 # do not use osa.start_wavelength it gives lot of digits
        doc.osa_stop_wavelength =  osa.wavelength_center+osa.wavelength_span/2 # do not use osa.stop_wavelength it gives lot of digits
        doc.osa_sweep_mode = osa.sweep_mode
        doc.osa_integrated_power = osa.integrated_power
        doc.osa_dBm_nm = osa.dBm_nm
            # Saving txt from osa measurement

    # Plot the trace
    # plot_trace(trace)

if __name__ == "__main__":
    main()
