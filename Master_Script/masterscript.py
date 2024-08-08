import subprocess
import logging

# Configure logging
logging.basicConfig(
    filename='data_processing.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Adding console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

def run_script(script_name):
    try:
        logging.info(f"Starting {script_name}")
        result = subprocess.run(['python', script_name], capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"{script_name} failed with error: {result.stderr}")
            return False
        logging.info(f"{script_name} completed successfully")
        return True
    except Exception as e:
        logging.error(f"Exception occurred while running {script_name}: {e}")
        return False

scripts = [r'C:\Users\shrey\OneDrive\Desktop\Projects\GeoSpace News\ISRO BHUMI\Web_Scraper\scraper_latest.py', r'C:\Users\shrey\OneDrive\Desktop\Projects\GeoSpace News\ISRO BHUMI\Text Classification\main.py', r'C:\Users\shrey\OneDrive\Desktop\Projects\GeoSpace News\ISRO BHUMI\NLP_Places\placeget.py', r'C:\Users\shrey\OneDrive\Desktop\Projects\GeoSpace News\ISRO BHUMI\NLP_Places\Most_frequent\mostfrequent_delete.py',r'C:\Users\shrey\OneDrive\Desktop\Projects\GeoSpace News\ISRO BHUMI\Geocoding\geolatest0.py']

for script in scripts:
    if not run_script(script):
        logging.error(f"Stopping execution due to failure in {script}")
        break

print("Data processing completed. Check data_processing.log for details.")