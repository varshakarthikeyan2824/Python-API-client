from apiclient.client import APIClient

client = APIClient("http://127.0.0.1:9000")

try:
    parcels = list(client.iter_parcels(page_size=50))

    print("Total parcels fetched:", len(parcels))
    print("First parcel:", parcels[0])
    print("Last parcel:", parcels[-1])
finally:
    client.close()
