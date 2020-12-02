//
//  ViewController.swift
//  Covid19WebClient
//
//  Created by CMBT on 24.11.20.
//

import Cocoa

class ViewController: NSViewController {

  // private let _strServer: String = "localhost"
  private let _strServer: String = "mb.cmbt.de"
  private var _wc: CoronaWebClient!
  private let _defaults = UserDefaults.standard
  
  // outlets for the controls
  @IBOutlet weak var imageView: NSImageView!
  @IBOutlet weak var cbAttributes: NSComboBox!
  @IBOutlet weak var cbFavourites: NSComboBox!
  @IBOutlet weak var txtRequestedGeoIDs: NSTextField!
  @IBOutlet weak var txtStatus: NSTextField!
  @IBOutlet weak var btnRemoveFromFavourites: NSButton!
  @IBOutlet weak var btnAddToFavourites: NSButton!
  @IBOutlet weak var btnGetData: NSButton!
  @IBOutlet weak var txtLastNDays: NSTextField!
  @IBOutlet weak var stpLastNDays: NSStepper!
  @IBOutlet weak var txtSinceNCases: NSTextField!
  @IBOutlet weak var stpSinceNCases: NSStepper!
  @IBOutlet weak var chkLogarithmic: NSButton!
  
  func initDefaults() {
    // init the default server
    _defaults.set("mb.cmbt.de", forKey: "server")
    // intial favourite list
    _defaults.set(["DE, FR, IT, ES, UK, CH",
                   "US, BR, MX, PE, CO, RU, IN",
                   "SE, NO, FI, DK",
                   "AT, HR, SI, ME, BA, XK",
                   "KR, JP, SG, TW, VN, PH, MY, TH"], forKey: "favourites")
    // flag that we have defaults
    _defaults.set(true, forKey: "hasDefaults")
  }
  
  override func viewDidLoad() {
    super.viewDidLoad()

    // open the defaults
    let hasDefaults: Bool = _defaults.bool(forKey: "hasDefaults")
    if hasDefaults != true {
      // init our defaults
      initDefaults()
    }
    // get the favourites
    let favourites: Array = _defaults.array(forKey: "favourites")!
    // remove all items from the combo box
    cbFavourites.removeAllItems()
    // add them to the combobox
    for favourite in favourites {
      cbFavourites.addItem(withObjectValue: favourite)
    }
    // select the first item
    cbFavourites.selectItem(at: 0)
    // if there are no favourites disable the remove button
    if cbFavourites.numberOfItems == 0 {
      btnRemoveFromFavourites.isEnabled = false
    }
    else {
      // add the selected item to the textbox
      txtRequestedGeoIDs.stringValue = cbFavourites.stringValue
    }
    
    // create webclient
    _wc = CoronaWebClient.init(strDomain: _strServer, nTimeout: 50)
    // remove all items from the combo box
    cbAttributes.removeAllItems()
    // fill the combo box with available attributes
    for attribute in _wc.Attributes.keys.sorted() {
      cbAttributes.addItem(withObjectValue: attribute)
    }
    // select the first item
    cbAttributes.selectItem(at: 0)
  }

  override var representedObject: Any? {
    didSet {
    // Update the view, if already loaded.
    }
  }
  
  override func viewWillDisappear() {
    // get the current defaults
    let favs = cbFavourites.objectValues
    // save them
    _defaults.set(favs, forKey: "favourites")
    // call the default
    super.viewWillDisappear()
  }

  override func viewDidDisappear() {
    // cloese the app
    NSApplication.shared.terminate(self)
  }
  
  @IBAction func cbFavouriteChanged(_ sender: Any) {
    // some geoids for testing
    let theFavourite: String = cbFavourites.stringValue
    if theFavourite == "" {
      return
    }
    // show the favourite
    txtRequestedGeoIDs.stringValue = theFavourite
  }
  
  @IBAction func txtRequestedGeoIDsChanged(_ sender: Any) {
    // disable the add button if the string is empty
    if txtRequestedGeoIDs.stringValue == "" {
      btnAddToFavourites.isEnabled = false
      btnGetData.isEnabled = false
    } else {
      btnAddToFavourites.isEnabled = true
      btnGetData.isEnabled = true
    }
  }
  
