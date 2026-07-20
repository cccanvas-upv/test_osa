from utils import plot_trace, save_trace
from lab_devices import Yeni, Yoko, Opm, YAMLDOCUMENT

import os, datetime, time
from os.path import isfile, expanduser

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
    
    # Connect to the OSA
    # try:
    #     osa = Yoko(
    #         resource_address = 'TCPIP0::192.168.54.1::5025::SOCKET', # Check the IP address of the OSA
    #     )
    # except Exception as e:
    #     raise ConnectionError(f"Could not connect to OSA:\n {e}")

    # Connect to the OPM
    try:
        opm = Opm(
            resource_address = 'USB0::0x1313::0x8078::P0030943::INSTR',
        )
    except Exception as e:
        raise ConnectionError(f"Could not connect to OPM:\n {e}")
    
    # Configure the YAML document
    doc = YAMLDOCUMENT()
    doc.datetime = formatted
    doc.operator = 'Your Name'
    doc.setup = 'PX.SX'
    doc.project = project = "XXXXX"
    doc.wafer = wafer = "XXXX"
    doc.reticle = reticle = "XX"
    doc.die = die_name = "X"
    doc.dut = dut = "XX" 
    doc.polarization = polarization = 'nana'
    doc.die_temperature = "na" #kOhm Tacc
    doc.coupling_type = 'VERT-SM-SM'
    doc.coupling_angle = angle = 49 # degrees
    doc.idsource = "ASE1"#'FiberLabs ASE-FL7015 1530-1610nm' 
    doc.idosa = 'OSA20' # "EXFO OSA20" 
    doc.operator_notes = """XXXXXXXX""" 
    doc.splitter = "1x295/5-1"  
    # Saving data
    folder_lab = os.path.expandvars("./data")
    save_date = datetime.datetime.now().strftime("%Y%m%d")
    circuit = die_name
    folder_measurements = "/".join([folder_lab, project, wafer, save_date])
    file_name = f"R{reticle}-C{circuit}-{dut}-{angle}" # Consider to remove the angle after ANGLE sweep

    # Work with the OSA
    with osa: 
        osa_idn = osa.id
        opm_idn = opm.id
        # osa.wait_for()
        print("Instrument ID:", osa_idn)
        print("Instrument ID:", opm_idn)

        # OSA settings
        tracename = 1
        averages = 5
        osa.setup_sweep(
            center_wavelength = 1565e-9,
            span = 80e-9,
            sweep_mode = 'SINGLE',
            sensitivity = -70, # Consider to change this value if high power is measured by OPM
            resolution = 200e-12, # Check between OSAs - After sweep value 
        )
        osa.run_sweep(tracename, averages=averages)
        trace = osa.get_trace(tracename)
        ## Editing the yaml document
        doc.opm_power = opm.measure_power() #dBm 
        print(f"Power measured by OPM: {opm.measure_power()} dBm")
        doc.osa_idn = osa_idn
        doc.osa_resolution = osa.resolution_bandwidth
        doc.osa_sensitivity = osa.sensitivity_level
        doc.osa_start_wavelength = osa.wavelength_center-osa.wavelength_span/2 # do not use osa.start_wavelength it gives lot of digits
        doc.osa_stop_wavelength =  osa.wavelength_center+osa.wavelength_span/2 # do not use osa.stop_wavelength it gives lot of digits
        doc.osa_sweep_mode = osa.sweep_mode
        doc.osa_integrated_power = osa.integrated_power
        doc.osa_dBm_nm = osa.dBm_nm
        # Saving txt from osa measurement
        save_trace(folder_measurements=folder_measurements,
                file_name=file_name,
                yaml=doc,osa=osa,data=trace)
    # Plot the trace
    plot_trace(trace)

if __name__ == "__main__":
    main()
