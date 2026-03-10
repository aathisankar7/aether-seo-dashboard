import json
import os

class LocalCitationManager:
    def __init__(self, data_file="./seo_project/citation_data.json"):
        self.data_file = data_file
        self.nap_data = {
            "business_name": "Ritz Group",
            "address": "Banjara Hills, Hyderabad, Telangana 500034, India",
            "phone": "+91-40-XXXX-XXXX",
            "website": "https://ritzgroup.co",
            "description": "Expert investment advisory and data consulting."
        }
        self.target_directories = [
            "Google My Business",
            "JustDial",
            "Sulekha",
            "UAE Yellow Pages",
            "Yelp",
            "LinkedIn Company Directory",
            "Bing Places"
        ]

    def generate_nap_report(self):
        """Generates a standardized NAP report for manual or automated submission."""
        report = f"""
======================================
Ritz Group - Official NAP Master Data
======================================
Use this EXACT format when submitting to local directories to avoid SEO penalties.

Business Name : {self.nap_data['business_name']}
Full Address  : {self.nap_data['address']}
Phone Number  : {self.nap_data['phone']}
Website URL   : {self.nap_data['website']}
Description   : {self.nap_data['description']}
======================================

Target Directories to Audit/Submit:
"""
        for i, directory in enumerate(self.target_directories, 1):
            report += f"{i}. [ ] {directory}\n"
            
        print(report)
        return report

    def save_nap_data(self):
        """Saves the master NAP data for other scripts (like schema_builder) to use."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w") as f:
            json.dump(self.nap_data, f, indent=4)
        print(f"✅ Master NAP data saved to {self.data_file}")

if __name__ == "__main__":
    manager = LocalCitationManager()
    manager.generate_nap_report()
    manager.save_nap_data()
