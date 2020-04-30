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
      try
      {
        // create the class
        _cwc = new CoronaWebClient(Properties.Settings.Default.Server, Properties.Settings.Default.Timeout);
        // show status
        tsslStatus.Text = "Connected to: " + Properties.Settings.Default.Server;
      }
      catch (Exception ex)
      {
        // display hint
        MessageBox.Show("Error connecting to server " + Properties.Settings.Default.Server + 
                        "! Please check your server address in the config file.", 
                        "Error", 
                        MessageBoxButtons.OK, 
                        MessageBoxIcon.Error);
        // disable button
        btnGetData.Enabled = false;
        // and exit
        System.Environment.Exit(-1);
      }
      // add the country list to the listbox
      foreach (KeyValuePair<string, string> entry in _cwc.Countries)
      {
        // fill combobox
        cbAvailableCountries.Items.Add(entry.Value + ": " + entry.Key);
      }
      // select the first one
      cbAvailableCountries.SelectedIndex = 0;

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
        // get the chart
        if (rbAll.Checked)
          pbReply.Image = _cwc.GetDataChart(txtCountries.Text, _cwc.Attributes[cbAvailableAttributes.Text], rbLog.Checked, rbBarGraph.Checked);
        else if (rbLast.Checked)
          pbReply.Image = _cwc.GetDataChartLast(txtCountries.Text, _cwc.Attributes[cbAvailableAttributes.Text], rbLog.Checked, rbBarGraph.Checked, (int)nudLast.Value);
        else if (rbSince.Checked)
          pbReply.Image = _cwc.GetDataChartSince(txtCountries.Text, _cwc.Attributes[cbAvailableAttributes.Text], rbLog.Checked, rbBarGraph.Checked, (int)nudSince.Value);
      }
      catch (Exception ex)
      {
        // something went wrong
        MessageBox.Show("Error getting chart! Please check your parameters.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
      }
    }
  }
}
