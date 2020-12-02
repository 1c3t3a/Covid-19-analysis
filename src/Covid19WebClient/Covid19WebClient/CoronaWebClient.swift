//
//  CoronaWebClient.swift
//  Covid19WebClient
//
//  Created by CMBT on 24.11.20.
//

import Foundation
import AppKit

class CoronaWebClient {

  /// <summary>
  /// Potential erros in accessing the server
  /// </summary>
  enum NetworkError:Error {
    /// <summary>
    /// Something is wrong with the URL, potentially it's because of the App Transport Security Settings (no http connections allowed) or the sandboxing
    /// </summary>
    case INVALID_URL
    /// <summary>
    /// The server is not responding
    /// </summary>
    case NO_RESPONSE
    /// <summary>
    /// The server does not respond data of the expected type (e.g. no image)
    /// </summary>
    case INVALID_RESPONSE
  }
  
  /// <summary>
  /// A flag to define wether to use https or http
  /// </summary>
  private var  _UseHTTPS: Bool = false
  
  /// <summary>_
  /// The server to talk to
  /// </summary>
  private var _server: String = "";
  
  /// <summary>_
  /// The path on the server
  /// </summary>
  private let _urlPath:String = "/api/data/";
  
  /// <summary>
  /// You may want to ping the server before trying to get data
  /// </summary>
  private var _ping: Bool = false
  
  /// <summary>
  /// A Key-Value pair list with chart information and their names on the server
  /// </summary>
  //private(set) var Attributes: [String: String] = [:]
  private(set) var Attributes:Dictionary<String, String> = [:]
  
  /// <summary>
  /// Constructor takeing the server and the timeout
  /// </summary>
  /// <param name="strDomain"> The name of the server either as a IP or name</param>
  /// <param name="nTimeout"> Timeout for the connection in ms</param>
  init (strDomain: String, nTimeout:UInt) {
    // keep the server address
    _server = strDomain
    // check if it is the localhost to add the port
    if (_server == "localhost") {
      _server = _server + ":8000"
    }
    Attributes = ["Daily cases": "DailyCases",
                  "Daily cases, 7 day average": "DailyCases7",
                  "7-day incidence": "Incidence7DayPer100Kpopulation",
                  "Cumulative cases": "Cases",
                  "Cumulative deaths": "Deaths",
                  "Daily Deaths": "DailyDeaths",
                  "Daily Deaths, 7 day average": "DailyDeaths7",
                  "Percent deathly cases": "PercentDeaths",
                  "Doubling time [days]": "DoublingTime",
                  "Cumulative cases per million population": "CasesPerMillionPopulation",
                  "Deaths per million population": "DeathsPerMillionPopulation",
                  "Reproduction rate R": "R7"]
  }
  
  /// <summary>
  /// Gets the data chart as a image from the given URL
  /// </summary>
  /// <param name="strURL"> The URL</param>
  /// <returns> A Result which might be a NSImage or a NetworkError</returns>
  private func GetChartFromURL(strURL: String) -> Result<NSImage, NetworkError> {
    // the url
    guard let url = URL(string: strURL) else {
      // there is a problem with the url
      return Result.failure(NetworkError.INVALID_URL)
    }
    // get the image from the url
    do {
      if let result = try NSImage(data: Data(contentsOf: url)) {
        // great, it worked, return the image
        return Result.success(result)
      }
      // obviously the server did not returned an imahe
      return Result.failure(NetworkError.INVALID_RESPONSE)
    }
    catch {
      // we got no answer at all
      return Result.failure(NetworkError.NO_RESPONSE)
    }
  }
  
