from appliance.handlers.factory import initialize_appliance
from bill.handlers.factory import initialize_bill
from controlpanel.handlers.factory import initialize_controlpanel
from docs.handlers.factory import initialize_documents
from compute.handlers.factory import initialize_compute 
from core.consts import ZONE_URLS
from networking.handlers.factory import initialize_networking
from objectstorage.handlers.factory import initialize_objectstorage
from objectstorage.consts import OBJDCTSTORAGE_ZONE_URLS
from core.mcp import create_mcp
from storage.handlers.factory import initialize_storage


# ====================
# main
# ====================
def main():
    # Initialize mcp 
    mcp = create_mcp()

    initialize_documents(mcp)
    initialize_compute(mcp, ZONE_URLS)
    initialize_storage(mcp, ZONE_URLS)
    initialize_networking(mcp, ZONE_URLS)
    initialize_appliance(mcp, ZONE_URLS)
    initialize_objectstorage(mcp, OBJDCTSTORAGE_ZONE_URLS)
    initialize_bill(mcp, ZONE_URLS)
    initialize_controlpanel(mcp, ZONE_URLS)

    mcp.run()


if __name__ == "__main__":
    main()
