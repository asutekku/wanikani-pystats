# Wanikani PyStats

A simple python script to generate an comprehensive spreadsheet you can use to analyze your data.

## Running

Clone the repository or download the wanikani.py script.

Edit the wanikani.py -file to have your v2-api key at *api_V2 = ""* so it will read something like *api_V2 = "asdasd-asdasd-asdasd-asdasd"*.

Run the wanikani.py script with python3. Depending of the amount of your reviews, it will do the job in from few seconds to two minutes.

It will generate two files to the scripts location. daystats.csv and subjects.csv. The data will be in daystats.csv

Subjects.csv is generated so you don't need to download the subjects from the wanikani API every single time you run the script.

The CSV file will be semicolon seperated.