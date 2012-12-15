Induced Radiation Damage Procedure
==================================

Please cite:
------------

J. Synchrotron Rad. (2011). 18, 381-386

Experimental procedure for the characterization of radiation damage in macromolecular crystals

Ricardo M. F. Leal, Gleb P. Bourenkov, Olof Svensson, Darren Spruce, Matias Guijarro, and Alexander N. Popov

Abstract
--------

A reliable and reproducible method to automatically characterize the radiation sensitivity of macromolecular crystals at the ESRF beamlines has been developed. This new approach uses the slope of the linear dependence of the overall isotropic B-factor with absorbed dose as the damage metric. The method has been implemented through an automated procedure using the EDNA on-line data analysis framework and the MxCuBE data collection control interface. The outcome of the procedure can be directly used to design an optimal data collection strategy. The results of tests carried out on a number of model and real-life crystal systems are presented.

----------

J. Synchrotron Rad. (2013). 20

A survey of global radiation damage to 15 different protein crystal types at room temperature: a new decay model

R. M. Ferraz Leal, G. Burenkov, S. Russi and A. N. Popov

Abstract
--------

The radiation damage rates to crystals of 15 model macromolecular structures were studied using an automated radiation sensitivity characterization procedure. The diffracted intensity variation with dose is described by a two-parameter model. This model includes a strong resolution-independent decay specific to room-temperature measurements along with a linear increase in overall Debye-Waller factors. An equivalent representation of sensitivity via a single parameter, normalized half-dose, is introduced. This parameter varies by an order of magnitude between the different structures studied. The data show a correlation of crystal radiation sensitivity with crystal solvent content but no dose-rate dependency was detected in the range 0.05-300 kGy s-1. The results of the crystal characterization are suitable for either optimal planning of room-temperature data collection or in situ crystallization plate screening experiments.

----------

FOR ESRF USERS ONLY
===================
Below are a few guidelines to show how to deal with data off-line.<br>
    The procedure is now very complex and with a lot of features to use
    off-line. Let me know if you have questions.<br>
    <h1>1. Reprocessing all data from 0</h1>
    <br>
    If a file 'history.log'&nbsp; does exist in the root folder (e.g.
    /data/visitor/mx1289/id14eh4/20120607/PROCESSED_DATA). The procedure
    was not even called by MxCube. In that case, all data has to be
    reprocessed in OAR (xds and best bfactor calculation). For this use
    the script:<br>
    <b>/opt/pxsoft/InducedRadDam/vdefault/linux/reprocess.py <br>
    </b><br>
    It should take approximately 2 to 3 minutes to run this.<br>
    <h2>Help:</h2>
    <tt><b>[mx231 5] ~ &gt;
        /opt/pxsoft/InducedRadDam/vdefault/linux/reprocess.py -h</b><br>
      reprocess.py: <br>
      This file will simulate the autoindexserver<br>
      <br>
      run as : /opt/pxsoft/InducedRadDam/vdefault/linux/reprocess.pyy -e
      EDApplication_20101126-094937 -p 'xds_t1w?_run1_1' -s 1 -f 21<br>
      in : process folder<br>
      <br>
      -e &lt;edna folder&gt;<br>
      -p &lt;xds template&gt;, e.g.: 'xds_t1w<b>?</b>_run1_1' (Note que
      question mark and the quotes!)<br>
      -s &lt;start from&gt;, default 1<br>
      -f &lt;last one&gt;, default 21<br>
      -t &lt;step&gt;, default 2 (to omit the even burnt wedges)<br>
    </tt><br>
    <h2>Usage:</h2>
    <p>For the data Sean collected yesterday (21 wedges, starting from 1
      and skipping the even wedges - burnt), this is how to proceed:</p>
    <tt>[mx231 5] ~ &gt; cd
      /data/visitor/mx1289/id14eh4/20120607/PROCESSED_DATA<br>
      [mx231 16] PROCESSED_DATA &gt;
      /opt/pxsoft/InducedRadDam/vdefault/linux/reprocess.py -e
      EDApplication_20120607-143651 -p 'xds_mx1289w?_run1_1' -s 1 -f 21
      <br>
    </tt><br>
    You can use <tt><b>ls -lrt</b></tt> to see which edna folder
    corresponds to the wedge sequence. For the data above, for example,
    the folder for the first&nbsp; collected wedge(w1) appears just after the
    EDNA folder name:<br>
    <tt><br>
      (...)<br>
      drwxr-xr-x 3 opid14 jsbg&nbsp;&nbsp; 4096 Jun&nbsp; 7 14:37 <b>EDApplication_20120607-143651</b>/<br>
      -rw-r--r-- 1 opid14 jsbg&nbsp; 24801 Jun&nbsp; 7 14:37
      EDApplication_20120607-143651.log<br>
      -rw-r--r-- 1 opid14 jsbg 397147 Jun&nbsp; 7 14:37 EDNAOutput_994237.xml<br>
      drwxrwxrwx 2 opid14 jsbg&nbsp;&nbsp; 4096 Jun&nbsp; 7 14:38 HKL2000_mx1289<b>w1</b>_run1_1/<br>
      drwxrwxrwx 2 opid14 jsbg&nbsp;&nbsp; 4096 Jun&nbsp; 7 14:38 mosflm_mx1289<b>w1</b>_run1_1/<br>
      (...)</tt> <br>
    <br>
    <h1>2. Showing the plots for data already processed</h1>
    <p><br>
      Sometimes&nbsp; in the beamlines the process runs but the plots are not
      displayed (Xterm problem....). If it run successfully, there is a
      history file in the process folder:<br>
    </p>
    <tt>[mx231 5] ~ &gt; cd
      /data/visitor/mx1289/id14eh4/20120607/PROCESSED_DATA<br>
      [mx231 18] PROCESSED_DATA &gt; cat history.log <br>
      <b>2012-06-08 10:49 -&gt;
        /bliss/users/leal/Python/InducedRadDam/src/InducedRadDam.py -i
        -e EDApplication_20120607-143651 -p
        /mntdirect/_data_visitor/mx1289/id14eh4/20120607/PROCESSED_DATA/xds_mx1289w1_run1_1
        -l 21<br>
      </b></tt><br>
    This history shows the command line used to call the procedure.<br>
    Note that the procedure is called as many times as the total of
    wedges collected (default 11 wedges, from 1 to 21 skipping even
    wedges: 1,3,5...19,21). <br>
    <br>
    To display the plots copy the last entry in the history.log and add
    the parameter -s&nbsp; to see the plots.<br>
    A few examples:<br>
    <br>
    Show a plot for all collected wedges (from 1 to 21 skipping the
    burnt wedges: even numbers). The two commands are equivalent:<br>
    <tt><b>InducedRadDam.py -i -e EDApplication_20120607-143651 -p
        xds_mx1289w21_run1_1 -s<br>
      </b></tt><tt><b>InducedRadDam.py -i -e
        EDApplication_20120607-143651 -p xds_mx1289w1_run1_1 -f 1 -l 21
        -s<br>
      </b></tt><br>
    Show a plot from wedge 1 to wedge 19. The two commands are
    equivalent::<br>
    <tt><b>InducedRadDam.py -i -e EDApplication_20120607-143651 -p
        xds_mx1289w19_run1_1 -s</b></tt><br>
    <tt><b>InducedRadDam.py -i -e EDApplication_20120607-143651 -p
        xds_mx1289w1_run1_1 -f 1 -l 19 -s<br>
      </b></tt><br>
    Show a plot from wedge 1 to wedge 21 skipping wedge 15,17:<br>
    <tt><b>InducedRadDam.py -i -e EDApplication_20120607-143651 -p
        xds_mx1289w1_run1_1 -f 1 -l 21 -u "15,17" -s<br>
        <br>
      </b></tt>Show a plot for all collected wedges cutting the
    resolution to 3 for the theoretical intensity decay curve:<tt><b><br>
      </b></tt><tt><b>InducedRadDam.py -i -e
        EDApplication_20120607-143651 -p xds_mx1289w1_run1_1 -f 1 -l 21
        -t 3 -s<br>
      </b></tt><br>
    <h2>All this information is available in the help file:</h2>
    <br>
    <tt><b>[mx231 1] ~ &gt; InducedRadDam.py -h<br>
      </b>InducedRadDam.py: <br>
      <br>
      Main routine for Induced Radiation Damage procedure<br>
      <br>
      Mandatory fields:<br>
      <br>
      -e --edna &lt;edna folder name &gt;<br>
      &nbsp;&nbsp; For the workflow: complete path for the XML StrategyResult file
      can be used.<br>
      -p --path &lt;xds path&gt; for the current wedge (the one just
      collected).<br>
      &nbsp;&nbsp;&nbsp; xds_path is of the form:
