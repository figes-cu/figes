# Fine Granularity Energy Storage- Web App  

- Select energy storage configuration parameters
- Indicate the electrical price profile to be used for optimization. The options for defining the profile are
	- Create a customizable profile by moving values interactively. Maximum 24 values.
	- Upload a .csv with price values and indicate the period in minutes of the uploaded series.  
- Press the optimize button and the system will find optimal charging and discharging periods considering operating constrains. 
- (Optional) Press the download results button to analyze the results in your device.

### Verify existing functionality   
- Clone the repository and target your directory  
- Install the necessary packages:  
  - `figesapp (main) $ alias pip=pip3`
  - `figesapp (main) $ pip install -r requirements.txt`
- Test that the app works:
  - `figes (main) $ python manage.py runserver 8080`
  - Go to the link running the application.
