# TREETS
> treets stands for Time Restricted Eating ExperimenTS.


## Install

`pip install time_restricted_eating_experiments`

## Example for data analysis on the Columbia study

```python
import treets.columbia as treetsc
import pandas as pd
```

### Take a brief look on the food logging dataset and the reference information sheet

```python
treetsc.read_logging_data('data/col_test_data').head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Unnamed: 0</th>
      <th>original_logtime</th>
      <th>desc_text</th>
      <th>food_type</th>
      <th>PID</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>2021-05-12 02:30:00 +0000</td>
      <td>milk</td>
      <td>b</td>
      <td>yrt1999</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>2021-05-12 02:45:00 +0000</td>
      <td>some medication</td>
      <td>m</td>
      <td>yrt1999</td>
    </tr>
  </tbody>
</table>
</div>



```python
pd.read_excel('data/col_test_data/toy_data_17May2021.xlsx').head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mCC_ID</th>
      <th>Participant_Study_ID</th>
      <th>Study Phase</th>
      <th>Intervention group (TRE or HABIT)</th>
      <th>Start_Day</th>
      <th>End_day</th>
      <th>Eating_Window_Start</th>
      <th>Eating_Window_End</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>yrt1999</td>
      <td>2</td>
      <td>S-REM</td>
      <td>TRE</td>
      <td>2021-05-12</td>
      <td>2021-05-14</td>
      <td>00:00:00</td>
      <td>23:59:00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>yrt1999</td>
      <td>2</td>
      <td>T3-INT</td>
      <td>TRE</td>
      <td>2021-05-15</td>
      <td>2021-05-18</td>
      <td>08:00:00</td>
      <td>18:00:00</td>
    </tr>
  </tbody>
</table>
</div>



### make the table that contains extra analytic information that we want

```python
df = treetsc.make_table(treetsc.read_logging_data('data/col_test_data')\
                      , pd.read_excel('data/col_test_data/toy_data_17May2021.xlsx'))
```

    Participant yrt1999 didn't log any food items in the following day(s):
    2021-05-18
    Participant yrt2000 didn't log any food items in the following day(s):
    2021-05-12
    2021-05-13
    2021-05-14
    2021-05-15
    2021-05-16
    2021-05-17
    2021-05-18
    Participant yrt1999 have bad logging day(s) in the following day(s):
    2021-05-12
    2021-05-15
    Participant yrt1999 have bad window day(s) in the following day(s):
    2021-05-15
    2021-05-17
    Participant yrt1999 have non adherent day(s) in the following day(s):
    2021-05-12
    2021-05-15
    2021-05-17


