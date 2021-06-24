import investpy as ip
import telebot
import yahoo_fin.stock_info as si
from google_trans_new import google_translator
import pandas as pd
import numpy as np
import yfinance
import matplotlib.dates as mpl_dates
import datetime as dt
import pandas_datareader as pdr

f = open("key.txt", "r")
token = f.readline().strip()
message_id = f.readline().strip()
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['test'])
def test(message):
    print(message.chat.id)

@bot.message_handler(commands=['start'])
def start(message):
    first_name = message.from_user.first_name
    bot.reply_to(message, 'Selamat datang, ' + first_name + '. Jangan lupa subscribe t.me/jasondelio dan follow ig @jasondelio untuk mendapatkan informasi seputar saham, ya. Untuk cara menggunakan bot bisa menggunakan command /help')

@bot.message_handler(commands=['help'])
def help(message):
    if(str(message.chat.id) == message_id):
        bot.reply_to(message, "Cara menggunakan bot ini dengan memasukan command + kode saham\n\nContohnya /per bbri")
    else:
        bot.reply_to(message, "Access denied!")
    
@bot.message_handler(commands=['info'])
def info(message):
    if(str(message.chat.id) == message_id):
        try:
            kode_saham = message.text.split()
            data = ip.stocks.get_stock_company_profile(stock=kode_saham[1], country='Indonesia', language='english')
            pesan = data['desc']
            translator = google_translator()  
            translate_text = translator.translate(pesan, lang_src='en', lang_tgt='id')
            pesan = translate_text
        except:
            pesan = "Kode saham tidak dapat ditemukan"
        bot.reply_to(message, pesan)
    else:
        bot.reply_to(message, "Access denied!")
    
@bot.message_handler(commands=['per'])
def per(message):
    if(str(message.chat.id) == message_id):
        try:
            kode_saham = message.text.split()
            data = ip.stocks.get_stock_information(kode_saham[1], "Indonesia", as_json=True)
            pesan = data['P/E Ratio']
        except:
            pesan = "Kode saham tidak dapat ditemukan"
        bot.reply_to(message, pesan)
    else:
        bot.reply_to(message, "Access denied!")

@bot.message_handler(commands=['pbv'])
def pbv(message):
    if(str(message.chat.id) == message_id):
        try:
            kode_saham = message.text.split()
            name = kode_saham[1] + '.JK'
            current_price = si.get_live_price(name)
            data = si.get_stats(name)
            bvs = float(data.loc[47].values[1])
            if(bvs < 2):
                bvs = bvs * 14000
            pbv = round(current_price / bvs, 2)
            pesan = pbv
        except:
            pesan = "Kode saham tidak dapat ditemukan"
        bot.reply_to(message, pesan)
    else:
        bot.reply_to(message, "Access denied!")

@bot.message_handler(commands=['beta'])
def beta(message):
    if(str(message.chat.id) == message_id):
        try:
            kode_saham = message.text.split()
            data = ip.stocks.get_stock_information(kode_saham[1], "Indonesia", as_json=True)
            pesan = data['Beta']
        except:
            pesan = "Kode saham tidak dapat ditemukan"
        bot.reply_to(message, pesan)
    else:
        bot.reply_to(message, "Access denied!")

@bot.message_handler(commands=['dividend'])
def dividend(message):
    if(str(message.chat.id) == message_id):
        try:
            kode_saham = message.text.split()
            data = ip.stocks.get_stock_information(kode_saham[1], "Indonesia", as_json=True)
            pesan = data['Dividend (Yield)']
        except:
            pesan = "Kode saham tidak dapat ditemukan"
        bot.reply_to(message, pesan)
    else:
        bot.reply_to(message, "Access denied!")

@bot.message_handler(commands=['snr'])
def snr(message):
    if(str(message.chat.id) == message_id):
        def isSupport(df,i):
              support = df['Low'][i] < df['Low'][i-1]  and df['Low'][i] < df['Low'][i+1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]
              return support
        def isResistance(df,i):
              resistance = df['High'][i] > df['High'][i-1]  and df['High'][i] > df['High'][i+1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]
              return resistance
        def isFarFromLevel(l):
            s =  np.mean(df['High'] - df['Low'])
            return np.sum([abs(l-x) < s  for x in levels]) == 0
        try:
            today = dt.datetime.today().strftime('%Y-%m-%d')
            kode_saham = message.text.split()
            name = kode_saham[1] + '.JK'
            ticker = yfinance.Ticker(name)
            df = ticker.history(interval="1d",start="2020-01-01", end=today)
            df['Date'] = pd.to_datetime(df.index)
            df['Date'] = df['Date'].apply(mpl_dates.date2num)
            df = df.loc[:,['Date', 'Open', 'High', 'Low', 'Close']]
            levels = []
            sl = []
            rl = []
            for i in range(2,df.shape[0]-2):
              if isSupport(df,i):
                l = df['Low'][i]
                if isFarFromLevel(l):
                  levels.append((i,l))
              elif isResistance(df,i):
                l = df['High'][i]
                if isFarFromLevel(l):
                  levels.append((i,l))
            current_price = si.get_live_price(name)
            for a,b in levels:
                if b > current_price:
                    rl.append(b)
                else:
                    sl.append(b)
            if(rl == []):
                res_result = int(df['High'][-14:].max())
            else:
                res_result = int(min(rl))     

            if(sl == []):
                sup_result = int(df['Low'][-14:].min())
            else:
                sup_result = int(max(sl))

            pesan = "Support = " + str(sup_result) + "\nResist = " + str(res_result)
        except:
            pesan = "Kode saham tidak dapat ditemukan"
        bot.reply_to(message, pesan)
    else:
        bot.reply_to(message, "Access denied!")