  /// <summary>
  /// Get the chart of all data since December 31st.
  /// </summary>
  /// <param name="strCountries"> The country string as a comma separated list of GeoIDs</param>
  /// <param name="strAttribut"> The attribut to get the data graph for</param>
  /// <param name="bLogarithmic"> A flag indicating linear or logarithmic y-axis</param>
  /// <param name="bBargraph"> A flag indicating wether to draw a line plot or bargraph</param>
  /// <returns>A Result which might be a NSImage or a NetworkError plus the url that has been used</returns>
  func GetDataChart(strCountries: String, strAttribut: String, bLogarithmic: Bool, bBargraph: Bool) -> (image: Result<NSImage, NetworkError>, strURL: String)
  {
    // build the url string
    var strURL: String = "http";
    if (_UseHTTPS) {
      strURL = strURL + "s"
    }
    // remove spaces from the GeoID string list
    let strCountriesNoSpaces = strCountries.replacingOccurrences(of: " ", with: "")
    // add these GeoID list to the url
    strURL = strURL + "://" + _server + _urlPath + strCountriesNoSpaces + "/" + strAttribut
    // add both flags
    if (bLogarithmic && bBargraph) {
      strURL = strURL + "?bar=True&log=True"
    }
    // add the log flag
    else if (bLogarithmic) {
      strURL = strURL + "?log=True"
    }
    // add the bargraph flag
    else if (bBargraph) {
      strURL = strURL + "?bar=True"
    }
    // finally get the image and the url that has been used from the server
    return (GetChartFromURL(strURL: strURL), strURL)
  }
  
  /// <summary>
  /// Get the chart since a number of cases has been exceeded
  /// </summary>
  /// <param name="strCountries"> The country string as a comma separated list of GeoIDs</param>
  /// <param name="strAttribut"> The attribut to get the data graph for</param>
  /// <param name="bLogarithmic"> A flag indicating linear or logarithmic y-axis</param>
  /// <param name="bBargraph"> A flag indicating wether to draw a line plot or bargraph</param>
  /// <param name="nSince"> The number of cases to bee increased at x=0</param>
  /// <returns>A Result which might be a NSImage or a NetworkError plus the url that has been used</returns>
  func GetDataChartSince(strCountries: String, strAttribut: String, bLogarithmic: Bool, bBargraph: Bool, nSince: Int32) -> (image: Result<NSImage, NetworkError>, strURL: String)
  {
    // build the url string
    var strURL: String = "http";
    if (_UseHTTPS) {
      strURL = strURL + "s"
    }
    // remove spaces from the GeoID string list
    let strCountriesNoSpaces = strCountries.replacingOccurrences(of: " ", with: "")
    // add these GeoID list to the url
    strURL = strURL + "://" + _server + _urlPath + strCountriesNoSpaces + "/" + strAttribut + "?sinceN=" + String(nSince)
    // add the log flag
    if (bLogarithmic) {
      strURL = strURL + "&log=True"
    }
    // add the bargraph flag
    if (bBargraph) {
      strURL = strURL + "&bar=True"
    }
    // finally get the image and the url that has been used from the server
    return (GetChartFromURL(strURL: strURL), strURL)
  }
  
  /// <summary>
  /// Get the chart for the last number of days
  /// </summary>
  /// <param name="strCountries"> The country string as a comma separated list of GeoIDs</param>
  /// <param name="strAttribut"> The attribut to get the data graph for</param>
  /// <param name="bLogarithmic"> A flag indicating linear or logarithmic y-axis</param>
  /// <param name="bBargraph"> A flag indicating wether to draw a line plot or bargraph</param>
  /// <param name="nLast"> Number of last days</param>
      /// <returns>A Result which might be a NSImage or a NetworkError plus the url that has been used</returns>
  func GetDataChartLast(strCountries: String, strAttribut: String, bLogarithmic: Bool, bBargraph: Bool, nLast: Int32) -> (image: Result<NSImage, NetworkError>, strURL: String)
  {
    // build the url string
    var strURL: String = "http";
    if (_UseHTTPS) {
      strURL = strURL + "s"
    }
    // remove spaces from the GeoID string list
    let strCountriesNoSpaces = strCountries.replacingOccurrences(of: " ", with: "")
    // add these GeoID list to the url
    strURL = strURL + "://" + _server + _urlPath + strCountriesNoSpaces + "/" + strAttribut + "?lastN=" + String(nLast)
    // add the log flag
    if (bLogarithmic) {
      strURL = strURL + "&log=True"
    }
    // add the bargraph flag
    if (bBargraph) {
      strURL = strURL + "&bar=True"
    }
    // finally get the image and the url that has been used from the server
    return (GetChartFromURL(strURL: strURL), strURL)
  }
}