```python
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mCC_ID</th>
      <th>Participant_Study_ID</th>
      <th>Study Phase</th>
      <th>Intervention group (TRE or HABIT)</th>
      <th>Start_Day</th>
      <th>End_day</th>
      <th>Eating_Window_Start</th>
      <th>Eating_Window_End</th>
      <th>phase_duration</th>
      <th>caloric_entries</th>
      <th>...</th>
      <th>logging_day_counts</th>
      <th>%_logging_day_counts</th>
      <th>good_logging_days</th>
      <th>%_good_logging_days</th>
      <th>good_window_days</th>
      <th>%_good_window_days</th>
      <th>outside_window_days</th>
      <th>%_outside_window_days</th>
      <th>adherent_days</th>
      <th>%_adherent_days</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>yrt1999</td>
      <td>2</td>
      <td>S-REM</td>
      <td>TRE</td>
      <td>2021-05-12</td>
      <td>2021-05-14</td>
      <td>00:00:00</td>
      <td>23:59:00</td>
      <td>3 days</td>
      <td>7.0</td>
      <td>...</td>
      <td>3.0</td>
      <td>1.00</td>
      <td>2.0</td>
      <td>0.666667</td>
      <td>3.0</td>
      <td>1.00</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>2.0</td>
      <td>0.666667</td>
    </tr>
    <tr>
      <th>1</th>
      <td>yrt1999</td>
      <td>2</td>
      <td>T3-INT</td>
      <td>TRE</td>
      <td>2021-05-15</td>
      <td>2021-05-18</td>
      <td>08:00:00</td>
      <td>18:00:00</td>
      <td>4 days</td>
      <td>8.0</td>
      <td>...</td>
      <td>3.0</td>
      <td>0.75</td>
      <td>2.0</td>
      <td>0.500000</td>
      <td>1.0</td>
      <td>0.25</td>
      <td>2.0</td>
      <td>0.5</td>
      <td>1.0</td>
      <td>0.250000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>yrt2000</td>
      <td>3</td>
      <td>T3-INT</td>
      <td>TRE</td>
      <td>2021-05-12</td>
      <td>2021-05-14</td>
      <td>08:00:00</td>
      <td>16:00:00</td>
      <td>3 days</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>3</th>
      <td>yrt2000</td>
      <td>3</td>
      <td>T3-INT</td>
      <td>TRE</td>
      <td>2021-05-15</td>
      <td>2021-05-18</td>
      <td>08:00:00</td>
      <td>16:00:00</td>
      <td>4 days</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.00</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>4</th>
      <td>yrt2001</td>
      <td>4</td>
      <td>T12-A</td>
      <td>TRE</td>
      <td>NaT</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaT</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 26 columns</p>
</div>



```python
df.iloc[0]
```




    mCC_ID                                           yrt1999
    Participant_Study_ID                                   2
    Study Phase                                        S-REM
    Intervention group (TRE or HABIT)                    TRE
    Start_Day                            2021-05-12 00:00:00
    End_day                              2021-05-14 00:00:00
    Eating_Window_Start                             00:00:00
    Eating_Window_End                               23:59:00
    phase_duration                           3 days 00:00:00
    caloric_entries                                      7.0
    mean_daily_eating_window                           13.75
    std_daily_eating_window                        11.986972
    earliest_entry                                       4.5
    2.5%                                              4.5375
    97.5%                                            27.5625
    duration mid 95%                                  23.025
    logging_day_counts                                   3.0
    %_logging_day_counts                                 1.0
    good_logging_days                                    2.0
    %_good_logging_days                             0.666667
    good_window_days                                     3.0
    %_good_window_days                                   1.0
    outside_window_days                                  0.0
    %_outside_window_days                                0.0
    adherent_days                                        2.0
    %_adherent_days                                 0.666667
    Name: 0, dtype: object



```python
df.iloc[1]
```




    mCC_ID                                           yrt1999
    Participant_Study_ID                                   2
    Study Phase                                       T3-INT
    Intervention group (TRE or HABIT)                    TRE
    Start_Day                            2021-05-15 00:00:00
    End_day                              2021-05-18 00:00:00
    Eating_Window_Start                             08:00:00
    Eating_Window_End                               18:00:00
    phase_duration                           4 days 00:00:00
    caloric_entries                                      8.0
    mean_daily_eating_window                        8.666667
    std_daily_eating_window                         8.504901
    earliest_entry                                       7.5
    2.5%                                                 7.7
    97.5%                                               23.9
    duration mid 95%                                    16.2
    logging_day_counts                                   3.0
    %_logging_day_counts                                0.75
    good_logging_days                                    2.0
    %_good_logging_days                                  0.5
    good_window_days                                     1.0
    %_good_window_days                                  0.25
    outside_window_days                                  2.0
    %_outside_window_days                                0.5
    adherent_days                                        1.0
    %_adherent_days                                     0.25
    Name: 1, dtype: object



## Example for data analysis using time restricted eating experiments core module

```python
import treets.core as treets
import pandas as pd
```

### take a look at the original dataset

```python
df = treets.file_loader('data/test_food_details.csv')
df.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Unnamed: 0</th>
      <th>ID</th>
      <th>unique_code</th>
      <th>research_info_id</th>
      <th>desc_text</th>
      <th>food_type</th>
      <th>original_logtime</th>
      <th>foodimage_file_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1340147</td>
      <td>7572733</td>
      <td>alqt14018795225</td>
      <td>150</td>
      <td>Water</td>
      <td>w</td>
      <td>2017-12-08 17:30:00+00:00</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1340148</td>
      <td>411111</td>
      <td>alqt14018795225</td>
      <td>150</td>
      <td>Coffee White</td>
      <td>b</td>
      <td>2017-12-09 00:01:00+00:00</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



### preprocess the data to have extra basic features

