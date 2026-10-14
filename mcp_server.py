
from mcp.server.fastmcp import FastMCP

from banking_data import (
    get_unsettled_trades as find_trades,
    get_payment_status as find_payment
)

mcp = FastMCP("FX Banking Tools")


@mcp.tool()
def get_unsettled_trades() -> list:
    """Get all unsettled mock FX trades."""
    return find_trades()


@mcp.tool()
def get_payment_status(payment_id: str) -> dict:
    """Get payment status using a payment ID."""
    return find_payment(payment_id)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
