# from mcp.server import FastMCP
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
import requests
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import os

mcp = FastMCP("company-details" )




COMPANY_DATA_URL = "https://www.corpvue.com/gateway/cometsearch/open/companyorllp"

CIN_FETCH_URL = "https://www.corpvue.com/gateway/cometsearch/open/searchcompanyorllp"

DIRECTOR_DATA_URL = "https://www.corpvue.com/gateway/cometsearch/directorsDetailsByDin"


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
def get_company_cin_or_llp_number(companyName: str) -> dict:
    """
    description: Fetch company/LLP Number details using company name.

    args: unique company name

    response : response will be a top 10 to 15 cin/LLP number JSON format data of that particular company Name

    """

    response = requests.get(
        f"{CIN_FETCH_URL}?query={companyName}",
        timeout=30,
        verify=False,
    )

    response.raise_for_status()

    return response.json()



import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("company-mcp")
from fastmcp.server.dependencies import get_http_request

def get_auth_header() -> str:

    request = get_http_request()

    logger.info("MCP request received")
    logger.info("Request headers: %s", dict(request.headers))

    x_token = request.headers.get("x-token")

    if x_token:
        logger.info("Using x-token")
        return f"Bearer {x_token}"

    auth_header = request.headers.get("authorization")

    if auth_header:
        logger.info("Authorization header received")
        return auth_header

    logger.error("NO AUTHORIZATION HEADER")

    raise ValueError("Authentication token is missing")

@mcp.tool()
def get_director_detail_via_din(din_number: str) -> dict:
    
    """
        description: Fetch director details using din number.
    
        args: unique din number
    
        response : response will be a complete details of a director fetched by din number in json format 
    
    """

    logger.info(
        "get_director_detail_via_din called. DIN=%s",
        din_number
    )

    auth_header = get_auth_header()

    logger.info(
        "Calling CorpVue API. Auth present=%s",
        bool(auth_header)
    )

    response = requests.get(
        f"{DIRECTOR_DATA_URL}?din={din_number}",
        headers={
            "Authorization": auth_header
        },
        timeout=30,
        verify=False,
    )

    logger.info(
        "CorpVue response status=%s",
        response.status_code
    )

    response.raise_for_status()

    return response.json()

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Development only
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
    )
]

app = mcp.http_app(middleware=middleware,stateless_http=True)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
    )
