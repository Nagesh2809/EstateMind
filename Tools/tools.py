"""
MCP server for the Real Estate Agent.

This exposes the same functionality as your FastAPI endpoints (main.py) as MCP
tools, calling the `Rules` class directly (no HTTP round-trip) so it can be
used by any MCP-compatible client (Claude Desktop, Claude Code, LangChain's
MCP adapters, etc.) instead of the old LangChain `Tool` wrappers that hit
`requests.get(f"{BASE_URL}/...")`.

Run it with:
    pip install "mcp[cli]" pandas geopy
    python mcp_server.py

Or, for local dev/testing with the MCP inspector:
    mcp dev mcp_server.py

To connect it to Claude Desktop, add to claude_desktop_config.json:
{
  "mcpServers": {
    "real-estate": {
      "command": "python",
      "args": ["D:\\Real_Estate_Agent\\mcp_server.py"]
    }
  }
}
"""

from typing import Optional, List, Dict, Any
import re

import pandas as pd
from geopy.distance import geodesic
from fastmcp import FastMCP

mcp = FastMCP("real-estate")


# ---------------------------------------------------------------------------
# Data + Rules class (same logic as in main.py)
# ---------------------------------------------------------------------------

df = pd.read_csv('Datasampling-konu - Sheet1.csv')


class Rules:
    def __init__(self) -> None:
        self.df = df
        self.min_price = None
        self.max_price = None
        self.area = None

    def select_city(self, city):
        if isinstance(city, str):
            self.df = self.df[self.df['city'].str.lower() == city.lower()]
        else:
            raise ValueError("City must be a string")

    def select_locality(self, locality):
        if isinstance(locality, str):
            self.df = self.df[self.df['address'].str.lower() == locality.lower()]
        else:
            raise ValueError("Locality must be a string")

    def pincode_filter(self, pincode):
        if isinstance(pincode, int):
            self.df = self.df[self.df['pincode'] == pincode]
        else:
            raise ValueError("Pincode must be an integer")

    def expected_min_max(self):
        self.df['new price'] = pd.to_numeric(self.df['new price'], errors='coerce')
        min_max = self.df['new price'].dropna()
        self.min_price = min_max.min() if not min_max.empty else 0
        self.max_price = min_max.max() if not min_max.empty else 0

    def bedroom_price(self, rooms=1):
        if isinstance(rooms, int) and rooms > 0:
            self.df = self.df[self.df['BHK'].fillna(0).astype(int) == rooms]
        else:
            raise ValueError("Rooms must be a positive integer")

    def area_price(self, area):
        if isinstance(area, (int, float)) and area > 0:
            self.area = area

            if not isinstance(self.min_price, (int, float)):
                self.min_price = float(self.min_price) if self.min_price else 0.0
            if not isinstance(self.max_price, (int, float)):
                self.max_price = float(self.max_price) if self.max_price else 0.0

            self.min_price *= area
            self.max_price *= area

            if self.min_price > self.max_price:
                self.min_price, self.max_price = self.max_price, self.min_price
        else:
            raise ValueError("Area must be a positive number")

    def gated_community_price(self):
        self.df = self.df[self.df['type'] == 'Gated community']

    def stand_alone_apartments(self):
        self.df = self.df[self.df['type'] == 'Stand Alone']

    def commercial_Spaces(self):
        self.df = self.df[self.df['type'] == 'Commercial Spaces']

    def filter_by_lat_long(self, lat, long, radius_km=2):
        if 'new price' not in self.df.columns:
            raise ValueError("'new price' column not found in the properties data")

        self.df = self.df.dropna(subset=['latitude', 'longitude'])

        if isinstance(lat, (int, float)) and isinstance(long, (int, float)):

            def is_within_range(row):
                try:
                    property_coords = (float(row['latitude']), float(row['longitude']))
                    user_coords = (lat, long)
                    distance = geodesic(user_coords, property_coords).km
                    return distance <= radius_km
                except Exception:
                    return False

            self.df = self.df[self.df.apply(is_within_range, axis=1)]
        else:
            raise ValueError("Latitude and Longitude must be numeric")

    def return_df(self):
        return self.df


def calculate_emi(loan_amount, annual_interest_rate, tenure_years):
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    total_months = tenure_years * 12
    emi = (loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** total_months)) / \
          (((1 + monthly_interest_rate) ** total_months) - 1)
    total_payment = emi * total_months
    total_interest = total_payment - loan_amount
    return emi, total_interest


