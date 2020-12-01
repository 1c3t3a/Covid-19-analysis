# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [ToDo]

- adding support for different datasources. Could be done by an enumeration passed in to the load datatabase function
- Conversion SVG to PNG so that the maps can be added to the REST API smoothly

## [Unreleased]

-

## [4.1.0] - 2020-11-30

### Added

- a MacOS web client is now also available

### Changed

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
