
# TUFLOW Summary Dashboard Tool

## Introduction

The **TUFLOW Summary Dashboard** tool provides a dashboard interface that allows users to drag and drop a various **TUFLOW Classic/HPC** and **TUFLOW FV** files, for example, the TUFLOW Summary File (TSF), TUFLOW *.hpc.dt.csv or TUFLOW FV *_int_cfl_dt.csv file. It then plots a number of summary statistics and visualisations summarising the file.  Time series result files can also be plotted, negating the need to plot up in Excel or similar.  This provides a quick way to plot up time-series outputs.

This tool offers a quick way to visualise the success and quality of a TUFLOW HPC/Classic or TUFLOW FV simulation and allows users to download the information for **QA purposes**.

---

## Run Locally or Host on the Cloud

The tool can be run in two ways:

### 1. **Locally**
- Run as a Python script from your IDE.
- Requires the following Python libraries:
  - `Plotly`
  - `Plotly Dash`
  - `Pandas`
  - `Numpy`
- Once running, navigate to [http://127.0.0.1:8050/](http://127.0.0.1:8050/) in your browser to access the dashboard.

![Home_Page_View](images/Home_Page.png)


### 2. **Cloud Hosting**
- Hosted version available via a cloud link.
- Example: [TUFLOW Summary Dashboard on render](https://tuflow-dashboard.onrender.com/)
- Note:
  - Free cloud hosting may be slower.
  - Limited memory.
  - Single-user access only.

---

## TUFLOW HPC/Classic File Uploads

### **TUFLOW Summary File (TSF)**
- Drag and drop a TSF file to generate a reporting dashboard.
- Dashboard appearance varies based on:
  - TUFLOW Classic vs HPC
  - Simulation status (ongoing or completed)

#### **Completed Simulation**
- Displays:
  - Hardware and solver used
  - Model nature and size
  - Warnings and messages
  - Runtime information
  - Inflows/outflows summary
  - Mass balance summary
  
   ![completed_sim_view](images/Completed_Sim.png)

#### **Simulation in Progress**
- Displays:
  - All of the above
  - Simulation progress
  - Estimated remaining time
  
  ![ongoing_sim_view](images/In_Progress_Sim.png)

---

### **HPC.DT.CSV Files**
- Upload a `*.hpc.dt.csv` file to generate subplots for each column.
- Includes:
  - Timesteps
  - Target timesteps
  - Control numbers
- Colour Fill shows typical acceptable values.  Green is valid.
- Subplots are linked:
  - Zooming in on one affects all others

  ![hpc_dt_csv_view](images/HPC_Dt.csv.png)
  
---

### **MB.CSV Files**
- Upload a `*_MB.csv` file to generate subplots with mass balance information.
- Includes:
  - Volumes from boundaries (H, S Estry and X1D boundaries)
  - Total and Cumulative Volumes
  - Mass Error
- Subplots are linked:
  - Zooming in on one affects all others

  ![MB_csv_view](images/MB_CSV.png)

---
 
### **MB_HPC.CSV Files**
- Upload a `*_MB_HPC.csv` file to generate subplots with mass balance information.
- Includes:
  - Volumes from boundaries (H, S Estry and X1D boundaries)
  - Total and Cumulative Volumes
  - Mass Error
- Subplots are linked:
  - Zooming in on one affects all others

  ![MB_HPC_csv_view](images/MB_HPC_CSV.png) 
  
---
 
### **MB2D.CSV Files**
- Upload a `*_MB2D.csv` file to generate subplots with mass balance information.
- Includes:
  - Volumes from boundaries (H, S Estry and X1D boundaries)
  - Total and Cumulative Volumes
  - Mass Error
- Subplots are linked:
  - Zooming in on one affects all others

  ![MB2D_csv_view](images/MB2D_CSV.png)
  
---
 
### **MB1D.CSV Files**
- Upload a `*_MB1D.csv` file to generate subplots with mass balance information.
- Includes:
  - Volumes from boundaries (H, S Estry and X1D boundaries)
  - Total and Cumulative Volumes
  - Mass Error
- Subplots are linked:
  - Zooming in on one affects all others

  ![MB1D_csv_view](images/MB1D_CSV.png)
  
---
 
### **_1D_MB.CSV Files**
- Upload a `*_1D_MB.csv` file to generate 1D node mass balance plots.
	- Dropdown menu can be used to select different nodes and plots mass balance.

  ![1D_MB_csv_view](images/1D_MB_CSV.png)
  
---
 
### **_PO.CSV Files**
- Upload a `*_PO.csv` file to generate time series plots.
	- Dropdown menu can be used to select different Plot Output (PO) points/lines/polygons.

  ![PO_csv_view](images/PO_CSV.png)
  
---
 
### **.tlf Files**
- Upload a `*.tlf` file to generate a table of the TLF settings.
	- Those settings which are not defaults are higlighted.

  ![TLF_Table_view](images/TLF_Table.png)
  
---
 
### **TUFLOW Simulations.log Files**
- Upload a `_ TUFLOW Simulations.log` file to generate a table summary of the success of the simulations.
	- Those settings which are not defaults are higlighted.

  ![TUFLOW_Simulatations_Table_view](images/TUFLOW_Simulations_Table.png)
  
---

### **Messages.csv Files**
- Upload a `*_messages.csv` file to generate a table of the model messages.
	- Counts unique messages and sorts in order from highest to lowest.
	- Colour coded based on severity.
    - Hyperlinked Error messages take you to the TUFLOW Messages Database for the specific error.

  ![Messages_CSV_View](images/Messages_CSV_View.png)
  
---

### **run_stats.txt Files**
- Upload a `*_run_stats.txt` file to generate a plot of the relative contributions of 1D, 2D and Other contributions to the run time.
	- Other includes writing of outputs, and transfer of data to GPU (if running on GPU devices). The “other” column also includes time spent within an external 1D solver.

  ![Run_Stats_View](images/Run_Stats_View.png)
  
---

### **start_stats.txt Files**
- Upload a `*_start_stats.txt` file to generate a plots of the startup times.
	- Plot of the elapsed time of each start up stage.  Useful to identify bottlenecks in the model start up.  Stages with elapsed times less than 0.05s are accumulated into other.
	- Plot of the cumulative start up time accross the various start up stages.

  ![Start_Stats_View](images/Start_Stats_View.png)
  
---

### **.eof Files**
- Upload a `*.eof` file to generate a plot of the node storage tables held within the EOF including storage over obvert.
	- Plot of the surface area versus elevation.  Useful to check defined node storage.
	- Dropdown menu can be used to select different nodes.

  ![EOF_Storage_Table](images/EOF.png)
  
---

## TUFLOW FV Plots

### TUFLOW FV **points.csv Files**
- Upload a TUFLOW FV `*_points.csv' file to generate a plot of the time series results for each point.
	- Dropdown menu can be used to select different points.

  ![FV_Points](images/FVpoints.png)
  
---

### TUFLOW FV **flux.csv Files**
- Upload a TUFLOW FV `*_flux.csv' file to generate a plot of the time series results for each flux line.
	- Dropdown menu can be used to select different flux lines.

  ![FV_Flux](images/FVflux.png)
  
---

### TUFLOW FV **structflux.csv Files**
- Upload a TUFLOW FV `*_flux.csv' file to generate a plot of the time series results for each structure line.
	- Dropdown menu can be used to select different structure lines.

  ![FV_structure](images/FVstructflux.png)
  
---

### TUFLOW FV **mass.csv Files**
- Upload a TUFLOW FV `*_mass.csv' file to generate a plot of the time series results for the model mass.
	- Top plot shows the total model volume and mass.
	- Dropdown menu can be used to select different determinant mass on the second plot.

  ![FV_Mass](images/FVmass.png)
  
---

### TUFLOW FV **massbalance.csv Files**
- Upload a TUFLOW FV `*_mass.csv' file to generate a plot of the time series results for the model mass.
	- Top plot shows the total determinent mass/volume within the model.
	- Second plot shows the determinant fluxes throughout the simulation.

  ![FV_Mass_Balance](images/FVmassbalance.png)
  
---

### TUFLOW FV **ext_cfl_dt.csv and int_cfl_dt.csv Files**
- Upload a TUFLOW FV `*ext_cfl_dt.csv' or `*int_cfl_dt.csv'file to generate a plot of mesh element centroids and the relative timestep %.  Useful to highlight small timesteps within the model domain
	- Top plot shows a map of the mesh element centroids themed by the timestep.  Use the dropdown menu to select the Minimum timestep (cfl_dt_min) or the mean timestep (cfl_dt_mean).
  - Use the slider to show mesh elements centroid lower than the selected percentile.- The bottom plot shows a histogram of the timestep values.
	

  ![FV_CFL_Timesteps](images/FV_CFL_Timestep.png)
  
---

### TUFLOW FV **.log**
- Upload a TUFLOW FV `*.log' to generate a plot of the timesteps being used.
	- Top plot shows a time-series of the internal and external timesteps being used within the simulation
  - The bottom plot shows a time-series of the elapsed time.  
	
  ![FV__Timesteps](images/FV_Timestep.png)
  
---

## Dashboard Menu Items

- Hover in the top-right corner of the dashboard to reveal the menu bar.
- Tools available:
  - Zoom
  - Pan to full extent
  - Reset axes
  - Toggle spike lines
  - Download plot as PNG
  - And more

  ![plotly_tools](images/Spike_lines.png)
---

