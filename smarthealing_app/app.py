from st_on_hover_tabs import on_hover_tabs
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import requests
import time as t
from bs4 import BeautifulSoup as bs
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
import plotly.figure_factory as ff
import streamlit.components.v1 as components
from PIL import Image

base = 'https://en.wikipedia.org/'
icd9_wiki = 'https://en.wikipedia.org/wiki/List_of_ICD-9_codes'
r = requests.get(icd9_wiki)
links = bs(r.content, 'html.parser').find('div', class_ = 'mw-parser-output')

# Scraping de diseases
def code_name(code):
    if code[0] in ['E', 'V', 'M']:
        return 'Sorry, no description.'
    elif code[0].isnumeric() == False:
        return 'Code does not exist.'
    else:
        # Get category to access specific link.
        i = None
        block_ends = [140,240,280,290,320,390,460,520,580,630,680,710,740,760,780,800,1000]
        blocks = [[i+1, s] for i, s in enumerate(block_ends)]
        for block in blocks:
            if float(code) < block[1]:
                i = block[0]
                break
        # Get url of icd9 specific page.
        try:
            link = links.ul.find_all('a')[i-1].get('href')
        except:
            return 'Code does not exist.'
        # Search for name of code.
        url = base + link
        r2 = requests.get(url)
        d = bs(r2.content, 'html.parser').find('div', class_ = 'mw-parser-output')
        found = False
        for a in d.find_all('a'):
            if found:
                return a.text
            if a.text == code:
                found = True
    
# ===============================================================================================================
# Page config            
st.set_page_config(
    page_title="Smart Healing",
    page_icon='⚕️',
    layout="wide",
    initial_sidebar_state="auto",
)

if "params" not in st.session_state:
    st.session_state['params'] = dict()

st.markdown('<style>' + open('style.css').read() + '</style>', unsafe_allow_html=True)

with st.sidebar:
        tabs = on_hover_tabs(tabName=['Dashboard', 'Input Tab', 'Results'], 
                             iconName=['dashboard', 'money', 'economy'],
                             key="0")

# ===============================================================================================================
# Tab Dashboard
if tabs =='Dashboard':
    st.title("Dashboard")
    st.write('Name of option is {}'.format(tabs))
    
    image = Image.open('smarthealing_app/Pngsmarthealing.png')
    st.image(image, caption=None, width=250, use_column_width=False, clamp=True, channels="RGB", output_format="auto")
    #displaying the image on streamlit app
    
    url_lottie = 'https://assets1.lottiefiles.com/private_files/lf30_y9czxcb9.json'
    def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    

    lottie_json = load_lottieurl(url_lottie)
    st_lottie(lottie_json)
    st_lottie_spinner(lottie_json)