METRO_STATIONS = {
    "Ameerpet": (17.434803, 78.448011),
    "Assembly": (17.3978004, 78.4699168),
    "Balanagar": (17.4965811, 78.3676732),
    "Begumpet": (17.4375, 78.456667),
    "Bharat Nagar": (17.463997, 78.4278693),
    "Chaitanyapuri": (17.3682882, 78.5357829),
    "Chikkadpally": (17.40036, 78.4949),
    "Dilsukhnagar": (17.3686, 78.5257),
    "Durgam Cheruvu": (17.442778, 78.3875),
    "Erragadda": (17.4567784, 78.4304257),
    "ESI Hospital": (17.4474, 78.43835),
    "Gandhi Bhavan": (17.348426, 78.550959),
    "Gandhi Hospital": (17.42552, 78.50196),
    "Habsiguda": (17.4337, 78.5016),
    "Hitec City": (17.448889, 78.383056),
    "Irrum Manzil": (17.4204695, 78.4539726),
    "JBS Parade Ground": (17.436793, 78.443906),
    "JNTU College": (17.498653, 78.388793),
    "Jubilee Hills Check Post": (17.416471, 78.438247),
    "Road No.5 Jubilee Hills": (17.43005, 78.4232),
    "Khairatabad": (17.41275, 78.45803),
    "KPHB Colony": (17.493780, 78.401795),
    "Kukatpally": (17.485116, 78.409369),
    "LB Nagar": (17.348426, 78.550959),
    "Lakdi-ka-pul": (17.404701, 78.464294),
    "Madhapur": (17.4372, 78.3982),
    "Madhura Nagar": (17.4225704, 78.37887),
    "Malakpet": (17.3772, 78.494),
    "Mettuguda": (17.4355, 78.5196),
    "MG Bus Station": (17.378055, 78.480005),
    "Miyapur": (17.4964, 78.3731),
    "Moosapet": (17.473961, 78.42044),
    "Musarambagh": (17.3711, 78.512),
    "Musheerabad": (17.425544, 78.503795),
    "Nagole": (17.3908477, 78.5587195),
    "Nampally": (17.4367, 78.4674),
    "Narayanaguda": (17.39436, 78.48996),
    "New Market": (17.3734, 78.5031),
    "NGRI": (17.41483, 78.54634),
    "Osmania Medical College": (17.382389, 78.478957),
    "Parade Grounds": (17.436793, 78.443906),
    "Paradise": (17.4435274, 78.4850961),
    "Peddamma Gudi": (17.43065, 78.40837),
    "Prakash Nagar": (17.4425252, 78.4704161),
    "Punjagutta": (17.436793, 78.443906),
    "RTC X Roads": (17.406599, 78.496959),
    "Raidurg": (17.4422, 78.3773),
    "Rasoolpura": (17.443333, 78.475833),
    "S.R Nagar": (17.440269, 78.441833),
    "Secunderabad West": (17.4338, 78.49954),
    "Secunderabad East": (17.4337, 78.5016),
    "Stadium": (17.398795, 78.553844),
    "Sultan Bazaar": (17.385983, 78.480344),
    "Tarnaka": (17.4279, 78.536),
    "Uppal": (17.3987948, 78.5538439),
    "Victoria Memorial": (17.348426, 78.550959),
    "Yusufguda": (17.435083, 78.426528)
}

IT_HUBS = {
    "Hitec City": (17.44155, 78.38264),
    "Madhapur": (17.448294, 78.391487),
    "Gachibowli": (17.440081, 78.348915),
    "Kondapur": (17.467579, 78.692345),
    "Financial District": (17.4117312, 78.3424898),
    "Nanakramguda": (17.4117312, 78.3424898),
    "Manikonda": (17.4000018, 78.3861896794107),
    "Raidurg": (17.416315, 78.389847),
    "Uppal": (17.401810, 78.560188),
    "Pocharam": (17.173595, 78.607178)
}


def _clean_text(value: str) -> str:
    """Normalize a free-text query param the same way the Flask/FastAPI app did."""
    value = re.sub(r'%\d+', ' ', value)
    return value.replace('+', ' ').strip('"').strip().lower()