@bot.message_handler(commands=['sma'])
def sma(message):
    if(str(message.chat.id) == message_id):
        try:
            kode_saham = message.text.split()
            current_price = si.get_live_price(kode_saham[1] + ".JK")
            data = si.get_data(kode_saham[1] + ".JK", interval='1d')
            sma5 = "SMA5 = " + str(int(data['close'][-5:].mean()))
            sma10 = "SMA10 = " + str(int(data['close'][-10:].mean()))
            sma20 = "SMA20 = " + str(int(data['close'][-20:].mean()))
            sma50 = "SMA50 = " +  str(int(data['close'][-50:].mean()))
            sma100 = "SMA100 = " +  str(int(data['close'][-100:].mean()))
            sma200 = "SMA200 = " +  str(int(data['close'][-200:].mean()))
            summary = ["    *NEUTRAL*"] * 6
            
            if(float(data['close'][-5:].mean()) < current_price):
                summary[0] = "  *BUY*"
            elif(float(data['close'][-5:].mean()) > current_price):
                summary[0] = "  *SELL*"
    
            if(float(data['close'][-10:].mean()) < current_price):
                summary[1] = "  *BUY*"
            elif(float(data['close'][-10:].mean()) > current_price):
                summary[1] = "  *SELL*"
                
            if(float(data['close'][-20:].mean()) < current_price):
                summary[2] = "  *BUY*"
            elif(float(data['close'][-20:].mean()) > current_price):
                summary[2] = "  *SELL*"

            if(float(data['close'][-50:].mean()) < current_price):
                summary[3] = "  *BUY*"
            elif(float(data['close'][-50:].mean()) > current_price):
                summary[3] = "  *SELL*"
                
            if(float(data['close'][-100:].mean()) < current_price):
                summary[4] = "  *BUY*"
            elif(float(data['close'][-100:].mean()) > current_price):
                summary[4] = "  *SELL*"

            if(float(data['close'][-200:].mean()) < current_price):
                summary[5] = "  *BUY*"
            elif(float(data['close'][-200:].mean()) > current_price):
                summary[5] = "  *SELL*"
                
            pesan = sma5 + summary[0] + "\n" + sma10 + summary[1] + "\n" + sma20 + summary[2] + "\n" + sma50 + summary[3] + "\n" + sma100 + summary[4] + "\n" + sma200 + summary[5] 

        except:
            pesan = "Kode saham tidak dapat ditemukan"
        bot.reply_to(message, pesan, parse_mode = "Markdown")
    else:
        bot.reply_to(message, "Access denied!")

@bot.message_handler(commands=['stoch'])
def stoch(message):
    if(str(message.chat.id) == message_id):
        try:
            kode_saham = message.text.split()
            name = kode_saham[1] + '.JK'
            ticker = pdr.get_data_yahoo(name, dt.datetime(2021, 1, 1), dt.datetime.now())
            ticker['14-high'] = ticker['High'].rolling(14).max()
            ticker['14-low'] = ticker['Low'].rolling(14).min()
            ticker['%Kfast'] = (ticker['Close'] - ticker['14-low'])*100/(ticker['14-high'] - ticker['14-low'])
            ticker['%Kslow'] = ticker['%Kfast'].rolling(3).mean()
            ticker['%Dslow'] = ticker['%Kslow'].rolling(3).mean()
            kslow = ticker['%Kslow'].iloc[-1]
            if(kslow > 80):
                result = "area overbought"
            elif(kslow < 20):
                result = "area oversold"
            elif(30 >= kslow >= 20):
                result = "dekat area oversold"
            elif(70 <= kslow <= 80):
                result = "dekat area overbought"
            else:
                result = "netral"
            pesan = "Stochastic(14,3,3) = " + result
        except:
            pesan = "Kode saham tidak dapat ditemukan"
        bot.reply_to(message, pesan)
    else:
        bot.reply_to(message, "Access denied!")

@bot.message_handler(commands=['fair'])
def fair(message):
    if(str(message.chat.id) == message_id):
        try:
            kode_saham = message.text.split()
            name = kode_saham[1] + '.JK'
            data = si.get_balance_sheet(name)
            data2 = si.get_income_statement(name)
            data3 = si.get_stats(name)
            bvs = float(data3.loc[47].values[1])
            if(bvs < 2):
                bvs = bvs * 14000
            result = data2.loc["netIncome"].mean() / data.loc["totalStockholderEquity"].mean() 
            result2 = 1
            if(result*100 > 10):
                a = int(result * 100) - 10
                for x in range (a):
                    result2 = (result2/10) + result2
            else:
                if(result*100 < 10): 
                    result2 = int(result * 100) / 10
                else:
                    result2 = 1
            pesan = "Nilai intrinsik berdasarkan ROE rata-rata tahunan = " + str(int(bvs * result2))
            if(bvs < 0 or result < 0):
                pesan = "Saham ini memiliki ROE rata- rata negative"
        except:
            pesan = "Kode saham tidak dapat ditemukan"
        bot.reply_to(message, pesan)
    else:
        bot.reply_to(message, "Access denied!")
f.close()     
bot.polling()