# ================================================================================================================
# Tab where we input the data
elif tabs == 'Input Tab':
    image = Image.open('smarthealing_app/Pngsmarthealing.png')
    c1, a2, a3 = st.columns(3)
    with a3:
        st.image(image, caption=None, use_column_width=True, clamp=True, channels="RGB", output_format="auto")
        #displaying the image on streamlit app
        
    st.title("Here we are gonna input the data to get the prediction")
    st.write('Name of tab is {}'.format(tabs))
    # with st.form(key='columns_in_form'):
    # 1st Line
    c1, c2, c3 = st.columns(3)
    with c1:
        # Number of leaves per company 
        bajas_empresa = st.number_input('Input number of leaves in company:',min_value=0, max_value=5000000)
        st.write('You selected: ', bajas_empresa)
    
    with c2:
        # Number of leaves per worker
        bajas_worker = st.number_input('Input number of leaves of worker:',min_value=0, max_value=5000000)
        st.write('You selected: ', bajas_worker)
    with c3:
        # CNAE category
        cnae_df = pd.read_csv('./smarthealing_app/data/cnae_list.csv', sep = '.-', dtype='string') 
        cnae_select = st.selectbox('Input CNAE Category:', (cnae_df['Code'] + ' - ' + cnae_df['Description']).tolist())
        cnae = cnae_select[:4]
        st.write('You selected: ', cnae)
    
    # 2nd Line
    c1, c2 = st.columns(2)   
    with c1:
        # Day of the week 
        options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_week = st.select_slider('Select day of the week on leave: ',
            options=options)
        week_day = options.index(day_week) + 1
        st.write('You select: ', week_day)     
    with c2:
        # ICD9 category
        valid_characters = ['M','V','E','m','b','e','1','2','3','4','5','6','7','8','9','0','.']
        idc9_select = st.text_input('Input the ICD9 code: ', value=303.2)
        matched_list = [characters in valid_characters for characters in idc9_select]
        if all(matched_list): 
            icd9 = f"{idc9_select} - {code_name(idc9_select)}"
            st.write('You selected: ', icd9)
        else:
            st.warning('Please input a valid string..', icon="⚠️")
    
    # 3rd Line
    c1, c2, c3 = st.columns(3)
    with c1:
        # Relapse, setback
        setback_select = st.selectbox('Is this a setback / relapse :', ('Yes', 'No'))
        if setback_select == 'Yes':
            setback = 1
        else:
            setback = 0
    
    with c2:
        # Number of workers 
        num_workers = st.number_input('Input number of workers in company: ',min_value=0, max_value=5000000)
        
    with c3:
        # Codigo Postal
        postal_df = pd.read_csv('./smarthealing_app/data/postal_list.csv', sep = ',', dtype='string') 
        
        postal = st.selectbox('Input Postal Code', (postal_df['codigopostalid'] + ' - ' + postal_df['provincia'] + ' - ' + postal_df['poblacion']).tolist())
        # Selecting just description from DF, idk why it wasn't working the simple way
        postal = postal.split(' ')[0]
        st.write('You selected: ',postal)
       
    c1, c2 = st.columns(2)
    with c1: 
        # Day counter
        day_counter = st.number_input('Input number of days on leave: ',min_value=0, max_value=5000000)
    
    with c2:
        # Multiple jobs
        multi_job_select = st.radio("Does the worker has multiple jobs", ('Yes', 'No'))
        if multi_job_select == 'Yes':
            multi_job = 1
        else:
            multi_job = 0
        st.write('You selected: ', multi_job)
    
    st.markdown("""---""")
    c1, c2 = st.columns(2)
    # Type of contract
    with c1:
        contract_df = pd.read_csv('./smarthealing_app/data/contract_list.csv', sep = ',', dtype='string') 
        contract = st.selectbox('Input Contract Type:', (contract_df['clave'] + ' - ' + contract_df['denominacion']).tolist())
        # Selecting just description from DF, idk why it wasn't working the simple way
        contract = contract[:3]
        st.write('You selected: ',contract)
    
    with c2:
        # Cotization group 
        coti_df = pd.read_csv('./smarthealing_app/data/coti_list.csv', sep = ':', dtype='string') 
        contribution = st.selectbox('Select contribution group:',
            options=(coti_df['description'].to_list()))
        # Selecting just description from DF, idk why it wasn't working the simple way
        selection_coti = coti_df[coti_df['description']==contribution]['category'].iloc[0]
        st.write('You selected: ', selection_coti)
    
    # 2nd Line
    c1, c2 = st.columns(2)
    # Years in the company
    with c1:
        d0 = st.date_input(
        "Working in the company since: ", date(2021, 7, 6), min_value=date(1920, 7, 6))
        d1 = date.today()
        d3 = d1 - d0
        result_year = round((d3.days/365),3)
        st.write('Years working:', result_year)
    
    with c2:
        # How old is the worker
        a0 = st.date_input(
        "When was the worker born: ", date(2010, 7, 6), min_value=date(1910, 7, 6))
        a1 = date.today()
        a3 = a1 - a0
        age = round((a3.days/365),3)
        st.write('Years working:', age)
    
    c1, c2 = st.columns(2)
    # Month 
    with c1:
        options=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        month_select = st.select_slider('Select month of the year on leave: ',
            options=options)
        month = options.index(month_select) + 1
        st.write('You select: ', month)
        
    # Week
    with c2:
        week = st.number_input('Select number week of the year on leave: ', min_value=0, max_value=5000000)
        st.write('You select: ', week)
        
    if st.button(label = 'Calculate'):
        my_bar = st.progress(0)
        for percent_complete in range(100):
            t.sleep(0.008)
            my_bar.progress(percent_complete + 1)
        st.write('Data saved! 💾')
        
        params = {"ContadorBajasCCC": int(bajas_empresa),
                "ContadorBajasDNI": int(bajas_worker),
                "sexo": int(1),
                "cnae": int(cnae),
                "icd9": str(idc9_select),
                "recaida": int(setback),
                "numtreb": int(num_workers),
                "codipostal": int(postal),
                "ContadordiasBajasDNI": int(day_counter),
                "contracte": int(contract),
                "grupcoti": int(selection_coti),
                "pluriempleo": int(multi_job),
                "diasemana": int(week_day),
                "tiempo_en_empresa": float(result_year),
                "edad": float(age),
                "mes_baja": int(month),
                "epiweek": int(week)
            }
        st.session_state["params"] = params.copy()
        # st.write(params)
        
        # API CALL
        url = "https://smarthealing-w5jxjldzkq-ew.a.run.app/predict"

        with st.spinner('Fetching your prediction...'):
            prediction = requests.get(url,params)
            duracion_baja = prediction.json().get('leave_duration')
            st.title(f" Predicted duration: {int(round(duracion_baja,0))} days")
        st.success('Done!')
    
# ================================================================================================================
elif tabs == 'Results':
    st.title("Results")
    if len(st.session_state["params"]) > 0:
        st.write(st.session_state["params"])
    st.write('Name of option is {}'.format(tabs))
    
    
# ================================================================
    postal_df = pd.read_csv('./smarthealing_app/data/postal_list.csv', sep = ',', dtype='string') 
    
    df = pd.DataFrame(
        np.random.randn(250, 2) / [2, 1] + [40.416775,-3.703790],
        columns=['lat', 'lon'])
    
    def lat(X):
        return f"{X.lat.split(',')[0]}.{''.join(X.lat.split(',')[1:])}"

    def lon(X):
        return f"{X.lon.split(',')[0]}.{''.join(X.lon.split(',')[1:])}"

    df['Postal Code'] = postal_df['codigopostalid']
    df['lat'] = postal_df.apply(lat, axis=1)
    df['lon'] = postal_df.apply(lon, axis=1)
    
    st.map(df)
# ================================================================
    import pydeck as pdk

    chart_data = pd.DataFrame(
    np.random.randn(100, 2) / [2, 1] + [40.416775,-3.703790],
    columns=['lat', 'lon'])

    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=40.416775,
            longitude=-3.703790,
            zoom=5,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
            'HexagonLayer',
            data=chart_data,
            get_position='[lon, lat]',
            radius=20000,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=chart_data,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=200,
            ),
        ],
    ))