```python
df = treets.load_public_data(df,4)
df.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Unnamed: 0</th>
      <th>ID</th>
      <th>unique_code</th>
      <th>research_info_id</th>
      <th>desc_text</th>
      <th>food_type</th>
      <th>original_logtime</th>
      <th>original_logtime_notz</th>
      <th>date</th>
      <th>local_time</th>
      <th>time</th>
      <th>week_from_start</th>
      <th>year</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1340147</td>
      <td>7572733</td>
      <td>alqt14018795225</td>
      <td>150</td>
      <td>Water</td>
      <td>w</td>
      <td>2017-12-08 17:30:00+00:00</td>
      <td>2017-12-08 17:30:00+00:00</td>
      <td>2017-12-08</td>
      <td>17.500000</td>
      <td>17:30:00</td>
      <td>1</td>
      <td>2017</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1340148</td>
      <td>411111</td>
      <td>alqt14018795225</td>
      <td>150</td>
      <td>Coffee White</td>
      <td>b</td>
      <td>2017-12-09 00:01:00+00:00</td>
      <td>2017-12-09 00:01:00+00:00</td>
      <td>2017-12-08</td>
      <td>24.016667</td>
      <td>00:01:00</td>
      <td>1</td>
      <td>2017</td>
    </tr>
  </tbody>
</table>
</div>



### do a brief annalysis

```python
df = treets.summarize_data(df, 'unique_code', 'local_time', 'date')
df.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>unique_code</th>
      <th>num_days</th>
      <th>num_total_items</th>
      <th>num_f_n_b</th>
      <th>num_medications</th>
      <th>num_water</th>
      <th>first_cal_avg</th>
      <th>first_cal_std</th>
      <th>last_cal_avg</th>
      <th>last_cal_std</th>
      <th>eating_win_avg</th>
      <th>eating_win_std</th>
      <th>good_logging_count</th>
      <th>first_cal variation (90%-10%)</th>
      <th>last_cal variation (90%-10%)</th>
      <th>2.5%</th>
      <th>95%</th>
      <th>duration mid 95%</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>alqt1148284857</td>
      <td>13</td>
      <td>149</td>
      <td>96</td>
      <td>19</td>
      <td>34</td>
      <td>7.821795</td>
      <td>6.710717</td>
      <td>23.485897</td>
      <td>4.869082</td>
      <td>15.664103</td>
      <td>-1.841635</td>
      <td>146</td>
      <td>2.966667</td>
      <td>9.666667</td>
      <td>4.535000</td>
      <td>26.813333</td>
      <td>22.636667</td>
    </tr>
    <tr>
      <th>1</th>
      <td>alqt14018795225</td>
      <td>64</td>
      <td>488</td>
      <td>484</td>
      <td>3</td>
      <td>1</td>
      <td>7.525781</td>
      <td>5.434563</td>
      <td>25.858594</td>
      <td>3.374839</td>
      <td>18.332813</td>
      <td>-2.059723</td>
      <td>484</td>
      <td>13.450000</td>
      <td>3.100000</td>
      <td>4.183333</td>
      <td>27.438333</td>
      <td>23.416667</td>
    </tr>
  </tbody>
</table>
</div>



```python
df.iloc[0]
```




    unique_code                      alqt1148284857
    num_days                                     13
    num_total_items                             149
    num_f_n_b                                    96
    num_medications                              19
    num_water                                    34
    first_cal_avg                          7.821795
    first_cal_std                          6.710717
    last_cal_avg                          23.485897
    last_cal_std                           4.869082
    eating_win_avg                        15.664103
    eating_win_std                        -1.841635
    good_logging_count                          146
    first_cal variation (90%-10%)          2.966667
    last_cal variation (90%-10%)           9.666667
    2.5%                                      4.535
    95%                                   26.813333
    duration mid 95%                      22.636667
    Name: 0, dtype: object



```python
df.iloc[1]
```




    unique_code                      alqt14018795225
    num_days                                      64
    num_total_items                              488
    num_f_n_b                                    484
    num_medications                                3
    num_water                                      1
    first_cal_avg                           7.525781
    first_cal_std                           5.434563
    last_cal_avg                           25.858594
    last_cal_std                            3.374839
    eating_win_avg                         18.332813
    eating_win_std                         -2.059723
    good_logging_count                           484
    first_cal variation (90%-10%)              13.45
    last_cal variation (90%-10%)                 3.1
    2.5%                                    4.183333
    95%                                    27.438333
    duration mid 95%                       23.416667
    Name: 1, dtype: object


