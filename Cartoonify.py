import streamlit as st
from PIL import Image
from datetime import datetime
import time
import random 
import pandas as pd
import numpy as np
import cv2
from cv2 import cvtColor, COLOR_BGR2RGB
import tensorflow as tf
import os
import tqdm
import io
import base64
import psycopg2
#st.set_option('deprecation.showfileUploaderEncoding', False)

from app.gallery import display_gallery
from app.stats import display_stats
from app import guided_filter
from app import network

status = False

fail_list = [
"I'm Not Crazy. My Developer Had Me Tested.",
"Well, That’s No Reason To Cry. One Cries Because One Is Sad.",
"Hey, you do your little experiments, I do mine.",
"Oh gravity, that heartless bitch.",
"Okay, you need to say these things in your head before you say them out loud.",
"Thank you for understanding.",
"Oh, great, this again.",
"Dude, you're embarrassing me in front of wizards.",
"It's an imperfect world, but it's the only one we got.",
"I'll be back.",
"Houston, we have a problem.",
"Houston, I have a bad feeling about this mission.",
"The greatest teacher, failure is.",
"Toto, i've a feeling we're not in Kansas anymore.",
"Frankly, my dear, I don't give a damn.",
"Why so serious ?",
"Nobody's perfect.",
"That is my least vulnerable spot.",
"Don't point that gun at him. He's an unpaid intern."
]

success_list = [
"Bazinga!",
"It’s a Satunalia miracle.",
"Yeah, I’m a freaking genius.",
"If I could speak the language of rabbits, they would be amazed, and I would be their king.",
"Sheldon Cooper does not get lucky.",
"Sometimes you gotta run before you walk.",
"Don't do anything I would do, and definitely don't do anything i wouldn't do.. ",
"Grab me a napkin homey, you just got served.",
"Show me the money..",
"To Infinity and Beyond",
"I am a golden god.",
"May the force be with you.",
"Hasta la vista baby.",
"Elementary, my dear Watson"
]

hash_funcs={'_thread.RLock' : lambda _: None, 
                '_thread.lock' : lambda _: None, 
                'builtins.PyCapsule': lambda _: None, 
                '_io.TextIOWrapper' : lambda _: None, 
                'builtins.weakref': lambda _: None,
                'builtins.dict' : lambda _:None}

