# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [ToDo]

- Conversion SVG to PNG so that the maps can be added to the REST API smoothly
- graphs with two different y-axis to compare e.g. *DailyCases* with vaccination effort.

## [Unreleased]

-

## [5.2.0] - 2021-07-19

### Added

- A method called *create_combined_data frame_by_geoid_string_list* was added to the *CovidCases* class. The method will create a combined data frame from a list of individual data fames. To avoid duplicate country names the method will add a *-DATASOURCE* string behind the country name (e.g. 'Germany-OWID'). 
- The *CovidCasesOWID* now provides information about the vaccination status of a country. This includes the following attributes:  

1. DailyVaccineDosesAdministered7DayAverage  
    New COVID-19 vaccination doses administered (7-day smoothed). For countries that don't report vaccination data on a daily basis, we assume that vaccination changed equally on a daily basis over any periods in which no data was reported. This produces a complete series of daily figures, which is then averaged over a rolling 7-day window. In OWID words this is the new_vaccinations_smoothed value.  

2. PeopleReceivedFirstDose  
    Total number of people who received at least one vaccine dose. In OWID words this is the people_vaccinated value.  

3. PercentPeopleReceivedFirstDose  
    The percentage of people of the population who received at least one vaccine dose.  

4. PeopleReceivedAllDoses  
   Total number of people who received all doses defined by the vaccination protocol. In OWID words this is the people_fully_vaccinated value.  

5. PercentPeopleReceivedAllDoses  
   The percentage of people of the population who received all doses defined by the vaccination protocol.  

6. VaccineDosesAdministered  
    Total number of COVID-19 vaccination doses administered. It's the sum of *PeopleReceivedFirstDose* and *PeopleReceivedAllDoses*. In OWID words this is the total_vaccinations value.  

- A method called *set_grid* has been added to toggle the display of a grid in the *PlotterBuilder* class.  

- The method *set_log* of the *PlotterBuilder* class now has an argument to toggle between a linear or logarithmic y-axis.  

- The method *set_xaxis_index* now has a parameter to toggle between index or date based x-axis.

- A new attribute *__xaxis_formatter* has been add to the *PlotterBuilder* class. The attribute can be changed by *set_yaxis_formatter*. The default yaxis_formatter is now ```mpl.ticker.StrMethodFormatter('{x:,.0f}') ```.

- The Jupyter Notebook now includes the vaccination data for the given list of countries.

### Changed  

- The *CovidCasesWHO* class included Taiwan in the return of a call to *get_pygal_asian_geoid_list* even when Taiwan was not included in the WHO dataset. Because of that the generation of Asian pygal maps were incorrect.  

- There was a bug in the method *__compute_doubling_time* of the *CovidCase*s class that could lead to a division by zero.  

### Removed  

-  

## [5.1.0] - 2021-03-16

### Added

- The MacOS application now supports the Apple M1 processor. Use [this link](http://mb.cmbt.de/download-area/) to get the MacOS and Windows applications to access an online version of the Covid-19 REST API. After copying the MacOS application to the *applications* directory you need to start it for the first time with a right-click and selecting *execute* to approve the application. Afterwards you can start it with the regular double-click. This is the common procedure for none-AppStore applications.     

### Changed  

-  
### Removed  

-  

## [5.0.0] - 2021-01-14

### Added

- support for different data provider e.g. ECDC, WHO and OWID
- new Jupyter Notebook to compare the quality of different data provider  
- new CovidCasesECDC class to download the data from the ECDC server  
- new CovidCasesWHO class to download the data from the WHO server
- new CovidCasesWHOv1 class to download the data from an alternative WHO server
- new CovidCasesOWID class to download the data from the OWID server
- new GeoInformationWorld class to handle ISO 3166 alpha-2 and alpha-3 GeoIDs
- new GeoInformationWorld.csv file in the data directory
- new GeoInformationWorld.xlsx file in the data directory
- new 2020-12-14-ECDC.csv file holding the ECDC until December 14th.
- new 2020-12-14-WHO.csv file holding the WHO until December 14th.
- new 2020-12-14-OWID.csv file holding the OWID until December 14th.

### Changed

- The CovidDataClass Jupyter Notebook can now use different data providers and defaults to WHO data  
- The CovidCases class now acts as a abstract class for its sub-classes  
- The PlotterBuilder class reflects changes in CovidCases  
- The CovidMap class reflects changes in CovidCases  
- The CovidClassSnippet reflects changes in CovidCases

### Removed

-
## [4.1.0] - 2020-11-30

### Added

- a MacOS web client is now also available

### Changed

- .gitignore  now includes XCode files
- duplicates in .gitignore have been removed
- some minor typos

### Removed

-

## [4.0.0] - 2020-10-23

### Added

- introduced a change log
- added functions to get the country codes for the continents
- added a class to display maps of the worldwide distribution of the data
- added a class to visualize data in a heatmap
- added a favicon
- added map generation to Junyper Notebook

### Changed

- The C# web client can now save the generated graphs
- changed the documentation method to make use of the *Python Docstring Generator*
- modified *requirements.txt*

### Removed

- removed the class sources from the Jupyter Notebook

## [3.0.0] - 2020-09-21

### Added

- added method to get a list of available GeoIDs/CountyNames (get_available_GeoID_list)
- added method to get the accumulated 7 day incidence (add_incidence_7day_per_100Kpopulation)

### Changed

- renamed 'Cases' to 'DailyCases'
- renamed 'Deaths' to 'DailyDeaths'
- renamed 'CumulativeCases' to 'Cases'
- renames 'CumulativeDeaths' to 'Deaths'

### Removed

-

## [2.0.0] - 2020-08-07

### Added

- added a function to lowpass a attribute  
  The width of the lowpass is given by the number n. The name of the newly
  created attribute is the given name with a tailing number n. E.g. 'Cases' 
  with n = 7 will add to a newly added attribute named 'Cases7'.
- added a function to save a dataframe to a CSV file
- added a function to calculate an estimation for the reproduction rate R0

### Changed

- instead of the ECDC JSON file we are now using the CSV with the same data
- instead of the JSON data structure we are now using a Pandas data frame
  Both changes allow us to easier add new methods and analytics
- the attribute 'Quotient' has been removed. the attribute was the number
  of cases on the day divided by the number of cases of the
  previous day
- 'Continent' is a new field to analyse the distribution of cases over
  continents

### Removed

- support for the JSON file of the ECDC

## [1.1.0] - 2020-04-18

### Added

- Added a REST API
- Added a C# client making use of the REST API
- The database file is now loaded automatically if it doesn't exist for the current day
- Applying some PEP8 style guides
- Add function to get the data for the last N days

### Changed

-  

### Removed

- 

## [1.0.0] - 2020-04-18

### Added

- Initial commits finalized

### Changed

-  

### Removed

- support for the JSON file of the ECDC