[/path/path/]xds_&lt;wedge_name&gt;w&lt;wedge_number&gt;_run&lt;run_number&gt;_&lt;dataset_number&gt;<br>
      <br>
      Optional fields:<br>
      <br>
      -h --help : show help message<br>
      -i --ignore: this will ignore even wedges (e.g. crystal1w2_run1_1)
      and will process only odd wedges (1,3,5,...,21). Use this when
      burning wedges are even.<br>
      -c --current &lt;integer&gt; : current wedge entry in the queue
      (if absent comes from: xds_crystal1w&lt;current&gt;_run1_1)<br>
      -f --first &lt;integer&gt;: first element in the queue (default 1)<br>
      -l --last &lt;integer&gt;: of n elements in the queue (default 21)<br>
      -s --see : see results of the burning strategy (no jobs are sent
      to condor/oar). Current wedge is used as last wedge (either from
      the -p &lt;xds path&gt; or -c parameter). This bit of code is
      called by default when current wedge == last wedge.<br>
      -u --unset &lt;list of ints&gt;: When showing the results (i.e.
      processing the last wedge from the queue: current == last), the
      user may ignore some "dodgy" wedges: e.g. "1,5,7"<br>
      -r --raddose &lt;string&gt;: raddose keywords file (file with
      entries of the form &lt;keyword&gt; = &lt;value&gt;, where keyword
      is defined in raddose manual, e.g.: FLUX = 10e12). By default the
      software looks for the file raddose.ini in the path. If the file
      exists, the keywords present in the file will replace the raddose
      script generated by EDNA. The new raddose file will be created as
      &lt;wedge_name&gt;_raddose.sh.<br>
      -d --draw : only draws the plot to an image file, doesn't open an
      X window (default is open the X window)<br>
      -n --config &lt;config ini file&gt; : default value config.ini<br>
      -t --resolution : resolution for calculate intensity decay.
      Default is the value used in strategy<br>
      <br>
      Output files:<br>
      &lt;wedge_name&gt;.png - plot<br>
      &lt;wedge_name&gt;.csv - csv file with all the important details<br>
      &lt;wedge_name&gt;_real.png - plot for real dose rate if
      raddose.ini exists<br>
      /tmp/InducedRadDam.log - log file<br>
      <br>
      Note: the calculations and graphs are only executed when: current
      &lt;integer&gt; == last &lt;integer&gt;<br>
    </tt><br>
    <br>
