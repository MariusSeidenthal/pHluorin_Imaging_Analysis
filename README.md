# pHluorin_Imaging_Analysis
Normalization and averaging of pHluorin fluorescence in C. elegans using a defined stimulation period.

1. Quantify dorsal nerve cord and background fluorescence using the segmented line tool in ImageJ. Measurements should be set to "Mean grey value". Results should be copied to the second column of Excel sheets. Each animal/replica should be put on a new sheet. Sheets should look as following:
![](https://i.imgur.com/rPzwv7U.jpeg)

Rows F + G may be left blank or for example used to directly calculate background correction and normalization.

2. Save excel sheets in separate folders.

Careful: This script requires a specific structure of folders:

>	    main folder -> subfolder for condition 1 -> excel files of condition 1
>	
>                   -> subfolder for condition 2 -> excel files of condition 2
>				        	
>                   ...
>					        
>                   -> subfolder for condition n -> excel files of condition n 
>					

3. Run pHluorin_Imaging_Analysis:

Select Main folder to analyze.

Enter the pulse start (number of frames until start of stimulation): up to this point the values will be normalized

Enter the pulse length (length of stimulation in frames): important for signal calculation and normalization to maximum during pulse

Enter the framerate in frames per second (fps)

Check bleach correction if linear bleach correction should be performed (should be tested)

Check Filter, if you want to filter animals according to whether they show a strong signal during stimulation:
>For this, the maximum background corrected fluorescence during stimulation was calculated (moving average of 1 s). If this was higher than the average background corrected fluorescence before the stimulation + 3 * standard deviation (of background corrected fluorescence before stimulation), the animal was counted as a strong responder. 

Filtered animals are discarded.

Run the program.

4. Output:
You will get two excel files per subfolder/condition. One shows the background corrected fluorescence normalized to the average before stimulation of each measurement (∆F/F0). The second will display the background corrected fluorescence normalized to the average before stimulation and additionally normalized to the maximum value during stimulation (minimum-maximum normalization).
Mean, SEM and number of measured worms are also calculated and displayed.