  @IBAction func btnRemoveFromFavouritesClick(_ sender: Any) {
    // remove the current item from combobox
    cbFavourites.removeItem(at: cbFavourites.indexOfSelectedItem)
    // take care of consitancy
    if cbFavourites.numberOfItems > 0 {
      // select the first item again
      cbFavourites.selectItem(at: 0)
      // add them to the textbox
      txtRequestedGeoIDs.stringValue = cbFavourites.stringValue
    } else {
      // erase the text
      cbFavourites.stringValue = ""
      // disable the button
      btnRemoveFromFavourites.isEnabled = false
    }
  }
  
  @IBAction func btnAddToFavouritesClick(_ sender: Any) {
    // return if there is now text given
    if txtRequestedGeoIDs.stringValue == "" {
      return
    }
    // add a new favourite
    cbFavourites.addItem(withObjectValue: txtRequestedGeoIDs.stringValue)
    // select it
    cbFavourites.selectItem(at: cbFavourites.numberOfItems - 1)
    // enable the remove button
    btnRemoveFromFavourites.isEnabled = true
  }
  
  var _dateOption: Int = 0
  @IBAction func rbDateOptions(_ sender: Any) {
    // get the sender
    if let radioButton = sender as? NSButton {
      // keep the selected option
      _dateOption = radioButton.tag
      // check which one has been clicked
      switch radioButton.tag {
        case 0:
          // all data
          txtLastNDays.isEnabled = false
          txtSinceNCases.isEnabled = false
        case 1:
          // lastNDays data
          txtLastNDays.isEnabled = true
          txtSinceNCases.isEnabled = false
        case 2:
          // sinceNCases data
          txtLastNDays.isEnabled = false
          txtSinceNCases.isEnabled = true
        default:
          txtLastNDays.isEnabled = false
          txtSinceNCases.isEnabled = false
      }
    }
    // enable or disable the steppers
    stpLastNDays.isEnabled = txtLastNDays.isEnabled
    stpSinceNCases.isEnabled = txtSinceNCases.isEnabled
  }
  
  @IBAction func stpLastN(_ sender: Any) {
    // display the value
    txtLastNDays.stringValue = String(stpLastNDays.intValue)
  }
  
  @IBAction func stelSinceN(_ sender: Any) {
    // display the value
    txtSinceNCases.stringValue = String(stpSinceNCases.intValue)
  }
  
  var _plotOption: Int = 0
  @IBAction func rbPlotTypeChanged(_ sender: Any) {
    // get the sender
    if let radioButton = sender as? NSButton {
      // keep the selected option
      _plotOption = radioButton.tag
    }
  }
  
  @IBAction func btnClick(_ sender: Any) {
    // get the requested attribute
    guard let theAttribute: String = _wc.Attributes[cbAttributes.stringValue] else {
      return
    }
    // get the requested GeoIDs
    let theGeoIDs: String = txtRequestedGeoIDs.stringValue
    if theGeoIDs.isEmpty {
      return
    }
    // plot options
    let barGraph: Bool = _plotOption == 1
    let logarithmic: Bool = chkLogarithmic.state == NSControl.StateValue.on
    // now get the data
    var theResult: (image: Result<NSImage, CoronaWebClient.NetworkError>, strURL: String)
    switch _dateOption {
      case 0:
        // get the data
        theResult = _wc.GetDataChart(strCountries: theGeoIDs, strAttribut: theAttribute, bLogarithmic: logarithmic, bBargraph: barGraph)
      case 1:
        // get the data
        theResult = _wc.GetDataChartLast(strCountries: theGeoIDs, strAttribut: theAttribute, bLogarithmic: logarithmic, bBargraph: barGraph, nLast: stpLastNDays.intValue)
      case 2:
        // get the data
        theResult = _wc.GetDataChartSince(strCountries: theGeoIDs, strAttribut: theAttribute, bLogarithmic: logarithmic, bBargraph: barGraph, nSince: stpSinceNCases.intValue)
      default:
        return
    }
   
    // check the return
    switch theResult {
      // success
      case let (Result.success(image), url):
        imageView.image = image
        txtStatus.stringValue = "Connected to " + _strServer + ". Request URL is: " + url
        // enable the menu items to save and copy the plot
        enableMenuItems()
      // server not found at all
      case let (Result.failure(CoronaWebClient.NetworkError.INVALID_URL), url):
        txtStatus.stringValue = "Error connecting to " + _strServer + ". Request URL is: " + url
      // server returned no image
      case let (Result.failure(CoronaWebClient.NetworkError.INVALID_RESPONSE), url):
        txtStatus.stringValue = "Error in server reply. Request URL is: " + url + ". Maybe server doesn't send an image."
      // server doesn't respond
      case let (Result.failure(CoronaWebClient.NetworkError.NO_RESPONSE), url):
        txtStatus.stringValue = "Error server didn't respond. Request URL is: " + url + ". Maybe an illegal GeoID?"
    }
  }
  
