from mcp.server.fastmcp import FastMCP
import requests
import os


mcp = FastMCP("company-details")


COMPANY_DATA_URL = "https://www.corpvue.com/gateway/cometsearch/open/companyorllp"

CIN_FETCH_URL = "https://www.corpvue.com/gateway/cometsearch/open/searchcompanyorllp"


@mcp.tool()
def get_company_details(cin_or_llp: str) -> dict:
    """
    description: Fetch company/LLP details using CIN or LLP number.

    args: unique cin number or llpin number

    response : response will be a JSON format data of that particular company

    """

    params = {
        "type": "company",
        "cinllpid": cin_or_llp,
    }

    response = requests.get(
        COMPANY_DATA_URL,
        params=params,
        timeout=30,
        verify=False,
    )

    response.raise_for_status()

    return response.json()


@mcp.tool()
def get_company_cin_or_llp_number(compnayName: str) -> dict:
    """
    description: Fetch company/LLP Number details using company name.

    args: unique company name

    response : response will be a top 10 to 15 cin/LLP number JSON format data of that particular company Name

    """

    response = requests.get(
        f"{CIN_FETCH_URL}?query={compnayName}",
        timeout=30,
        verify=False,
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    mcp.run( transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),)
