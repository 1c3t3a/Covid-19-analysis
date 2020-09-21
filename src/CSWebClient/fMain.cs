using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace CSWebClient
{
  public partial class fMain : Form
  {
    public fMain()
    {
      InitializeComponent();
    }

    /// <summary>
    /// our webclient class
    /// </summary>
    private CoronaWebClient _cwc;
    private void fMain_Load(object sender, EventArgs e)
    {
      // create the ToolTip and associate with the Form container.
      ToolTip tt = new ToolTip();
      // set up the delays for the ToolTip.
      tt.AutoPopDelay = 5000;
      tt.InitialDelay = 1000;
      tt.ReshowDelay = 500;
      // force the ToolTip text to be displayed whether or not the form is active.
      tt.ShowAlways = true;
      // set up the ToolTip text for the Button and Checkbox.
      tt.SetToolTip(this.btnAddToFavourites, "Add to favourites");
      tt.SetToolTip(this.btnRemoveFromFavourites, "Remove from favourites");
      tt.SetToolTip(this.btnGetData, "Get the data plot");
      tt.SetToolTip(this.txtCountries, "Provide a comma separated listed of GeoIDs such as 'DE,UK,IT'");
      tt.SetToolTip(this.rbAll, "Get data for all dates");
      tt.SetToolTip(this.rbSince, "Get data for the time since n cumulative cases have been exceeded");
      tt.SetToolTip(this.rbLast, "Get data for the last n days");
      tt.SetToolTip(this.rbLinePlot, "Show a line plot");
      tt.SetToolTip(this.rbBarGraph, "Show a bar graph");
      tt.SetToolTip(this.rbLinear, "Show a linear y-axis");
      tt.SetToolTip(this.rbLog, "Show a logarithmic y-axis");
      tt.SetToolTip(this.chkUseLocalhost, "Use the local server that needs to be started");
      // establish connection
      chkUseLocalhost_CheckedChanged(this, new EventArgs());
      // add the data attrinutes
      foreach (KeyValuePair<string, string> entry in _cwc.Attributes)
      {
        // fill combobox
        cbAvailableAttributes.Items.Add(entry.Key);
      }
      // select the first one
      cbAvailableAttributes.SelectedIndex = 0;

      // get the favourites
      if (Properties.Settings.Default.Favourites != null)
      {
        // load the favourites
        foreach (string strFavourite in Properties.Settings.Default.Favourites)
        {
          // add them to combobox
          cbFavourites.Items.Add(strFavourite);
        }
      }
      // select the first one
      if (cbFavourites.Items.Count > 0)
        cbFavourites.SelectedIndex = 0;
    }

    /// <summary>
    /// Closing the form, but saving the favourites first
    /// </summary>
    /// <param name="sender"></param>
    /// <param name="e"></param>
    private void fMain_FormClosing(object sender, FormClosingEventArgs e)
    {
      // get favourites
      System.Collections.Specialized.StringCollection favourites = new System.Collections.Specialized.StringCollection();
      foreach (string cbItem in cbFavourites.Items)
        favourites.Add(cbItem.ToString());
      // save the favourites
      Properties.Settings.Default.Favourites = favourites;
      Properties.Settings.Default.Save();
    }

    private string _server { get; set; }
    private void chkUseLocalhost_CheckedChanged(object sender, EventArgs e)
    {
      // use the local host or the public host
      if (chkUseLocalhost.Checked == true)
        _server = "localhost";
      else
        _server = Properties.Settings.Default.Server;
      try
      {
        // create the class
        _cwc = new CoronaWebClient(_server, Properties.Settings.Default.Timeout);
        // show status
        tsslStatus.Text = "Connected to: " + _server;
      }
      catch (Exception ex)
      {
        // display hint
        MessageBox.Show("Error connecting to server " + _server +
                        "! Please check your server address in the config file or start your local server.",
                        "Error",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error);
        // disable button
        btnGetData.Enabled = false;
        // and exit
        System.Environment.Exit(-1);
      }
    }

    /// <summary>
    /// Textbox handling the comma separated list of GeoIDs such as "DE, FR, UK"
    /// </summary>
    /// <param name="sender"></param>
    /// <param name="e"></param>
    private void cbFavourites_SelectedIndexChanged(object sender, EventArgs e)
    {
      // select the favourite
      txtCountries.Text = cbFavourites.SelectedItem.ToString();
      /// ToDO: check the string by trying to seperate it in components
    }

    /// <summary>
    /// Adding the text of the textbox to our favourites list
    /// </summary>
    /// <param name="sender"></param>
    /// <param name="e"></param>
    private void btnAddToFavourites_Click(object sender, EventArgs e)
    {
      if (txtCountries.Text == "")
        return;
      // add it to the list
      cbFavourites.Items.Add(txtCountries.Text);
      // select it
      cbFavourites.SelectedIndex = cbFavourites.Items.Count - 1;
    }

    /// <summary>
    /// Removes the currently selected item of the favourites combo
    /// </summary>
    /// <param name="sender"></param>
    /// <param name="e"></param>
    private void btnRemoveFromFavourites_Click(object sender, EventArgs e)
    {
      // remove the current item
      if (cbFavourites.Items.Count > 0)
        cbFavourites.Items.RemoveAt(cbFavourites.SelectedIndex);
      // select item 0
      if (cbFavourites.Items.Count > 0)
        cbFavourites.SelectedIndex = 0;
    }

    /// <summary>
    /// Getting the data chart
    /// </summary>
    /// <param name="sender"></param>
    /// <param name="e"></param>
    private void btnGetData_Click(object sender, EventArgs e)
    {
      try
      {
        string strURL = "";
        // get the chart
        if (rbAll.Checked)
          pbReply.Image = _cwc.GetDataChart(txtCountries.Text, _cwc.Attributes[cbAvailableAttributes.Text], rbLog.Checked, rbBarGraph.Checked, out strURL);
        else if (rbLast.Checked)
          pbReply.Image = _cwc.GetDataChartLast(txtCountries.Text, _cwc.Attributes[cbAvailableAttributes.Text], rbLog.Checked, rbBarGraph.Checked, (int)nudLast.Value, out strURL);
        else if (rbSince.Checked)
          pbReply.Image = _cwc.GetDataChartSince(txtCountries.Text, _cwc.Attributes[cbAvailableAttributes.Text], rbLog.Checked, rbBarGraph.Checked, (int)nudSince.Value, out strURL);
        tsslStatus.Text = "Connected to: " + strURL;
      }
      catch (Exception ex)
      {
        // something went wrong
        MessageBox.Show("Error getting chart! Please check your parameters.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
      }
      // enable/disable the save button
      if (pbReply.Image != null)
        btnSaveImage.Enabled = true;
      else
        btnSaveImage.Enabled = false;
    }

    private void btnShowList_Click(object sender, EventArgs e)
    {
      // create the dialog and show it
      fCountryList dlg = new fCountryList();
      dlg.ShowDialog();
    }

    private void btnSaveImage_Click(object sender, EventArgs e)
    {
      if (saveFileDialog.ShowDialog() == DialogResult.OK)
        pbReply.Image.Save(saveFileDialog.FileName);
    }
  }
}
