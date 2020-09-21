using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net;
using System.Net.NetworkInformation;
using System.Windows.Forms;


namespace CSWebClient
{
  class CoronaWebClient
  {

    /// <summary>
    /// A flag to define wether to use https or http
    /// </summary>
    public bool _UseHTTPS { get; set; }

    /// <summary>
    /// A Key-Value pair list with chart information and their names on the server
    /// </summary>
    public Dictionary<string, string> Attributes
    {
      get;
      private set;
    }

    
    /// <summary>_
    /// The server to talk to
    /// </summary>
    private string _server;
    /// <summary>
    /// The path on the server
    /// </summary>
    private string _urlPath = "/api/data/";
    /// <summary>
    /// You may want to ping the server before trying to get data
    /// </summary>
    private bool _ping = false;

    /// <summary>
    /// Constructor takeing the server and the timeout
    /// </summary>
    /// <param name="strDomain"> The name of the server either as a IP or name</param>
    /// <param name="nTimeout"> Timeout for the connection in ms</param>
    public CoronaWebClient(string strDomain, uint nTimeout)
    {
      if (_ping)
      {
        // check if the server is online
        PingReply reply = PingServer(strDomain, (int)nTimeout);
        if (reply.Status != IPStatus.Success)
          throw new ArgumentException("Server at " + strDomain + " not available!");
      }
      // keep the domain
      _server = strDomain;
      // check if it is the localhost to add the port
      if (_server == "localhost")
        _server = _server + ":8000";
      // a list of data description and data names
      Attributes = new Dictionary<string, string>();
      // fill the list
      Attributes.Add("Daily cases", "DailyCases");
      Attributes.Add("Daily cases, 7 day average", "DailyCases7");
      Attributes.Add("7-day incidence", "Incidence7DayPer100Kpopulation");
      Attributes.Add("Cumulative cases", "Cases");
      Attributes.Add("Cumulative deaths", "Deaths");
      Attributes.Add("Daily Deaths", "DailyDeaths");
      Attributes.Add("Daily Deaths, 7 day average", "DailyDeaths7");
      Attributes.Add("Percent deathly cases", "PercentDeaths");
      Attributes.Add("Doubling time [days]", "DoublingTime");
      Attributes.Add("Cumulative cases per million population", "CasesPerMillionPopulation");
      Attributes.Add("Cumulative deaths per million population", "DeathsPerMillionPopulation");
      Attributes.Add("Reproduction rate R", "R7");
    }

    /// <summary>
    /// Gets the data chart as a image from the given URL
    /// </summary>
    /// <param name="strURL"> The URL</param>
    /// <returns> A bitmap</returns>
    private System.Drawing.Bitmap GetChartFromURL(string strURL)
    {
      // the result
      System.Drawing.Bitmap result = null;
      // create a web client
      System.Net.WebClient wc = new System.Net.WebClient();
      // download image data 
      Byte[] image = wc.DownloadData(strURL);
      // put it in a stream
      System.IO.MemoryStream stream = new System.IO.MemoryStream(image);
      // create image from stream
      result = new System.Drawing.Bitmap(stream);
      return result;
    }

    /// <summary>
    /// Get the chart of all data since December 31st.
    /// </summary>
    /// <param name="strCountries"> The country string as a comma separated list of GeoIDs</param>
    /// <param name="strAttribut"> The attribut to get the data graph for</param>
    /// <param name="bLogarithmic"> A flag indicating linear or logarithmic y-axis</param>
    /// <param name="bBargraph"> A flag indicating wether to draw a line plot or bargraph</param>
    /// <param name="strURL"> The URL being used</param>
    /// <returns></returns>
    public System.Drawing.Bitmap GetDataChart(string strCountries, string strAttribut, bool bLogarithmic, bool bBargraph, out string strURL)
    {
      // build the URL
      strURL = "http";
      if (_UseHTTPS)
        strURL = strURL + "s";
      strCountries = strCountries.Replace(" ", "");
      strURL = strURL + "://" + _server + _urlPath + strCountries + "/" + strAttribut + "?";
      if (bLogarithmic)
        strURL = strURL + "&log=True";
      if (bBargraph)
        strURL = strURL + "&bar=True";
      // get the bitmap
      return GetChartFromURL(strURL);
    }