def _records(dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
    return dataframe.to_dict(orient='records')


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------


# mcp = FastMCP("WeatherTools",host="0.0.0.0", port=8000)

@mcp.tool()
def budget_properties(locality: str, budget: float) -> Dict[str, Any]:
    """Get properties in a locality within a maximum budget (final_price <= budget)."""
    try:
        loc = _clean_text(locality)
        data = df.copy()
        data['final_price'] = pd.to_numeric(data['final_price'], errors='coerce')
        filtered = data[(data['address'].str.lower() == loc) & (data['final_price'] <= budget)]

        columns = ['project name', 'type', 'new price', 'final_price', 'size', 'BHK', 'pincode', 'address', 'city', 'RERA Approved']
        filtered = filtered[columns]

        if filtered.empty:
            return {"message": "No properties found under the specified budget in this locality"}
        return {"properties": _records(filtered)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def available_properties(location: str) -> Dict[str, Any]:
    """Get available properties matching (partial match) a location/address."""
    try:
        loc = _clean_text(location)
        data = df.copy()
        data['address'] = data['address'].fillna('').str.lower()
        filtered = data[data['address'].str.contains(loc, na=False)].copy()

        if filtered.empty:
            return {"message": f"No properties available in or near {loc}"}

        filtered['new price'] = pd.to_numeric(filtered['new price'], errors='coerce')
        filtered['size'] = pd.to_numeric(filtered['size'], errors='coerce')
        filtered['final_price'] = pd.to_numeric(filtered['final_price'], errors='coerce')

        columns = ['project name', 'type', 'new price', 'final_price', 'size', 'BHK', 'pincode', 'address', 'city', 'RERA Approved']
        filtered = filtered[columns]

        return {"properties": _records(filtered)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def market_value(location: str, property_category: Optional[str] = None) -> Dict[str, Any]:
    """Get min/max/mean/median/mode property price for a location, optionally filtered by property category."""
    try:
        loc = _clean_text(location)
        filtered = df[df['address'].str.strip().str.lower() == loc]

        cat = None
        if property_category:
            cat = property_category.strip().lower()
            filtered = filtered[filtered['type'].str.strip().str.lower() == cat]

        if filtered.empty:
            return {"message": "No data available for the specified location and property category"}

        filtered = filtered.copy()
        filtered['new price'] = pd.to_numeric(filtered['new price'], errors='coerce')

        min_price = filtered['new price'].min()
        max_price = filtered['new price'].max()
        mean_price = filtered['new price'].mean()
        median_price = filtered['new price'].median()
        mode_series = filtered['new price'].mode()
        mode_price = mode_series.iloc[0] if not mode_series.empty else None

        return {
            "location": loc,
            "property_category": cat or "All Categories",
            "min_price": int(min_price),
            "max_price": int(max_price),
            "mean_price": float(mean_price),
            "median_price": float(median_price),
            "mode_price": float(mode_price) if mode_price is not None else None,
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def properties_near(latitude: float, longitude: float, radius: float = 2.0) -> Dict[str, Any]:
    """Get properties within `radius` km of a given latitude/longitude, with price stats."""
    try:
        if not (-90 <= latitude <= 90):
            return {"error": "Latitude must be between -90 and 90"}
        if not (-180 <= longitude <= 180):
            return {"error": "Longitude must be between -180 and 180"}
        if radius <= 0:
            return {"error": "Radius must be a positive number"}

        rules = Rules()
        rules.filter_by_lat_long(latitude, longitude, radius)
        filtered = rules.return_df()

        if 'new price' not in filtered.columns:
            return {"error": "'new price' column not found in the properties data"}

        filtered = filtered.copy()
        filtered['new price'] = pd.to_numeric(filtered['new price'], errors='coerce')
        filtered = filtered.dropna(subset=['new price'])

        if filtered.empty:
            return {"message": "No properties found near the given coordinates"}

        mode_series = filtered['new price'].mode()

        return {
            "min_price": float(filtered['new price'].min()),
            "max_price": float(filtered['new price'].max()),
            "mean_price": float(filtered['new price'].mean()),
            "median_price": float(filtered['new price'].median()),
            "mode_price": float(mode_series.iloc[0]) if not mode_series.empty else None,
            "properties": _records(filtered),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def properties_near_metro_station(station_name: str, radius: float = 2.0) -> Dict[str, Any]:
    """Get properties near a named Hyderabad metro station within `radius` km."""
    try:
        name = _clean_text(station_name).title()
        coords = METRO_STATIONS.get(name)
        if not coords:
            return {"error": f"Invalid or unknown metro station name: {station_name}"}

        lat, long = coords
        rules = Rules()
        rules.filter_by_lat_long(lat, long, radius)
        filtered = rules.return_df()

        if filtered.empty:
            return {"message": "No properties found near the specified metro station"}
        return {"properties": _records(filtered)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def properties_near_it_hub(hub_name: str, radius: float = 2.0) -> Dict[str, Any]:
    """Get properties near a named Hyderabad IT hub within `radius` km."""
    try:
        name = _clean_text(hub_name).title()
        coords = IT_HUBS.get(name)
        if not coords:
            return {"error": f"Invalid or unknown IT hub name: {hub_name}"}

        lat, long = coords
        rules = Rules()
        rules.filter_by_lat_long(lat, long, radius)
        filtered = rules.return_df()

        if filtered.empty:
            return {"message": "No properties found near the specified IT hub"}
        return {"properties": _records(filtered)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def rera_approved(location: str = "", project_name: str = "") -> Dict[str, Any]:
    """Get RERA-approved properties, optionally filtered by location and/or project name (partial match)."""
    try:
        loc = _clean_text(location) if location else ""
        proj = _clean_text(project_name) if project_name else ""

        for column in ['RERA Approved', 'Project', 'address']:
            if column not in df.columns:
                return {"error": f"'{column}' column not found in the dataset"}

        filtered = df[df['RERA Approved'].str.strip().str.lower() == 'yes']

        if not loc and not proj:
            return {"rera_approved_properties": _records(filtered)}

        if proj:
            filtered = filtered[filtered['Project'].str.strip().str.lower().str.contains(proj, na=False)]
        if loc:
            filtered = filtered[filtered['address'].str.strip().str.lower().str.contains(loc, na=False)]

        if filtered.empty:
            return {"message": "No RERA-approved properties found matching the criteria"}
        return {"rera_approved_properties": _records(filtered)}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def project_price(project_name: str, area: float = 1.0) -> Dict[str, Any]:
    """Get a project's price, adjusted by area (price * area)."""
    try:
        if area <= 0:
            return {"error": "Area must be a positive number"}

        name = _clean_text(project_name)
        data = df.copy()
        data['project name'] = data['project name'].str.strip().str.lower()
        filtered = data[data['project name'].str.strip().str.lower() == name]

        if filtered.empty:
            return {"message": "No project found with the given name"}

        filtered['new price'] = pd.to_numeric(filtered['new price'], errors='coerce')
        if filtered['new price'].isna().all():
            return {"message": "Price information not available for this project"}

        filtered['adjusted_price_with_area'] = filtered['new price'] * area

        return {"projects": _records(filtered[['project name', 'new price', 'adjusted_price_with_area']])}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def calculate_emi_tool(loan_amount: float, tenure_years: float, annual_interest_rate: float) -> Dict[str, Any]:
    """Calculate the monthly EMI and total interest for a loan."""
    try:
        if loan_amount <= 0 or tenure_years <= 0 or annual_interest_rate <= 0:
            return {"error": "All input values must be positive numbers."}

        emi, total_interest = calculate_emi(loan_amount, annual_interest_rate, tenure_years)
        return {
            "loan_amount": loan_amount,
            "annual_interest_rate": annual_interest_rate,
            "tenure_years": tenure_years,
            "emi": round(emi, 2),
            "total_interest": round(total_interest, 2),
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def filter_properties(
    locality: Optional[str] = None,
    pincode: Optional[int] = None,
    property_category: Optional[str] = None,
    bhk: Optional[int] = None,
    area: Optional[float] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    """Filter properties by locality, pincode, property category, BHK, and area, with pagination."""
    try:
        rules = Rules()

        if locality:
            rules.select_locality(locality)

        if pincode is not None:
            rules.pincode_filter(int(pincode))

        if property_category:
            if property_category == 'Gated community':
                rules.gated_community_price()
            elif property_category == 'Stand Alone':
                rules.stand_alone_apartments()
            elif property_category == 'Commercial':
                rules.commercial_Spaces()

        if bhk is not None:
            rules.bedroom_price(int(bhk))

        if area is not None and area > 0:
            rules.expected_min_max()
            rules.area_price(area)
        else:
            rules.expected_min_max()
            rules.area_price(1.0)

        filtered = rules.return_df()

        if filtered.empty:
            return {
                "message": "No properties found matching the given filters",
                "min_price": rules.min_price,
                "max_price": rules.max_price,
            }

        start = (page - 1) * page_size
        end = start + page_size
        page_df = filtered[start:end]

        return {
            "properties": _records(page_df),
            "min_price": rules.min_price,
            "max_price": rules.max_price,
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8005,
    )