@st.cache(suppress_st_warning=True,hash_funcs=hash_funcs)
def resize_crop(image):
  try:
    h, w, c = np.shape(image)
    if min(h, w) > 720:
        if h > w:
            h, w = int(720*h/w), 720
        else:
            h, w = 720, int(720*w/h)
    image = cv2.resize(image, (w, h),
                        interpolation=cv2.INTER_AREA)
    h, w = (h//8)*8, (w//8)*8
    image = image[:h, :w, :]
    return image
  except:
    return "ERROR"

def load_model():

  ss = time.time()
  model_path = 'saved_models'

  input_photo = tf.placeholder(tf.float32, [1, None, None, 3])
  network_out = network.unet_generator(input_photo)
  final_out = guided_filter.guided_filter(input_photo, network_out, r=1, eps=5e-3)

  all_vars = tf.trainable_variables()
  gene_vars = [var for var in all_vars if 'generator' in var.name]
  saver = tf.train.Saver(var_list=gene_vars)

  print("loading model...............")
  config = tf.ConfigProto()
  config.gpu_options.allow_growth = True
  sess = tf.Session(config=config)

  sess.run(tf.global_variables_initializer())
  saver.restore(sess, tf.train.latest_checkpoint(model_path))
  print("model loaded.................")
  print("model loading time ",str(time.time()-ss))

  return sess, input_photo, final_out 

def cartoonize(image):
  try:
    batch_image = image.astype(np.float32)/127.5 - 1
    batch_image = np.expand_dims(batch_image, axis=0)

    sess, input_photo, final_out = load_model()

    output = sess.run(final_out, feed_dict={input_photo: batch_image})
    output = (np.squeeze(output)+1)*127.5
    output = np.clip(output, 0, 255).astype(np.uint8)
    return output
  except:
    st.markdown("error from cartoonize...")
    return "ERROR"
         
@st.cache(suppress_st_warning=True,hash_funcs=hash_funcs)
def get_image_download_link(img):
  buffered = io.BytesIO()
  img = Image.fromarray(np.uint8(img)).convert('RGB')
  img.save(buffered, format="JPEG")
  img_str = base64.b64encode(buffered.getvalue()).decode()
  href = f'<a href="data:file/jpg;base64,{img_str}" download="cartoon.jpg">Download this image</a>'
  return href

@st.cache(suppress_st_warning=True,hash_funcs=hash_funcs)
def load_image(image):
  try:
    global status
    status = True
    image = Image.open(image)#.convert('RGB')
    open_cv_image = np.asarray(image)
    return open_cv_image
  except:
    return "ERROR"

def db_connection():
  DATABASE_URL = # enter url reveived from heroku postgres
  conn = psycopg2.connect(DATABASE_URL, sslmode='require')
  cur = conn.cursor()
  return cur,conn

def cartoon_main(uploaded_file):         

  if uploaded_file is not None:

    try:
	
      image = load_image(uploaded_file)
      if image != "ERROR":
        start = time.time()
        image = resize_crop(image)
        with st.spinner('Hang on, cartoonizing your image....'):

          result = cartoonize(image)
          if result != "ERROR":
            end = time.time()
            st.image(result, use_column_width=True)
            st.markdown(get_image_download_link(result), unsafe_allow_html=True)  
          else:
            global status
            status = False

        shapes = image.shape
        inptype = "Image"
        messages = random.choice(success_list)

      else:
        start = time.time() 	 								
        inptype = "Not_Image"
        shapes = "None"
        messages = random.choice(fail_list)
        end = time.time()
        st.markdown("Invalid Input : Please upload image only")
                  
      if status == True:
        timestamp_str = datetime.now()
        duration = end-start

        cur,conn = db_connection() 
        cur.execute("INSERT INTO LOG (timestampStr,inp_type,shape,inference_time,message) VALUES (%s,%s,%s,%s,%s)",(timestamp_str,inptype, shapes,duration,messages))
        conn.commit()
        conn.close()
        
        status = False
      else:
        pass

    except:
      st.markdown("ERROR : Something went wrong ")


page = st.sidebar.selectbox("Select a page", ["Cartoonify", "Gallery", "Credits","For NERd","About Me"])

if page == "Cartoonify":
  
  st.title('Image Cartoonify')

  uploaded_file = None

  uploaded_file = st.file_uploader("Choose your image...")

  cartoon_main(uploaded_file)

  agree = st.checkbox("Watch this video to get most out of this application")
  
  if agree:

    st.video('https://youtu.be/k2FQ0KN2J-Q') 
           

elif page == "Credits":

  st.title('Credits')

  st.markdown(" This application is based on the paper published in <b>CVPR 2020</b> titled <b>'Learning to Cartoonize Using White-box Cartoon Representations'</b>",unsafe_allow_html=True)
  st.markdown("Link to paper : [paper](https://github.com/SystemErrorWang/White-box-Cartoonization/blob/master/paper/06791.pdf)")

elif page == "About Me":
  st.title('About Me')
  st.markdown("Hi There,")
  st.markdown("My name is Kaushal Chapaneri, i have been working in field of Machine Learning for almost 2 years now. I Learn new things by trying it out.")
  st.markdown("We can connect over LinkedIn at : https://in.linkedin.com/in/kaushal-chapaneri-34a0b4107")
  st.markdown("You can reach out to me at : [kaushalchapaneri@gmail.com] ()")
  st.markdown("<a href='http://www.nerdtests.com/ft_nq.php'>![Alt Text](http://www.nerdtests.com/images/ft/nq/b1ccbdb62e.gif)</a>",unsafe_allow_html=True)

if page == "Gallery":

  display_gallery()    

elif page == "For NERd":

  cur,conn = db_connection()
  cur.execute("SELECT * from LOG");
  rows = cur.fetchall()
  conn.commit()
  conn.close()
  df = pd.DataFrame(rows, columns =['timestampStr','inp_type','shape','inference_time','message'])
  display_stats(df)
 
else:
	pass