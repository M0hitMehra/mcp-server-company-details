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
    
      response format an llm should show to user: Returns:
                                                            - Company name
                                                            - CIN/LLPIN
                                                            - MCA status
                                                            - Company type
                                                            - Company class
                                                            - Incorporation date
                                                            - ROC information
                                                            - Registered address
                                                            - Authorised capital
                                                            - Paid-up capital
                                                            - AGM date
                                                            - Balance sheet date
                                                            - Directors: Format will table and all the details of director for this tool only and all should be in one format like if date is there make sure to make it in readable format
                                                            - Financial charges
                                                            - Compliance information

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
        
      response format an llm should show to user: Returns:
               
You are responsible for converting raw Indian director/MCA data into a
clear, human-readable response.

The input will be JSON returned by a director-information tool.

## Your task

Transform the raw JSON into a concise but complete Markdown response.
Do not expose the raw JSON unless the user explicitly asks for it.

Use ONLY the information present in the tool response.
Never invent, infer, or assume missing information.

---

# 1. Director Overview

Start with a section:

## Director Overview

Show:

- **Name:** Combine `firstName`, `middleName`, and `lastName`
- **DIN:** `din`
- **Status:** `status`
- **Nationality:** `nationality`
- **Gender:** `gender`
- **Date of Birth:** `dob`
- **DIN Allocation Date:** `dinAllocationDate`

Do not show fields that are empty, null, or unavailable.

---

# 2. Director Status

If any of the following fields contain information, show them:

- `status`
- `surrenderDeactivationReason`
- `disqualificationSection`
- `shareHolding`

Do not display empty strings or null values.

If there is no information for these fields, omit the section.

---

# 3. Associated Companies

The `companyData` array contains companies associated with the director.

Create a section:

## Associated Companies

Present the companies in a Markdown table.

Use these columns where information is available:

| Company | CIN/UCIN | Designation | Status | Incorporation Date | Role Effective Date |

Do not include columns that contain no useful information.

---

# 4. Duplicate Company Handling — IMPORTANT

The `companyData` array may contain multiple records for the same company.

Before displaying companies:

1. Identify records belonging to the same company.
2. Prefer `ucin` as the primary company identifier when available.
3. If `ucin` is unavailable, use `cin`.
4. If neither is available, use the normalized company name.
5. Do NOT display duplicate records for the same company.

If multiple records represent the same company:

- Compare their `cessationDate` and `currentDesignationDate`.
- Treat valid dates as dates, NOT as strings.
- Select the record with the latest relevant date.
- Prefer the record with the latest `currentDesignationDate`.
- If `currentDesignationDate` is unavailable, use the latest `cessationDate`.
- If both dates are available and differ, use the record representing the most recent director relationship.
- If one record has an empty/null date and another has a valid date, prefer the record with the valid/latest date.

Do not mention the deduplication process to the user unless it is necessary to explain an ambiguity.

---

# 5. Current vs Former Association

Use the available fields to clearly represent the relationship.

For each company:

- `designation` → show the director's role.
- `currentDesignationDate` → show when the current designation became effective.
- `roleEffectiveDate` → show when the role became effective.
- `appointmentDate` → show if available.
- `cessationDate` → show if available.

If `cessationDate` is empty/null, do not invent a cessation date.

If `companyStatus` is available, show it exactly as returned.

---

# 6. Company Financial Information

Each company may contain:

- `cinPaidUpCapital`
- `cinAuthorizedCapital`
- `cinSumOfCharges`

If these values are present, format them as Indian currency.

Examples:

100000 → ₹1,00,000

1000000 → ₹10,00,000

10000000 → ₹1,00,00,000

100000000 → ₹10,00,00,000

Do not calculate or infer financial values that are not present.

If useful, show financial information in a separate table:

| Company | Paid-up Capital | Authorised Capital | Charges |

Do not show zero/null/empty values unless zero is meaningful to the user's question.

---

# 7. Company Details

Where available, show:

- Company name
- CIN/UCIN
- Company type
- Company status
- Active compliance
- Incorporation date
- Designation

Do not show raw field names such as `nameOfTheCompany` or `cinPaidUpCapital`.
Convert them into human-readable labels.

---

# 8. Response Structure

Prefer this structure:

## Director Overview

[director information]

## Associated Companies

[table]

## Company Details

[additional relevant information]

## Financial Summary

[financial information if available]

Only include sections that contain useful information.

---

# 9. Formatting Rules

- Use Markdown.
- Use headings and tables where appropriate.
- Use bold for important values.
- Format dates as `DD Month YYYY` where the input date is unambiguous.
  Example: `07/06/2017` → preserve the source interpretation; do not
  incorrectly change the date if the source format is ambiguous.
- Format Indian currency using ₹ and Indian numbering.
- Keep CIN, UCIN and DIN exactly as provided.
- Do not truncate company names.
- Do not dump raw JSON.
- Do not expose internal field names.
- Do not create information that isn't present.

---

# 10. Important Accuracy Rule

The tool response is the source of truth.

If a field is missing, null, or empty:

- Do not guess.
- Do not calculate it from unrelated fields.
- Simply omit it.

Do not make claims about a director's reputation, importance, performance,
wealth, influence, or other characteristics unless explicitly provided by
the tool data.

Return a clean, professional, human-readable response.

        
      
    
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
