import json
import os

class SchemaBuilder:
    def __init__(self, base_url="https://ritzgroup.co"):
        self.base_url = base_url
        self.organization_name = "Ritz Group"

    def build_organization_schema(self):
        """Builds the main Organization schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.organization_name,
            "url": self.base_url,
            "logo": f"{self.base_url}/logo.png",
            "sameAs": [
                "https://www.linkedin.com/company/ritz-group",
                "https://twitter.com/ritzgroup",
                "https://www.facebook.com/ritzgroup"
            ],
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": "+91-XXXXXXXXXX",
                "contactType": "customer service"
            }
        }
        return schema

    def build_local_business_schema(self, location_name, address, telephone):
        """Builds LocalBusiness schema for specific office locations."""
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": f"{self.organization_name} - {location_name}",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": address.get("street"),
                "addressLocality": address.get("city"),
                "addressRegion": address.get("region"),
                "postalCode": address.get("postal_code"),
                "addressCountry": address.get("country")
            },
            "telephone": telephone,
            "url": self.base_url
        }
        return schema

    def build_service_schema(self, service_name, description):
        """Builds Service schema for Ritz Group offerings."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Service",
            "serviceType": service_name,
            "provider": {
                "@type": "Organization",
                "name": self.organization_name
            },
            "description": description
        }
        return schema

    def save_schema(self, schema, filename):
        """Saves the schema to a JSON file."""
        os.makedirs("./schemas", exist_ok=True)
        filepath = os.path.join("./schemas", filename)
        with open(filepath, "w") as f:
            json.dump(schema, f, indent=4)
        print(f"✅ Schema saved to {filepath}")
        return filepath

if __name__ == "__main__":
    builder = SchemaBuilder(base_url="https://cosmosclinics.in/")
    builder.organization_name = "Cosmos Clinics"
    
    # 1. Org/MedicalClinic Schema (using Organization as a base for MedicalClinic)
    org_schema = builder.build_organization_schema()
    org_schema["@type"] = ["Organization", "MedicalClinic"] # Dual typing is good for SEO
    org_schema["logo"] = "https://cosmosclinics.in/wp-content/uploads/2023/10/cosmos-logo.png"
    builder.save_schema(org_schema, "cosmos_organization.json")
    
    # 2. Local Business (Kukatpally)
    kphb_address = {
        "street": "Kukatpally",
        "city": "Hyderabad",
        "region": "Telangana",
        "postal_code": "500072",
        "country": "IN"
    }
    loc_schema = builder.build_local_business_schema("Kukatpally Clinic", kphb_address, "+91-9999999999")
    loc_schema["@type"] = ["LocalBusiness", "MedicalClinic", "Dentist"]
    builder.save_schema(loc_schema, "cosmos_local_business_kphb.json")
    
    # 3. Service (Smile Makeovers)
    service_schema = builder.build_service_schema(
        "Smile Makeover and Painless Dentistry", 
        "Comprehensive smile design, teeth whitening, and cosmetic dentistry using advanced, painless techniques."
    )
    builder.save_schema(service_schema, "cosmos_service_smile_makeovers.json")
