# Covid-19-analysis
![](https://github.com/1c3t3a/Covid-19-analysis/workflows/Run%20jupyter%20notebook/badge.svg)<br>
Gets the WHO data about COVID-19 from the [European Center of Disease Control](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide) and visualize them.<br>
Additionally it will calculate some important numbers such as the doubling time and the reproduction number R0. To do so it offers a set of Python classes and functions including a Jupyter notebook to generate PDF reports. The functions are also available through a REST API and the repository offers a C# application in source code to call the REST API.<br><br>
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
