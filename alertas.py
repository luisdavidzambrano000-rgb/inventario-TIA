import sqlite3
import telebot
from datetime import datetime

TOKEN = "8851216912:AAGsnkw07vpVkHks6p_EbGfI14xZu90OsMo"
CHAT_ID = "5062650494"

bot = telebot.TeleBot(TOKEN)

conexion = sqlite3.connect("inventario.db")
cursor = conexion.cursor()

cursor.execute("SELECT * FROM productos")
productos = cursor.fetchall()

hoy = datetime.now().date()

for producto in productos:

    nombre = producto[2]
    marca = producto[3]
    cantidad = producto[4]
    caducidad = producto[5]

    fecha_caducidad = datetime.strptime(
        caducidad,
        "%Y-%m-%d"
    ).date()

    dias_restantes = (fecha_caducidad - hoy).days

    if dias_restantes <= 3:

        mensaje = f"""
🚨 ALERTA DE CADUCIDAD

Producto: {nombre}
Marca: {marca}
Cantidad: {cantidad}

⚠️ Vence en {dias_restantes} días
"""

        bot.send_message(CHAT_ID, mensaje)

conexion.close()