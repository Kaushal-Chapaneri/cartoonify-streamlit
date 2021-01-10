import streamlit as st
import pandas as pd
#st.set_option('deprecation.showPyplotGlobalUse', False)

def display_stats(df):	

	st.title('Stats for NERd')
	st.write("") 
	df['shape'] = df['shape'].str.strip()
	df['message'] = df['message'].str.strip()
 
	st.markdown('<h4>Recent requests</h4>',unsafe_allow_html=True)
	fmt = "%d-%m-%Y %H:%M:%S"
	styler = df.tail(10).style.format(
    {
        "timestampStr": lambda t: t.strftime(fmt)
    }
)
	st.table(styler)
	st.markdown('<h3>Minimum Inference time observed so far (in seconds) : '+str(df[df['inp_type'] == "Image"]['inference_time'].min())[:5]+'</h3>',unsafe_allow_html=True)
	st.markdown('<h3>Maximum Inference time observed so far (in seconds) : '+str(df[df['inp_type'] == "Image"]['inference_time'].max())[:5]+'</h3>',unsafe_allow_html=True)
	st.markdown('<h3>Average Inference time observed so far (in seconds) : '+str(sum(df['inference_time'])/len(df))[:5]+'</h3>',unsafe_allow_html=True)
 
	df.inp_type.str.get_dummies().sum().plot.pie(label='Requests', autopct='%1.0f%%')

	st.pyplot()
	st.write("") 
	st.write("") 

	df2 = df.copy()
	df2['dates'] = df['timestampStr'].apply(lambda x : x.strftime('%D')[:-3])
	d = df2.groupby(['dates','inp_type'])['inp_type'].size().unstack()
	unique_dates = df2['dates'].unique().tolist()
	d = d.reindex(unique_dates)
	d = d[-9:]
	d.plot(kind='bar',stacked=True,title='Request type by Day')
	st.pyplot()
	
	st.write("") 
	st.write("") 
	st.title('How it works?')
	st.write("")
	st.video('https://youtu.be/JKR4kX4P8Cw')
	
	st.write("") 
	st.write("") 
	st.markdown("Link to Source code : [github](https://github.com/Kaushal-Chapaneri/cartoonify-streamlit)")

 