import os
import googlemaps


"""get company info from google maps"""
def get_company_info(company_name, city):
    GMAPS_API_KEY = os.getenv("GMAPS_API_KEY")
    gmaps = googlemaps.Client(key=GMAPS_API_KEY)
    place_results = gmaps.places(query=f"{company_name} {city}")

    if place_results['status'] == 'OK' and len(place_results['results']) > 0:
        place = place_results['results'][0]

        place_details = gmaps.place(place_id=place['place_id'], fields=['website', 'formatted_phone_number', 'formatted_address', 'geometry', 'name'])
        if place_details['status'] == 'OK':
            name = place_details['result'].get('name', 'not available')
            address = place_details['result'].get('formatted_address', 'not available')
            website = place_details['result'].get('website', "not available")
            phone = place_details['result'].get('formatted_phone_number', "not available")
            lat = place_details['result']['geometry']['location']['lat']
            lng = place_details['result']['geometry']['location']['lng']

        return {
            "company_name": name,
            'address': address,
            'website': website,
            "phone": phone,
            'lat': lat,
            'lng': lng
        }
    else:
        return None