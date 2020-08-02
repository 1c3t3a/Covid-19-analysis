# Covid-19-analysis
![](https://github.com/1c3t3a/Covid-19-analysis/workflows/Run%20jupyter%20notebook/badge.svg)<br>
![Docker](https://github.com/1c3t3a/Covid-19-analysis/workflows/Docker/badge.svg)<br>
![Run class snippet](https://github.com/1c3t3a/Covid-19-analysis/workflows/Run%20class%20snippet/badge.svg)<br><br> 

## Introduction
Gets the WHO data about COVID-19 from the [European Center of Disease Control](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide) and visualize them.<br>
Additionally it will calculate some important numbers such as the doubling time and the reproduction number R0. To do so it offers a set of Python classes and functions including a Jupyter notebook to generate PDF reports. The functions are also available through a REST API and the repository offers a C# application in source code to call the REST API.<br><br>
## Installation
You basically neet to install the JupyterLab, MatPlotLib and Pandas libraries. To use some interactins in the notebook we are using ipywidgets as well.  
These are the pip commands to install the packes:  
```
pip install jupyterlab  
pip install pandas  
pip install matplolib  
pip install ipywidgets  
``` 
In order to get ipywidgets working with jupyter notebook please run the following command:  
```
jupyter nbextension enable --py --sys-prefix widgetsnbextension
```
    
If you're using jupyter lab you also have to register the extension:  
```
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```
  
Please refer to: [https://github.com/jupyter-widgets/ipywidgets/blob/master/README.md](https://github.com/jupyter-widgets/ipywidgets/blob/master/README.md)  
  
When exectuing the second command you may wonder that the terminal is somehow standing still. Don't worry, start the jupyter notebook in a second terminal using:  

```
jupyter lab
```
  
For your convenience we added all of these indivdual installtion to one requirements text file that you can execute using the one and only following command (you will find requirements.txt in the root folder of this project):  
```
pip install -r requirements.txt
```


## Using a Docker image to execute the REST API
To build the Docker image use the following command line:

```
docker build -t covid_api:latest .
```

It will take a while to build but finally it will generate a Docker image that you can run using:

```
docker run -d -p 8080:5000 --name covidREST flask 
```
This will start a Docker container that is running the REST API and that is listing to port 8080. The container name is *covidREST*. Port 8080 on the host is mapped to port 5000 inside the container. Start a browser and go to the following web site http://localhost:8080/api/data/DE,UK,FR,IT,ES/CumulativeCases
You may also want to try some more links such as:
- http://localhost:8080/api/data/DE,UK,FR,IT,ES/Cases?lastN=30&bar=True
- http://localhost:8080/api/data/JP,KR,SG/CumulativeCases?sinceN=100
- http://localhost:8080/api/data/US,RU,BR,PE,MX/CumulativeCases?sinceN=100&log=True

As this REST API is build on the [FastAPI framework](https://fastapi.tiangolo.com), the documentation is generated at <host>:8080/docs. You will find a documentation of certain parameters there as well as the possibility to test the API by submitting requests to it.

To stop the Docker image use:

````
docker stop covidREST 
````