  func enableMenuItems () {
    // get the main menu
    if let mainMenu = NSApplication.shared.mainMenu {
      // the file submenu
      if let menuItem = mainMenu.item(withTitle: "File") {
        // get the copy plot menu item
        if let subMenu = menuItem.submenu?.item(withTitle: "Save plot") {
          // bind the action
          subMenu.action = #selector(menuFileSavePlot(_:))
        }
      }// the edit submenu
      if let menuItem = mainMenu.item(withTitle: "Edit") {
        // get the copy plot menu item
        if let subMenu = menuItem.submenu?.item(withTitle: "Copy plot") {
          // bind the action
          subMenu.action = #selector(menuEditCopyPlot(_:))
        }
      }
    }
  }
  
  @IBAction func btnHelpClicked(_ sender: Any) {
    // open the help online
    if let url = URL(string: "http://mb.cmbt.de/covid-19-analysis/the-rest-api/") {
      NSWorkspace.shared.open(url)
    }
  }
  
  @IBAction func btnGeoIDsClicked(_ sender: Any) {
    // open the help online
    if let url = URL(string: "http://mb.cmbt.de/covid-19-analysis/list-of-geoids-and-countries/") {
      NSWorkspace.shared.open(url)
    }}
  

  @IBAction func menuFileSavePlot(_ sender: Any) {
    // check the image first
    guard let img = self.imageView.image else {
      return;
    }
    // create a save panel
    let savePanel = NSSavePanel()
    // define its properties
    savePanel.canCreateDirectories = true
    savePanel.showsTagField = false
    savePanel.title = "Save current plot"
    savePanel.allowedFileTypes = ["png"]
    savePanel.nameFieldStringValue = "plot.png"
    // set the position
    savePanel.level = NSWindow.Level(rawValue: Int(CGWindowLevelForKey(.modalPanelWindow)))
    // show it
    savePanel.begin {
      (result) in if result.rawValue == NSApplication.ModalResponse.OK.rawValue {
        // get the selected url
        guard let url = savePanel.url else {
          return;
        }
        // write the file
        if !img.pngWrite(to: url) {
          // show an error message
          let alert = NSAlert()
          alert.messageText = "Error saving file"
          alert.informativeText = "Couldn't save the plot as a PNG to file: " + url.path
          alert.addButton(withTitle: "Ok")
          alert.runModal()
        }
      }
    }
  }
  
  @IBAction func menuEditCopyPlot(_ sender: Any) {
    // check the image first
    guard let img = self.imageView.image else {
      return;
    }
    // get the pastebook
    let pb = NSPasteboard.general
    // clear it
    pb.clearContents()
    // copy the image
    pb.writeObjects([img])
  }
}

extension NSImage {
    var pngData: Data? {
        guard let tiffRepresentation = tiffRepresentation, let bitmapImage = NSBitmapImageRep(data: tiffRepresentation) else { return nil }
        return bitmapImage.representation(using: .png, properties: [:])
    }
    func pngWrite(to url: URL, options: Data.WritingOptions = .atomic) -> Bool {
        do {
            try pngData?.write(to: url, options: options)
            return true
        } catch {
            print(error)
            return false
        }
    }
}
