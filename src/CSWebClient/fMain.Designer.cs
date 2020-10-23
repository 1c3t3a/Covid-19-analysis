namespace CSWebClient
{
  partial class fMain
  {
    /// <summary>
    /// Required designer variable.
    /// </summary>
    private System.ComponentModel.IContainer components = null;

    /// <summary>
    /// Clean up any resources being used.
    /// </summary>
    /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
    protected override void Dispose(bool disposing)
    {
      if (disposing && (components != null))
      {
        components.Dispose();
      }
      base.Dispose(disposing);
    }

    #region Windows Form Designer generated code

    /// <summary>
    /// Required method for Designer support - do not modify
    /// the contents of this method with the code editor.
    /// </summary>
    private void InitializeComponent()
    {
      System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(fMain));
      this.panel2 = new System.Windows.Forms.Panel();
      this.panel5 = new System.Windows.Forms.Panel();
      this.rbLog = new System.Windows.Forms.RadioButton();
      this.rbLinear = new System.Windows.Forms.RadioButton();
      this.panel4 = new System.Windows.Forms.Panel();
      this.rbBarGraph = new System.Windows.Forms.RadioButton();
      this.rbLinePlot = new System.Windows.Forms.RadioButton();
      this.panel3 = new System.Windows.Forms.Panel();
      this.nudLast = new System.Windows.Forms.NumericUpDown();
      this.nudSince = new System.Windows.Forms.NumericUpDown();
      this.rbLast = new System.Windows.Forms.RadioButton();
      this.rbSince = new System.Windows.Forms.RadioButton();
      this.rbAll = new System.Windows.Forms.RadioButton();
      this.label4 = new System.Windows.Forms.Label();
      this.cbAvailableAttributes = new System.Windows.Forms.ComboBox();
      this.btnGetData = new System.Windows.Forms.Button();
      this.statusStrip1 = new System.Windows.Forms.StatusStrip();
      this.tsslStatus = new System.Windows.Forms.ToolStripStatusLabel();
      this.cbFavourites = new System.Windows.Forms.ComboBox();
      this.txtCountries = new System.Windows.Forms.TextBox();
      this.label3 = new System.Windows.Forms.Label();
      this.label2 = new System.Windows.Forms.Label();
      this.btnAddToFavourites = new System.Windows.Forms.Button();
      this.btnRemoveFromFavourites = new System.Windows.Forms.Button();
      this.panel1 = new System.Windows.Forms.Panel();
      this.chkUseLocalhost = new System.Windows.Forms.CheckBox();
      this.btnShowList = new System.Windows.Forms.Button();
      this.btnSaveImage = new System.Windows.Forms.Button();
      this.saveFileDialog = new System.Windows.Forms.SaveFileDialog();
      this.btnGitHub = new System.Windows.Forms.Button();
      this.btnHelpAttributes = new System.Windows.Forms.Button();
      this.pbReply = new System.Windows.Forms.PictureBox();
      this.panel2.SuspendLayout();
      this.panel5.SuspendLayout();
      this.panel4.SuspendLayout();
      this.panel3.SuspendLayout();
      ((System.ComponentModel.ISupportInitialize)(this.nudLast)).BeginInit();
      ((System.ComponentModel.ISupportInitialize)(this.nudSince)).BeginInit();
      this.statusStrip1.SuspendLayout();
      this.panel1.SuspendLayout();
      ((System.ComponentModel.ISupportInitialize)(this.pbReply)).BeginInit();
      this.SuspendLayout();
      // 
      // panel2
      // 
      this.panel2.Controls.Add(this.btnHelpAttributes);
      this.panel2.Controls.Add(this.panel5);
      this.panel2.Controls.Add(this.panel4);
      this.panel2.Controls.Add(this.panel3);
      this.panel2.Controls.Add(this.label4);
      this.panel2.Controls.Add(this.cbAvailableAttributes);
      this.panel2.Location = new System.Drawing.Point(13, 120);
      this.panel2.Name = "panel2";
      this.panel2.Size = new System.Drawing.Size(319, 131);
      this.panel2.TabIndex = 10;
      // 
      // panel5
      // 
      this.panel5.Controls.Add(this.rbLog);
      this.panel5.Controls.Add(this.rbLinear);
      this.panel5.Location = new System.Drawing.Point(168, 89);
      this.panel5.Name = "panel5";
      this.panel5.Size = new System.Drawing.Size(122, 41);
      this.panel5.TabIndex = 7;
      // 
      // rbLog
      // 
      this.rbLog.AutoSize = true;
      this.rbLog.Location = new System.Drawing.Point(13, 23);
      this.rbLog.Name = "rbLog";
      this.rbLog.Size = new System.Drawing.Size(108, 17);
      this.rbLog.TabIndex = 1;
      this.rbLog.Text = "Logarithmic y-axis";
      this.rbLog.UseVisualStyleBackColor = true;
      // 
      // rbLinear
      // 
      this.rbLinear.AutoSize = true;
      this.rbLinear.Checked = true;
      this.rbLinear.Location = new System.Drawing.Point(13, 3);
      this.rbLinear.Name = "rbLinear";
      this.rbLinear.Size = new System.Drawing.Size(83, 17);
      this.rbLinear.TabIndex = 0;
      this.rbLinear.TabStop = true;
      this.rbLinear.Text = "Linear y-axis";
      this.rbLinear.UseVisualStyleBackColor = true;
      // 
      // panel4
      // 
      this.panel4.Controls.Add(this.rbBarGraph);
      this.panel4.Controls.Add(this.rbLinePlot);
      this.panel4.Location = new System.Drawing.Point(168, 43);
      this.panel4.Name = "panel4";
      this.panel4.Size = new System.Drawing.Size(123, 40);
      this.panel4.TabIndex = 6;
      // 
      // rbBarGraph
      // 
      this.rbBarGraph.AutoSize = true;
      this.rbBarGraph.Location = new System.Drawing.Point(13, 23);
      this.rbBarGraph.Name = "rbBarGraph";
      this.rbBarGraph.Size = new System.Drawing.Size(71, 17);
      this.rbBarGraph.TabIndex = 1;
      this.rbBarGraph.Text = "Bar graph";
      this.rbBarGraph.UseVisualStyleBackColor = true;
      // 
      // rbLinePlot
      // 
      this.rbLinePlot.AutoSize = true;
      this.rbLinePlot.Checked = true;
      this.rbLinePlot.Location = new System.Drawing.Point(13, 3);
      this.rbLinePlot.Name = "rbLinePlot";
      this.rbLinePlot.Size = new System.Drawing.Size(65, 17);
      this.rbLinePlot.TabIndex = 0;
      this.rbLinePlot.TabStop = true;
      this.rbLinePlot.Text = "Line plot";
      this.rbLinePlot.UseVisualStyleBackColor = true;
      // 
      // panel3
      // 
      this.panel3.Controls.Add(this.nudLast);
      this.panel3.Controls.Add(this.nudSince);
      this.panel3.Controls.Add(this.rbLast);
      this.panel3.Controls.Add(this.rbSince);
      this.panel3.Controls.Add(this.rbAll);
      this.panel3.Location = new System.Drawing.Point(0, 43);
      this.panel3.Name = "panel3";
      this.panel3.Size = new System.Drawing.Size(162, 78);
      this.panel3.TabIndex = 5;
      // 
      // nudLast
      // 
      this.nudLast.Increment = new decimal(new int[] {
            10,
            0,
            0,
            0});
      this.nudLast.Location = new System.Drawing.Point(107, 49);
      this.nudLast.Maximum = new decimal(new int[] {
            120,
            0,
            0,
            0});
      this.nudLast.Minimum = new decimal(new int[] {
            10,
            0,
            0,
            0});
      this.nudLast.Name = "nudLast";
      this.nudLast.Size = new System.Drawing.Size(47, 20);
      this.nudLast.TabIndex = 4;
      this.nudLast.Value = new decimal(new int[] {
            30,
            0,
            0,
            0});
      // 
      // nudSince
      // 
      this.nudSince.Increment = new decimal(new int[] {
            50,
            0,
            0,
            0});
      this.nudSince.Location = new System.Drawing.Point(107, 26);
      this.nudSince.Maximum = new decimal(new int[] {
            2500,
            0,
            0,
            0});
      this.nudSince.Minimum = new decimal(new int[] {
            50,
            0,
            0,
            0});
      this.nudSince.Name = "nudSince";
      this.nudSince.Size = new System.Drawing.Size(47, 20);
      this.nudSince.TabIndex = 2;
      this.nudSince.Value = new decimal(new int[] {
            100,
            0,
            0,
            0});
      // 
      // rbLast
      // 
      this.rbLast.AutoSize = true;
      this.rbLast.Location = new System.Drawing.Point(6, 49);
      this.rbLast.Name = "rbLast";
      this.rbLast.Size = new System.Drawing.Size(82, 17);
      this.rbLast.TabIndex = 3;
      this.rbLast.Text = "Last n days:";
      this.rbLast.UseVisualStyleBackColor = true;
      // 
      // rbSince
      // 
      this.rbSince.AutoSize = true;
      this.rbSince.Location = new System.Drawing.Point(6, 26);
      this.rbSince.Name = "rbSince";
      this.rbSince.Size = new System.Drawing.Size(95, 17);
      this.rbSince.TabIndex = 1;
      this.rbSince.Text = "Since n cases:";
      this.rbSince.UseVisualStyleBackColor = true;
      // 
      // rbAll
      // 
      this.rbAll.AutoSize = true;
      this.rbAll.Checked = true;
      this.rbAll.Location = new System.Drawing.Point(6, 3);
      this.rbAll.Name = "rbAll";
      this.rbAll.Size = new System.Drawing.Size(61, 17);
      this.rbAll.TabIndex = 0;
      this.rbAll.TabStop = true;
      this.rbAll.Text = "All days";
      this.rbAll.UseVisualStyleBackColor = true;
      // 
      // label4
      // 
      this.label4.AutoSize = true;
      this.label4.Location = new System.Drawing.Point(3, 13);
      this.label4.Name = "label4";
      this.label4.Size = new System.Drawing.Size(77, 13);
      this.label4.TabIndex = 4;
      this.label4.Text = "Available data:";
      // 
      // cbAvailableAttributes
      // 
      this.cbAvailableAttributes.FormattingEnabled = true;
      this.cbAvailableAttributes.Location = new System.Drawing.Point(86, 10);
      this.cbAvailableAttributes.Name = "cbAvailableAttributes";
      this.cbAvailableAttributes.Size = new System.Drawing.Size(199, 21);
      this.cbAvailableAttributes.TabIndex = 0;
      // 
      // btnGetData
      // 
      this.btnGetData.Font = new System.Drawing.Font("Microsoft Sans Serif", 15.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
      this.btnGetData.Location = new System.Drawing.Point(13, 266);
      this.btnGetData.Name = "btnGetData";
      this.btnGetData.Size = new System.Drawing.Size(285, 77);
      this.btnGetData.TabIndex = 0;
      this.btnGetData.Text = "Get data";
      this.btnGetData.UseVisualStyleBackColor = true;
      this.btnGetData.Click += new System.EventHandler(this.btnGetData_Click);
      // 
      // statusStrip1
      // 
      this.statusStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.tsslStatus});
      this.statusStrip1.Location = new System.Drawing.Point(0, 471);
      this.statusStrip1.Name = "statusStrip1";
      this.statusStrip1.Size = new System.Drawing.Size(897, 22);
      this.statusStrip1.TabIndex = 12;
      this.statusStrip1.Text = "statusStrip1";
      // 
      // tsslStatus
      // 
      this.tsslStatus.Name = "tsslStatus";
      this.tsslStatus.Size = new System.Drawing.Size(108, 17);
      this.tsslStatus.Text = "Not connected yet.";
      // 
      // cbFavourites
      // 
      this.cbFavourites.FormattingEnabled = true;
      this.cbFavourites.Location = new System.Drawing.Point(6, 21);
      this.cbFavourites.Name = "cbFavourites";
      this.cbFavourites.Size = new System.Drawing.Size(279, 21);
      this.cbFavourites.TabIndex = 0;
      this.cbFavourites.SelectedIndexChanged += new System.EventHandler(this.cbFavourites_SelectedIndexChanged);
      // 
      // txtCountries
      // 
      this.txtCountries.Location = new System.Drawing.Point(6, 69);
      this.txtCountries.Name = "txtCountries";
      this.txtCountries.Size = new System.Drawing.Size(279, 20);
      this.txtCountries.TabIndex = 1;
      // 
      // label3
      // 
      this.label3.AutoSize = true;
      this.label3.Location = new System.Drawing.Point(3, 5);
      this.label3.Name = "label3";
      this.label3.Size = new System.Drawing.Size(100, 13);
      this.label3.TabIndex = 6;
      this.label3.Text = "Favourite countries:";
      // 
      // label2
      // 
      this.label2.AutoSize = true;
      this.label2.Location = new System.Drawing.Point(3, 53);
      this.label2.Name = "label2";
      this.label2.Size = new System.Drawing.Size(98, 13);
      this.label2.TabIndex = 3;
      this.label2.Text = "Selected countries:";
      // 
      // btnAddToFavourites
      // 
      this.btnAddToFavourites.Location = new System.Drawing.Point(291, 64);
      this.btnAddToFavourites.Name = "btnAddToFavourites";
      this.btnAddToFavourites.Size = new System.Drawing.Size(28, 28);
      this.btnAddToFavourites.TabIndex = 3;
      this.btnAddToFavourites.Text = "+";
      this.btnAddToFavourites.UseVisualStyleBackColor = true;
      this.btnAddToFavourites.Click += new System.EventHandler(this.btnAddToFavourites_Click);
      // 
      // btnRemoveFromFavourites
      // 
      this.btnRemoveFromFavourites.Location = new System.Drawing.Point(291, 16);
      this.btnRemoveFromFavourites.Name = "btnRemoveFromFavourites";
      this.btnRemoveFromFavourites.Size = new System.Drawing.Size(28, 28);
      this.btnRemoveFromFavourites.TabIndex = 2;
      this.btnRemoveFromFavourites.Text = "-";
      this.btnRemoveFromFavourites.UseVisualStyleBackColor = true;
      this.btnRemoveFromFavourites.Click += new System.EventHandler(this.btnRemoveFromFavourites_Click);
      // 
      // panel1
      // 
      this.panel1.Controls.Add(this.btnRemoveFromFavourites);
      this.panel1.Controls.Add(this.btnAddToFavourites);
      this.panel1.Controls.Add(this.label2);
      this.panel1.Controls.Add(this.label3);
      this.panel1.Controls.Add(this.txtCountries);
      this.panel1.Controls.Add(this.cbFavourites);
      this.panel1.Location = new System.Drawing.Point(13, 12);
      this.panel1.Name = "panel1";
      this.panel1.Size = new System.Drawing.Size(319, 102);
      this.panel1.TabIndex = 9;
      // 
      // chkUseLocalhost
      // 
      this.chkUseLocalhost.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
      this.chkUseLocalhost.AutoSize = true;
      this.chkUseLocalhost.Location = new System.Drawing.Point(13, 451);
      this.chkUseLocalhost.Name = "chkUseLocalhost";
      this.chkUseLocalhost.Size = new System.Drawing.Size(90, 17);
      this.chkUseLocalhost.TabIndex = 4;
      this.chkUseLocalhost.Text = "Use localhost";
      this.chkUseLocalhost.UseVisualStyleBackColor = true;
      this.chkUseLocalhost.CheckedChanged += new System.EventHandler(this.chkUseLocalhost_CheckedChanged);
      // 
      // btnShowList
      // 
      this.btnShowList.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
      this.btnShowList.Location = new System.Drawing.Point(158, 423);
      this.btnShowList.Name = "btnShowList";
      this.btnShowList.Size = new System.Drawing.Size(140, 22);
      this.btnShowList.TabIndex = 3;
      this.btnShowList.Text = "Show GeoID list";
      this.btnShowList.UseVisualStyleBackColor = true;
      this.btnShowList.Click += new System.EventHandler(this.btnShowList_Click);
      // 
      // btnSaveImage
      // 
      this.btnSaveImage.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
      this.btnSaveImage.Enabled = false;
      this.btnSaveImage.Location = new System.Drawing.Point(13, 423);
      this.btnSaveImage.Name = "btnSaveImage";
      this.btnSaveImage.Size = new System.Drawing.Size(140, 22);
      this.btnSaveImage.TabIndex = 2;
      this.btnSaveImage.Text = "Save the plot";
      this.btnSaveImage.UseVisualStyleBackColor = true;
      this.btnSaveImage.Click += new System.EventHandler(this.btnSaveImage_Click);
      // 
      // saveFileDialog
      // 
      this.saveFileDialog.DefaultExt = "*.png";
      this.saveFileDialog.Filter = "PNG images|*.png";
      this.saveFileDialog.Title = "Save image";
      // 
      // btnGitHub
      // 
      this.btnGitHub.Image = global::CSWebClient.Properties.Resources.imgGitHub20x20;
      this.btnGitHub.Location = new System.Drawing.Point(304, 315);
      this.btnGitHub.Name = "btnGitHub";
      this.btnGitHub.Size = new System.Drawing.Size(28, 28);
      this.btnGitHub.TabIndex = 1;
      this.btnGitHub.UseVisualStyleBackColor = true;
      this.btnGitHub.Click += new System.EventHandler(this.btnGitHub_Click);
      // 
      // btnHelpAttributes
      // 
      this.btnHelpAttributes.Image = global::CSWebClient.Properties.Resources.imgHelp20x20;
      this.btnHelpAttributes.Location = new System.Drawing.Point(291, 5);
      this.btnHelpAttributes.Name = "btnHelpAttributes";
      this.btnHelpAttributes.Size = new System.Drawing.Size(28, 28);
      this.btnHelpAttributes.TabIndex = 1;
      this.btnHelpAttributes.UseVisualStyleBackColor = true;
      this.btnHelpAttributes.Click += new System.EventHandler(this.btnHelpAttributes_Click);
      // 
      // pbReply
      // 
      this.pbReply.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
      this.pbReply.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
      this.pbReply.Location = new System.Drawing.Point(338, 12);
      this.pbReply.Name = "pbReply";
      this.pbReply.Size = new System.Drawing.Size(547, 457);
      this.pbReply.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
      this.pbReply.TabIndex = 0;
      this.pbReply.TabStop = false;
      // 
      // fMain
      // 
      this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
      this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
      this.ClientSize = new System.Drawing.Size(897, 493);
      this.Controls.Add(this.btnGitHub);
      this.Controls.Add(this.btnSaveImage);
      this.Controls.Add(this.btnShowList);
      this.Controls.Add(this.chkUseLocalhost);
      this.Controls.Add(this.statusStrip1);
      this.Controls.Add(this.btnGetData);
      this.Controls.Add(this.panel2);
      this.Controls.Add(this.panel1);
      this.Controls.Add(this.pbReply);
      this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
      this.MinimumSize = new System.Drawing.Size(767, 387);
      this.Name = "fMain";
      this.Text = "Covid-19 Data Visualisation";
      this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.fMain_FormClosing);
      this.Load += new System.EventHandler(this.fMain_Load);
      this.panel2.ResumeLayout(false);
      this.panel2.PerformLayout();
      this.panel5.ResumeLayout(false);
      this.panel5.PerformLayout();
      this.panel4.ResumeLayout(false);
      this.panel4.PerformLayout();
      this.panel3.ResumeLayout(false);
      this.panel3.PerformLayout();
      ((System.ComponentModel.ISupportInitialize)(this.nudLast)).EndInit();
      ((System.ComponentModel.ISupportInitialize)(this.nudSince)).EndInit();
      this.statusStrip1.ResumeLayout(false);
      this.statusStrip1.PerformLayout();
      this.panel1.ResumeLayout(false);
      this.panel1.PerformLayout();
      ((System.ComponentModel.ISupportInitialize)(this.pbReply)).EndInit();
      this.ResumeLayout(false);
      this.PerformLayout();

    }

        #endregion

        private System.Windows.Forms.PictureBox pbReply;
        private System.Windows.Forms.Panel panel2;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.ComboBox cbAvailableAttributes;
        private System.Windows.Forms.Panel panel3;
        private System.Windows.Forms.NumericUpDown nudLast;
        private System.Windows.Forms.NumericUpDown nudSince;
        private System.Windows.Forms.RadioButton rbLast;
        private System.Windows.Forms.RadioButton rbSince;
        private System.Windows.Forms.RadioButton rbAll;
        private System.Windows.Forms.RadioButton rbBarGraph;
        private System.Windows.Forms.RadioButton rbLinePlot;
        private System.Windows.Forms.Panel panel4;
        private System.Windows.Forms.Button btnGetData;
        private System.Windows.Forms.Panel panel5;
        private System.Windows.Forms.RadioButton rbLog;
        private System.Windows.Forms.RadioButton rbLinear;
        private System.Windows.Forms.StatusStrip statusStrip1;
        private System.Windows.Forms.ToolStripStatusLabel tsslStatus;
        private System.Windows.Forms.ComboBox cbFavourites;
        private System.Windows.Forms.TextBox txtCountries;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Button btnAddToFavourites;
        private System.Windows.Forms.Button btnRemoveFromFavourites;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.CheckBox chkUseLocalhost;
        private System.Windows.Forms.Button btnShowList;
        private System.Windows.Forms.Button btnSaveImage;
        private System.Windows.Forms.SaveFileDialog saveFileDialog;
        private System.Windows.Forms.Button btnHelpAttributes;
        private System.Windows.Forms.Button btnGitHub;
    }
}

