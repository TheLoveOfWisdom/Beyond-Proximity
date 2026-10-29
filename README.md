# Beyond Proximity: Mapping Invisible Food Deserts via Geospatial AI

**Author:** Steven Xu  
**Role:** Lead Developer / Researcher  
**Region:** York Region, Ontario, Canada

## 📌 Project Overview
Despite being one of Canada's most affluent municipalities, York Region has seen food bank demand double since 2019, with over 22% of households facing food insecurity. 

**Beyond Proximity** is a Python-based Operations Research model. It proves that geographic proximity to a food bank does not equal accessibility. By utilizing Graph Theory and a custom A* pathfinding algorithm, this project calculates the actual transit friction vulnerable families face, revealing hidden "Food Deserts" in affluent suburbs.

### 🔗 Live Interactive Map
👉 **[Click here to view the live Food Desert Heatmap]( https://TheLoveOfWisdom.github.io/Beyond-Proximity/york_region_food_deserts.html )**

---

## ⚙️ The Math: Food Access Friction Index (FAFI)
Standard urban planning uses "Euclidean (straight-line) distance." This algorithm replaces that with **FAFI**.
The program models the York Region road network (24,000+ intersections, 61,000+ roads) and routes 1,184 neighborhoods to 27 food bank hubs. 

FAFI penalizes routes based on logistical realities:
- **Drive/Transit Time:** Calculated using OpenStreetMap network data.
- **Capacity Bottlenecks:** Locations with strict "Appointment Only" rules receive a 1.5x mathematical friction penalty.

---

## 📊 Key Findings (The "Missing Middle")
The final visualization filters out ultra-wealthy neighborhoods to isolate the working-class and vulnerable populations (Median After-Tax Income < $95k). 
- **Yellow Zones:** Low income, but low friction (System is working).
- **Dark Red Zones:** Low income + High friction (**True Food Deserts**).

---

## 🛠️ Tech Stack
- **Languages:** Python 3
- **Geospatial & Math:** `GeoPandas`, `OSMnx`, `NetworkX`, `Shapely`
- **Visualization:** `Folium`, `Branca` (Esri Canvas)
- **Data Sources:** Statistics Canada 2021 Census, York Region Open Data, FBYR.

---

## 🚀 How to Run Locally (For Developers)
1. Clone the repository: `git clone https://github.com/yourusername/York-Region-Food-Bank.git`
2. Create virtual environment: `python3 -m venv venv`
3. Install dependencies: `pip install pandas geopandas osmnx networkx folium branca`
4. Run scripts in the `/src` folder in sequential order (01 to 06).
