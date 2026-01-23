import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from model_pred import predict_car_price
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

(
    SYMBOLING, FUELTYPE, ASPIRATION, DOORNUMBER, CARBODY,
    DRIVEWHEEL, ENGINELOCATION, WHEELBASE, CARLENGTH, CARWIDTH,
    CARHEIGHT, CURBWEIGHT, ENGINETYPE, CYLINDERNUMBER, ENGINESIZE,
    FUELSYSTEM, BORERATIO, STROKE, COMPRESSIONRATIO, HORSEPOWER,
    PEAKRPM, CITYMPG, HIGHWAYMPG, BRAND
) = range(24)

FIELDS = [
    'symboling', 'fueltype', 'aspiration', 'doornumber', 'carbody',
    'drivewheel', 'enginelocation', 'wheelbase', 'carlength', 'carwidth',
    'carheight', 'curbweight', 'enginetype', 'cylindernumber', 'enginesize',
    'fuelsystem', 'boreratio', 'stroke', 'compressionratio', 'horsepower',
    'peakrpm', 'citympg', 'highwaympg', 'brand'
]

PROMPTS = {
    'symboling': "Введите symboling (числовая оценка риска, целое число, обычно от -2 до 3):",
    'fueltype': "Тип топлива (gas/diesel):",
    'aspiration': "Наддув (std/turbo):",
    'doornumber': "Число дверей (two/four):",
    'carbody': "Тип кузова (sedan, hatchback, wagon, convertible, suv):",
    'drivewheel': "Привод (fwd/rwd/4wd):",
    'enginelocation': "Расположение двигателя (front/rear):",
    'wheelbase': "Колёсная база (дюймы, например 99.8):",
    'carlength': "Длина (дюймы):",
    'carwidth': "Ширина (дюймы):",
    'carheight': "Высота (дюймы):",
    'curbweight': "Снаряжённая масса (фунты, например 2500):",
    'enginetype': "Тип двигателя (ohc, dohc, ohcv и т.д.):",
    'cylindernumber': "Число цилиндров (four, six, eight):",
    'enginesize': "Объём двигателя (см³, например 130):",
    'fuelsystem': "Система питания (mpfi, 2bbl и т.д.):",
    'boreratio': "Диаметр цилиндра (например 3.47):",
    'stroke': "Ход поршня (например 2.68):",
    'compressionratio': "Степень сжатия (например 9.0):",
    'horsepower': "Мощность (л.с., например 111):",
    'peakrpm': "Обороты макс. мощности (например 5000):",
    'citympg': "Расход в городе (миль/галлон):",
    'highwaympg': "Расход на трассе (миль/галлон):",
    'brand': "Марка (audi, bmw, toyota, honda и т.д.):"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! введи все характеристики последовательно и я предскажу цену автомобиля\n" + PROMPTS['symboling'])
    return SYMBOLING

async def receive_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    current_field = FIELDS[len(user_data)]
    
    user_data[current_field] = update.message.text.strip()
    
    if len(user_data) == 24:
        try:
            numeric_fields = [
                'symboling', 'wheelbase', 'carlength', 'carwidth', 'carheight',
                'curbweight', 'enginesize', 'boreratio', 'stroke', 'compressionratio',
                'horsepower', 'peakrpm', 'citympg', 'highwaympg'
            ]
            for f in numeric_fields:
                user_data[f] = float(user_data[f]) if '.' in user_data[f] else int(user_data[f])
            
            price = predict_car_price(dict(user_data))
            await update.message.reply_text(f"predicted price: ${price:,.2f}")
        except Exception as e:
            await update.message.reply_text(f"error: {str(e)}")
        finally:
            user_data.clear()
        return ConversationHandler.END
    
    next_field = FIELDS[len(user_data)]
    await update.message.reply_text(PROMPTS[next_field])
    return len(user_data)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("cancelled")
    return ConversationHandler.END

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            i: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_input)]
            for i in range(24)
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()