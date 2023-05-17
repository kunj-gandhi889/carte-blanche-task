import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from datetime import datetime,timedelta
from st_aggrid import AgGrid

def convertStr2Time(s):
    dd, mm, yyyy = s.split('-')
    yyyy, time = yyyy.split(' ')
    hr, mn = time.split(':')
    return datetime(int(yyyy), int(mm), int(dd), hour=int(hr), minute=int(mn))

def efficiency(df,device_no):
    fig,ax = plt.subplots()
    ax.plot(df.time, df.On_time, label='on_time')
    ax.plot(df.time, df.Off_time, label='off_time')
    plt.xlabel('Time')
    plt.ylabel('No. of Minutes Device was on/off')
    plt.title('Efficiency of Device {} : {:.2f} %'.format(device_no,df.On_time.max()/len(df)*100))
    plt.legend()
    # plt.show()
    st.pyplot(fig)

# ontime offtime visualization
def visualizeOnOff(df,label,plot=True,returnData=False):

    data = df[['time', 'On_time', 'Off_time']]
    data = data.to_numpy()

    output = [0 for _ in range(len(data))]

    prev = 0
    for idx, value in enumerate(data):
        if idx == 0:
            prev = value[1]
            if(prev == 1):
                output[idx] = 1
        else:
            output[idx] = value[1] - prev
            prev = value[1]

    if plot:
        fig,ax = plt.subplots()
        ax.scatter(data[:, 0], output)
        plt.yticks([0, 1], ['Off', 'On'])
        plt.xlabel('Time')
        plt.ylabel('Status of device')
        plt.title(f'Status of device {label} at each minute')
        # plt.show()
        st.pyplot(fig)
    
    output = ['On' if i==1 else 'Off' for i in output]
    data = np.concatenate((data,np.atleast_2d(output).T),axis=1)
    
    if returnData:
        data = pd.DataFrame(data[:,1:],index=data[:,0],columns=['On_time','Off_time','Status'])
        return data # to know at which time device was off

st.write('<h1 style="color:blue">Dataset Visualization</h1>',unsafe_allow_html=True)
st.write('<h5 align="right">- By 20BCE073 Kunj Gandhi</h5>',unsafe_allow_html=True)
file = st.file_uploader('Upload Dataset',type='csv')
if file is not None:

    try:
        df = pd.read_csv(file)
    except:
        st.error('Invalid File Type')
        st.stop()

    st.success('File Uploaded Successfuly!')

    df['time'] = df['time'].apply(convertStr2Time)
    
    st.subheader("Some Useful Insights about data")
    st.write('**Columns :**',", ".join(df.columns))

    # st.dataframe(df,height=200,width=600)
    AgGrid(df.head(10),fit_columns_on_grid_load=True)

    st.write('RPM Range :',df.RPM.min(),'-',df.RPM.max())
    st.write(df['Device_id'].value_counts())


    st.info('Note \n1. Total_rotations is cumulative sum of RPM (Rotation per minute) for each device, 156 datapoints of each device is given, Data is taken every minute   \n2. On_time means no. of minutes the device was turned on  \n3. Off_time means no. of minutes the device was turned off')

    grouped_data = df.groupby('Device_id')

    fig,ax = plt.subplots()
    for device_id, group in grouped_data:
        ax.plot(group['time'], group['RPM'], label='Device {}'.format(device_id))
    plt.title('RPM Vs Time')
    plt.xlabel('Time')
    plt.ylabel('RPM')
    plt.legend()
    # plt.show()
    st.pyplot(fig)

    average_rpm = grouped_data.agg('mean')
    average_rpm = average_rpm['RPM']
    st.write('Average RPM',average_rpm)
    # Plot the average rpm for each device
    fig,ax = plt.subplots()
    ax.bar(average_rpm.index, average_rpm, color=['b', 'g', 'r'])
    plt.title('Average RPM for each device')
    plt.xlabel('Device')
    plt.ylabel('Average RPM')
    plt.xticks([1, 2, 3])
    plt.legend()
    # plt.show()
    st.pyplot(fig)

    device_1 = df.iloc[:156]
    device_2 = df.iloc[156:156*2]
    device_3 = df.iloc[156*2:156*3]

    efficiency(device_1,1)
    efficiency(device_2,2)
    efficiency(device_3,3)

    data1 = visualizeOnOff(device_1,returnData=True,label=1)
    data2 = visualizeOnOff(device_2,returnData=True,label=2)
    data3 = visualizeOnOff(device_3,returnData=True,label=3)

    st.header('Check Whether the Device was On or Off on paricular time')
    choice = st.selectbox('Select a Device',('Device 1','Device 2','Device 3'))
    st.write(data1.index[0].to_pydatetime())
    date_val = st.slider('Select Time',min_value=data1.index[0].to_pydatetime(),max_value=data1.index[-1].to_pydatetime(),format='DD/MM/YYYY - hh:mm',step=timedelta(minutes=1))

    if choice == 'Device 1':
        st.info(f'Status of Device 1 during Time {date_val} : {data1.loc[date_val]["Status"]}')
    elif choice == 'Device 2':
        st.info(f'Status of Device 2 during Time {date_val} : {data2.loc[date_val]["Status"]}')
    elif choice == 'Device 3':
        st.info(f'Status of Device 3 during Time {date_val} : {data3.loc[date_val]["Status"]}')