    /// <summary>
    /// Get the chart since a number of cases has been exceeded
    /// </summary>
    /// <param name="strCountries"> The country string as a comma separated list of GeoIDs</param>
    /// <param name="strAttribut"> The attribut to get the data graph for</param>
    /// <param name="bLogarithmic"> A flag indicating linear or logarithmic y-axis</param>
    /// <param name="bBargraph"> A flag indicating wether to draw a line plot or bargraph</param>
    /// <param name="nSince"> The number of cases</param>
    /// <param name="strURL"> The URL being used</param>
    /// <returns></returns>
    public System.Drawing.Bitmap GetDataChartSince(string strCountries, string strAttribut, bool bLogarithmic, bool bBargraph, int nSince, out string strURL)
    {
      // build the URL
      strURL = "http";
      if (_UseHTTPS)
        strURL = strURL + "s";
      strCountries = strCountries.Replace(" ", "");
      strURL = strURL + "://" + _server + _urlPath + strCountries + "/" + strAttribut + "?sinceN=" + nSince.ToString();
      if (bLogarithmic)
        strURL = strURL + "&log=True";
      if (bBargraph)
        strURL = strURL + "&bar=True";
      // get the bitmap
      return GetChartFromURL(strURL);
    }

    /// <summary>
    /// Get the chart for the last number of days
    /// </summary>
    /// <param name="strCountries"> The country string as a comma separated list of GeoIDs</param>
    /// <param name="strAttribut"> The attribut to get the data graph for</param>
    /// <param name="bLogarithmic"> A flag indicating linear or logarithmic y-axis</param>
    /// <param name="bBargraph"> A flag indicating wether to draw a line plot or bargraph</param>
    /// <param name="nLast"> Number of last days</param>
    /// <param name="strURL"> The URL being used</param>
    /// <returns></returns>
    public System.Drawing.Bitmap GetDataChartLast(string strCountries, string strAttribut, bool bLogarithmic, bool bBargraph, int nLast, out string strURL)
    {
      // build the URL
      strURL = "http";
      if (_UseHTTPS)
        strURL = strURL + "s";
      strCountries = strCountries.Replace(" ", "");
      strURL = strURL + "://" + _server + _urlPath + strCountries + "/" + strAttribut + "?lastN=" + nLast.ToString();
      if (bLogarithmic)
        strURL = strURL + "&log=True";
      if (bBargraph)
        strURL = strURL + "&bar=True";
      // get the bitmap
      return GetChartFromURL(strURL);
    }

    /// <summary>
    /// Pings the given server
    /// </summary>
    /// <param name="strDomain"> The name of the server either as a IP or name</param>
    /// <param name="nTimeout"> Timeout for the connection in ms</param>
    /// <returns> The server reply</returns>
    private PingReply PingServer(string strDomain, int nTimeout)
    {
      Ping pingSender = new Ping();
      PingOptions options = new PingOptions();

      // use the default Ttl value which is 128, but change the fragmentation behavior
      options.DontFragment = true;
      // create a buffer of 32 bytes of data to be transmitted.
      string data = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
      byte[] buffer = Encoding.ASCII.GetBytes(data);
      // ping
      PingReply reply = pingSender.Send(strDomain, nTimeout, buffer, options);
      if (reply.Status == IPStatus.Success)
      {
        Console.WriteLine("Address: {0}", reply.Address.ToString());
        Console.WriteLine("RoundTrip time: {0}", reply.RoundtripTime);
        //Console.WriteLine("Time to live: {0}", reply.Options.Ttl);
        //Console.WriteLine("Don't fragment: {0}", reply.Options.DontFragment);
        //Console.WriteLine("Buffer size: {0}", reply.Buffer.Length);
      }
      return reply;
    }
  }
}
