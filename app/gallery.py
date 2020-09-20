import streamlit as st
from PIL import Image

def display_gallery():

	st.title('Gallery')

	st.markdown("Here are some of the results i have generated of My favourite Characters..")

	im1 = Image.open('asset/images/1.png')

	st.image(im1,width=None)

	im2 = Image.open('asset/images/2.png')

	st.image(im2,width=None)

	im3 = Image.open('asset/images/3.png')

	st.image(im3,width=None)

	im4 = Image.open('asset/images/4.png')

	st.image(im4,width=None)

	im5 = Image.open('asset/images/5.png')

	st.image(im5,width=None)

	im6 = Image.open('asset/images/6.png')

	st.image(im6,width=None)

	im7 = Image.open('asset/images/7.png')

	st.image(im7,width=None)

	im8 = Image.open('asset/images/8.png')

	st.image(im8,width=None)

	im9 = Image.open('asset/images/9.png')

	st.image(im9,width=None)

	im10 = Image.open('asset/images/10.png')

	st.image(im10,width=None)
